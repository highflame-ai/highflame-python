"""LangGraph agent definition for customer support."""

import os
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from src.agent.state import AgentState
from src.agent.llm import get_llm
from src.agent.mcp_tools import create_mcp_tools
from src.agent.tools.web_search import web_search_tool, web_search_news_tool
from src.agent.tools.email import send_email_tool
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Collect all tools (MCP + Direct)
def get_tools():
    """Get all available tools: MCP tools + direct tools."""
    # Get MCP tools (database operations)
    mcp_tools = create_mcp_tools()

    # Direct tools (no database access)
    direct_tools = [
        web_search_tool,
        web_search_news_tool,
        send_email_tool,
    ]

    return mcp_tools + direct_tools


def start_node(state: AgentState) -> AgentState:
    """Seed conversation with a single system prompt and ensure defaults."""
    messages = state.get("messages", [])
    outputs: dict = {}

    if not any(isinstance(msg, SystemMessage) for msg in messages):
        system_prompt = SystemMessage(
            content=(
                "You are a professional customer support AI assistant for Highflame. "
                "Be direct and helpful - only greet on the very first message of a conversation. "
                "\n\nYour capabilities include:"
                "\n1. Order Management: Look up order details, check order status, view order history"
                "\n2. Customer Support: Find customer information, view customer profiles, create new customers"
                "\n3. Ticket Management: Create, update, and check support tickets"
                "\n4. Knowledge Base: Search help articles and FAQs"
                "\n5. Web Search: Find current information from the web"
                "\n6. Email: Send emails to customers"
                "\n\nCRITICAL RULES:"
                "\n1. You must ALWAYS use tools to retrieve factual information. Never guess or fabricate data."
                "\n2. MEMORY AND CONVERSATION HISTORY: You have access to the FULL conversation history in the messages you receive. "
                "When a user asks about previous questions, messages, or conversation context, you MUST look through the HumanMessage "
                "instances in the conversation history and answer based on what was actually said. DO NOT default to listing capabilities "
                "when asked about conversation history."
                "\n3. When asked 'what questions did I ask', 'what did I ask you', 'last questions', or similar queries about the conversation, "
                "you MUST examine the HumanMessage objects in the conversation history and list the actual questions the user asked."
                "\n4. When asked about your capabilities (e.g., 'what can you do'), explain what you can do based on the tools available to you."
                "\n5. After receiving tool results, provide a clear, concise summary to the user."
                "\n6. Always use the conversation history to provide context-aware responses. The messages array contains the full conversation."
            )
        )
        outputs["messages"] = [system_prompt]

    # Ensure optional fields are initialized so downstream nodes can rely on them
    if "customer_id" not in state:
        outputs["customer_id"] = None
    if "current_ticket_id" not in state:
        outputs["current_ticket_id"] = None
    if "tool_calls" not in state:
        outputs["tool_calls"] = []
    if "context" not in state:
        outputs["context"] = {}
    if "intent" not in state:
        outputs["intent"] = None
    if "confidence" not in state:
        outputs["confidence"] = 0.5
    if "should_escalate" not in state:
        outputs["should_escalate"] = False

    return outputs


def understand_intent_node(state: AgentState) -> AgentState:
    """Classify customer query intent with improved categorization."""
    logger.debug("Understanding intent node")
    llm = get_llm()
    messages = state.get("messages", [])
    
    # Get the last user message
    last_message = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_message = msg.content
            break

    logger.debug(f"Classifying intent for message: {last_message[:100]}")
    intent_prompt = f"""Analyze this customer support message and classify its primary intent.

Message: "{last_message}"

Intent categories:
- order_inquiry: Questions about specific orders, shipping status, tracking, delivery
- account: Customer account info, profile, login, registration
- ticket_management: Creating, updating, or checking support tickets
- billing: Payments, refunds, invoices, pricing questions
- technical_support: Product issues, troubleshooting, how-to questions
- general: General questions, policies, FAQs, product information

Rules:
1. Choose the MOST SPECIFIC category that fits
2. If message contains order numbers (ORD-XXX), likely "order_inquiry"
3. If asking about policies/procedures, likely "general"
4. If reporting a problem, likely "technical_support" or "ticket_management"

Respond with ONLY the category name, nothing else."""

    response = llm.invoke([HumanMessage(content=intent_prompt)])
    intent = response.content.strip().lower()
    
    # Validate and set confidence
    valid_intents = {
        "order_inquiry",
        "account",
        "ticket_management",
        "billing",
        "technical_support",
        "general",
    }

    confidence = 0.9 if intent in valid_intents else 0.5
    if intent not in valid_intents:
        intent = "general"  # Default fallback
    
    return {
        "intent": intent,
        "confidence": confidence,
    }


