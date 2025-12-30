"""FastAPI server for the customer support agent."""

import os
import sys
import warnings
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Suppress websockets deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn.protocols.websockets")

# Initialize logger early
from src.utils.logger import get_logger
logger = get_logger(__name__)

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agent.database.setup import init_database
from src.agent.graph import get_agent


# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("Starting FastAPI application")
    try:
        logger.debug("Initializing database...")
        init_database(seed_data=True)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application")


# Initialize FastAPI app
app = FastAPI(
    title="Customer Support Agent API",
    description="AI-powered customer support agent with LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str
    thread_id: Optional[str] = "default"
    customer_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    thread_id: str
    tool_calls: Optional[List[dict]] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None


class GenerateRequest(BaseModel):
    """Request model for generate endpoint."""

    message: str
    thread_id: Optional[str] = None
    customer_id: Optional[int] = None


class GenerateResponse(BaseModel):
    """Response model for generate endpoint."""

    response: str
    thread_id: str


# Initialize agent (lazy loading)
_agent = None


def get_agent_instance():
    """Get or create agent instance."""
    global _agent
    if _agent is None:
        try:
            logger.debug("Initializing agent instance")
            _agent = get_agent()
            logger.info("Agent instance created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")
    return _agent


def reset_agent():
    """Reset agent instance (for testing/debugging)."""
    global _agent
    _agent = None


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint accessed")
    return {
        "message": "Customer Support Agent API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - Chat with the agent (maintains conversation state)",
            "/generate": "POST - Generate a single response (no state)",
            "/health": "GET - Health check",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy", "service": "customer-support-agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that maintains conversation state.
    
    The agent remembers previous messages in the conversation thread,
    allowing for multi-turn conversations.
    """
    thread_id = request.thread_id or "default"
    logger.info(f"Chat request received - thread_id: {thread_id}, message length: {len(request.message)}")
    logger.debug(f"Chat message: {request.message[:200]}")
    
    try:
        agent = get_agent_instance()
        
        # Create human message
        human_message = HumanMessage(content=request.message)
        
        # Prepare input state
        input_state = {"messages": [human_message]}
        
        # Configure thread ID for state management
        config = {"configurable": {"thread_id": thread_id}}
        
        # Stream the agent response
        logger.debug(f"Streaming agent response for thread: {thread_id}")
        final_state = None
        event_count = 0
        for event in agent.stream(input_state, config):
            final_state = event
            event_count += 1
            logger.debug(f"Agent event {event_count}: {list(event.keys())}")

        logger.debug(f"Agent completed with {event_count} events")
        
        # Extract response and metadata
        response_text = ""
        tool_calls_list = []
        intent = None
        confidence = None
        
        if final_state:
            # Look for response in synthesize node first
            if "synthesize" in final_state:
                messages = final_state["synthesize"].get("messages", [])
                    for msg in reversed(messages):
                        if hasattr(msg, "content") and msg.content:
                            if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                response_text = msg.content
                                break
                
                # Extract metadata from synthesize node
                if "tool_calls" in final_state["synthesize"]:
                    tool_calls_list = final_state["synthesize"].get("tool_calls", [])
                if "confidence" in final_state["synthesize"]:
                    confidence = final_state["synthesize"].get("confidence")
            
            # Extract intent from understand_intent node
            if "understand_intent" in final_state:
                intent = final_state["understand_intent"].get("intent")
            
            # Fallback: check all nodes
            if not response_text:
                for node_name, node_output in final_state.items():
                    if node_name in ["start", "understand_intent"]:
                        continue  # Skip these nodes
                    messages = node_output.get("messages", [])
                    if messages:
                        for msg in reversed(messages):
                            if hasattr(msg, "content") and msg.content:
                                if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                    # Skip generic greetings
                                    if msg.content not in ["How can I assist you today?", "Hello! How can I help you?"]:
                                        response_text = msg.content
                                        break
                        if response_text:
                            break
        
        if not response_text:
            logger.warning(f"No response text extracted for thread: {thread_id}")
            response_text = "I apologize, but I couldn't generate a response. Please try again."
        else:
            logger.info(f"Response generated - length: {len(response_text)}, tool_calls: {len(tool_calls_list) if tool_calls_list else 0}")
        
        return ChatResponse(
            response=response_text,
            thread_id=thread_id,
            tool_calls=tool_calls_list if tool_calls_list else None,
            intent=intent,
            confidence=confidence,
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate endpoint for single responses without maintaining state.
    
    Each request is treated as a new conversation.
    """
    import uuid
    
    thread_id = request.thread_id or str(uuid.uuid4())
    logger.info(f"Generate request received - thread_id: {thread_id}, message length: {len(request.message)}")
    logger.debug(f"Generate message: {request.message[:200]}")
    
    try:
        agent = get_agent_instance()
        
        # Create human message
        human_message = HumanMessage(content=request.message)
        
        # Prepare input state
        input_state = {"messages": [human_message]}
        
        # Use a unique thread ID for each request (no state persistence)
        config = {"configurable": {"thread_id": thread_id}}
        
        # Stream the agent response and collect all states
        logger.debug(f"Streaming agent response for thread: {thread_id}")
        all_states = []
        event_count = 0
        for event in agent.stream(input_state, config):
            all_states.append(event)
            event_count += 1
            logger.debug(f"Agent event {event_count}: {list(event.keys())}")
        
        logger.debug(f"Agent completed with {event_count} events, {len(all_states)} states collected")

        # Extract response - check all states in reverse order
        response_text = ""
        from langchain_core.messages import AIMessage, ToolMessage
        
        # Check if tools were called by looking for ToolMessage in any state
        tools_called = False
        for state in all_states:
            if "tools" in state:
                tool_messages = state["tools"].get("messages", [])
                if any(isinstance(msg, ToolMessage) for msg in tool_messages):
                    tools_called = True
                    break
        
        # Priority 1: If tools were called, use synthesize node from final state
        if tools_called and all_states:
            final_state = all_states[-1]
            if "synthesize" in final_state:
                messages = final_state["synthesize"].get("messages", [])
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage) and hasattr(msg, "content") and msg.content:
                        if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                            response_text = msg.content
                            break
        
        # Priority 2: If no tools called, use call_tools node response (check all states)
        if not response_text:
            for state_idx, state in enumerate(reversed(all_states)):
                if "call_tools" in state:
                    messages = state["call_tools"].get("messages", [])
                    for msg in reversed(messages):
                        if isinstance(msg, AIMessage) and hasattr(msg, "content") and msg.content:
                            if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                content = msg.content.strip()
                                # Always use call_tools response if it exists and is not empty
                                if content:
                                    response_text = content
                                    break
                    if response_text:
                        break
        
        # Priority 3: Fallback to synthesize node
        if not response_text and all_states:
            final_state = all_states[-1]
            if "synthesize" in final_state:
                messages = final_state["synthesize"].get("messages", [])
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage) and hasattr(msg, "content") and msg.content:
                        if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                            content = msg.content.strip()
                            if content and content not in [
                                "How can I assist you today?",
                                "Hello! How can I help you?",
                            ]:
                                response_text = content
                                break
        
        if not response_text:
            logger.warning(f"No response text extracted for thread: {thread_id}")
            response_text = "I apologize, but I couldn't generate a response. Please try again."
        else:
            logger.info(f"Response generated - length: {len(response_text)}")
            logger.debug(f"Response preview: {response_text[:200]}")
        
        return GenerateResponse(response=response_text, thread_id=thread_id)
        
    except Exception as e:
        logger.error(f"Error processing generate request: {e}", exc_info=True)
        import traceback
        error_detail = f"Error processing generate request: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting FastAPI server on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