def call_tools_node(state: AgentState) -> AgentState:
    """Invoke appropriate tools based on intent."""
    logger.debug("Call tools node")
    llm = get_llm()
    tools = get_tools()
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    messages = state.get("messages", [])
    if not messages:
        logger.warning("No messages in state for call_tools_node")
        return {}

    # Log conversation context for debugging
    from langchain_core.messages import HumanMessage
    human_messages = [msg.content for msg in messages if isinstance(msg, HumanMessage)]
    logger.debug(f"Calling tools with {len(messages)} total messages, {len(human_messages)} human messages")
    if len(human_messages) > 1:
        logger.debug(f"Previous human messages: {human_messages[:-1]}")

    logger.debug(f"Invoking LLM with {len(tools)} tools available")
    response = llm_with_tools.invoke(messages)

    if hasattr(response, "tool_calls") and response.tool_calls:
        existing_calls = state.get("tool_calls", [])
        new_calls = [
            {
                "tool": tool_call["name"],
                "args": tool_call.get("args", {}),
                "id": tool_call.get("id", ""),
            }
            for tool_call in response.tool_calls
        ]
        logger.info(f"LLM requested {len(response.tool_calls)} tool calls: {[tc['name'] for tc in response.tool_calls]}")
        return {
            "messages": [response],
            "tool_calls": existing_calls + new_calls,
        }

    # No tool calls made - return the response
    logger.debug("LLM responded without tool calls")
    if hasattr(response, "content") and response.content:
        logger.debug(f"LLM response preview: {response.content[:200]}")
    return {"messages": [response]}


def synthesize_response_node(state: AgentState) -> AgentState:
    """Generate final response from tool results."""
    logger.debug("Synthesize response node")
    llm = get_llm()
    messages = state.get("messages", [])
    if not messages:
        logger.warning("No messages in state for synthesize_response_node")
        return {}

    # Keep ALL messages including system message for full context
    # This ensures the LLM has access to conversation history
    llm_messages = [msg for msg in messages if hasattr(msg, "content")]
    
    # Log message types for debugging memory
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    human_count = sum(1 for msg in llm_messages if isinstance(msg, HumanMessage))
    ai_count = sum(1 for msg in llm_messages if isinstance(msg, AIMessage))
    tool_count = sum(1 for msg in llm_messages if isinstance(msg, ToolMessage))
    logger.debug(f"Synthesizing response from {len(llm_messages)} messages (Human: {human_count}, AI: {ai_count}, Tool: {tool_count})")
    
    # Log ALL human messages for debugging memory
    all_human = [msg.content for msg in llm_messages if isinstance(msg, HumanMessage)]
    if all_human:
        logger.debug(f"All human messages in context ({len(all_human)} total): {all_human}")
        if len(all_human) > 1:
            logger.info(f"Conversation history available: {len(all_human)} human messages in context")
            logger.debug(f"Previous questions: {all_human[:-1]}")

    response = llm.invoke(llm_messages)
    logger.debug(f"Generated response length: {len(response.content) if hasattr(response, 'content') else 0}")

    confidence = state.get("confidence", 0.5)
    if hasattr(response, "content") and response.content:
        if "I don't know" in response.content or "i'm not sure" in response.content.lower():
            confidence = min(confidence, 0.4)
            logger.debug(f"Low confidence detected, adjusted to {confidence}")
    
    return {
        "messages": [response],
        "confidence": confidence,
    }


def escalate_node(state: AgentState) -> AgentState:
    """Handle escalation to human agent."""
    escalation_message = AIMessage(
        content=(
        "I understand this is a complex issue. Let me connect you with a human support agent "
        "who can provide more specialized assistance. Your ticket has been created and you'll "
        "receive an email confirmation shortly."
        )
    )
    return {"messages": [escalation_message], "should_escalate": True}
    

def should_continue_after_call_tools(
    state: AgentState,
) -> Literal["tools", "synthesize", "escalate", "end"]:
    """Determine next step after call_tools node."""
    messages = state.get("messages", [])
    if not messages:
        logger.debug("No messages, ending")
        return "end"
    
    last_message = messages[-1]
    
    # Check if we need to escalate
    if state.get("should_escalate", False):
        logger.info("Escalation requested")
        return "escalate"
    
    # Check if last message has tool calls - route to tools node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.debug(f"Routing to tools node ({len(last_message.tool_calls)} tool calls)")
        return "tools"
    
    # Check confidence for escalation
    confidence = state.get("confidence", 0.5)
    if confidence < 0.3:
        logger.warning(f"Low confidence ({confidence}), escalating")
        return "escalate"
    
    # If no tool calls and model provided a response, check if we need to synthesize
    # Only synthesize if we have UNSYNTHESIZED tool results to incorporate
    if isinstance(last_message, AIMessage) and last_message.content:
        # If the last message is an AIMessage without tool_calls, it means the LLM answered directly
        # Check if there are any tool messages AFTER this AI message (which would be impossible)
        # OR if there are tool messages that haven't been followed by a synthesized response
        
        # Find the last AI message with tool_calls (if any)
        last_tool_call_ai_idx = -1
        for i in range(len(messages) - 1, -1, -1):
            msg = messages[i]
            if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
                last_tool_call_ai_idx = i
                break
        
        # If there's a tool-calling AI message, check if there are tool messages after it
        # that haven't been synthesized yet (i.e., no AI message after the tool messages)
        has_unsynthesized_tool_messages = False
        if last_tool_call_ai_idx >= 0:
            # Find tool messages after the tool-calling AI message
            tool_message_indices = []
            for i in range(last_tool_call_ai_idx + 1, len(messages)):
                msg = messages[i]
                if isinstance(msg, ToolMessage):
                    tool_message_indices.append(i)
            
            # Check if there's an AI message after the tool messages (synthesized)
            if tool_message_indices:
                last_tool_idx = tool_message_indices[-1]
                # Check if there's an AI message after the last tool message
                has_synthesized_response = False
                for i in range(last_tool_idx + 1, len(messages)):
                    msg = messages[i]
                    if isinstance(msg, AIMessage) and not (hasattr(msg, "tool_calls") and msg.tool_calls):
                        has_synthesized_response = True
                        break
                
                if not has_synthesized_response:
                    # Tool messages exist but haven't been synthesized yet
                    has_unsynthesized_tool_messages = True
                    logger.debug(f"Found unsynthesized tool messages after index {last_tool_call_ai_idx}")
        
        if not has_unsynthesized_tool_messages:
            # No unsynthesized tool messages - LLM answered directly
            logger.info("Model provided direct answer without tools, ending")
            return "end"

    # If we have tool results, synthesize them
    logger.debug("Routing to synthesize node to incorporate tool results")
    return "synthesize"


def should_continue_after_synthesize(state: AgentState) -> Literal["call_tools", "escalate", "end"]:
    """Determine next step after synthesize node."""
    messages = state.get("messages", [])
    if not messages:
        return "end"
    
    last_message = messages[-1]
    
    # Check if we need to escalate
    if state.get("should_escalate", False):
        return "escalate"
    
    # Check if last message has tool calls - need to call tools again
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tools"
    
    # Check confidence for escalation
    confidence = state.get("confidence", 0.5)
    if confidence < 0.3:
        return "escalate"
    
    # Default to ending conversation
    return "end"


def create_agent_graph():
    """Create and compile the LangGraph agent."""
    logger.info("Creating agent graph")
    # Create tool node
    tools = get_tools()
    tool_node = ToolNode(tools)
    logger.debug("Tool node created")
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("start", start_node)
    workflow.add_node("understand_intent", understand_intent_node)
    workflow.add_node("call_tools", call_tools_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("synthesize", synthesize_response_node)
    workflow.add_node("escalate", escalate_node)
    
    # Set entry point
    workflow.set_entry_point("start")
    
    # Add edges
    workflow.add_edge("start", "understand_intent")
    workflow.add_edge("understand_intent", "call_tools")
    workflow.add_conditional_edges(
        "call_tools",
        should_continue_after_call_tools,
        {"tools": "tools", "synthesize": "synthesize", "escalate": "escalate", "end": END},
    )
    # Tools node outputs tool messages, which should go directly to synthesize
    # But we need to ensure the message sequence is valid
    workflow.add_edge("tools", "synthesize")
    workflow.add_conditional_edges(
        "synthesize",
        should_continue_after_synthesize,
        {"call_tools": "call_tools", "escalate": "escalate", "end": END},
    )
    workflow.add_edge("escalate", END)
    
    # Add memory for conversation persistence
    memory = MemorySaver()
    
    # Compile graph
    logger.debug("Compiling agent graph with memory")
    app = workflow.compile(checkpointer=memory)
    logger.info("Agent graph compiled successfully")
    
    return app


# Create the agent instance
def get_agent():
    """Get the compiled agent graph."""
    return create_agent_graph()
