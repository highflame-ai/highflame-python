"""Streamlit UI for Customer Support Agent."""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path (go up from src/ui/app.py to project root)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables from .env file
from dotenv import load_dotenv

env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Try default locations

from langchain_core.messages import HumanMessage
from src.agent.graph import get_agent
from src.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Page config
st.set_page_config(page_title="Customer Support Agent", page_icon="💬", layout="wide")

# Initialize session state
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "current_thread" not in st.session_state:
    st.session_state.current_thread = None
if "agent" not in st.session_state:
    try:
        # Verify Highflame API keys are loaded
        logger.info("Checking Highflame API keys")
        
        highflame_key = os.getenv("HIGHFLAME_API_KEY")
        llm_api_key = os.getenv("LLM_API_KEY")
        route = os.getenv("HIGHFLAME_ROUTE")
        model = os.getenv("MODEL")
        
        if not highflame_key:
            st.error("HIGHFLAME_API_KEY not found. Please check your .env file.")
            st.info(f"Looking for .env at: {env_path}")
            st.stop()
        
        if not llm_api_key:
            st.error("LLM_API_KEY not found. Please check your .env file.")
            st.info(f"Looking for .env at: {env_path}")
            st.stop()
        
        if not route:
            st.error("HIGHFLAME_ROUTE not found. Please check your .env file.")
            st.info(f"Looking for .env at: {env_path}")
            st.stop()
        
        if not model:
            st.error("MODEL not found. Please check your .env file.")
            st.info(f"Looking for .env at: {env_path}")
            st.stop()
        
        logger.info(f"Highflame configured with route: {route}, model: {model}")
        
        st.session_state.agent = get_agent()
        logger.info("Agent initialized successfully in Streamlit")
    except ValueError as e:
        st.error(f"Configuration error: {e}")
        st.info("Please ensure your .env file contains:")
        st.info("  - HIGHFLAME_API_KEY")
        st.info("  - HIGHFLAME_ROUTE (openai or google)")
        st.info("  - MODEL (e.g., gpt-4o-mini or gemini-2.5-flash-lite)")
        st.info("  - LLM_API_KEY (OpenAI key for openai route, Gemini key for google route)")
        logger.error(f"Configuration error during Streamlit agent initialization: {e}", exc_info=True)
        st.stop()
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        logger.critical(f"Critical error initializing agent in Streamlit: {e}", exc_info=True)
        st.stop()

# Sidebar for conversations
with st.sidebar:
    st.title("💬 Conversations")
    
    # New conversation button
    if st.button("➕ New Conversation", use_container_width=True):
        import uuid

        new_thread = str(uuid.uuid4())
        st.session_state.conversations[new_thread] = []
        st.session_state.current_thread = new_thread
        st.rerun()
    
    st.divider()
    
    # List of conversations
    st.subheader("Recent")
    thread_names = list(st.session_state.conversations.keys())
    
    if not thread_names:
        st.caption("No conversations yet. Start a new one!")
    else:
        for thread_id in thread_names:
            # Get conversation title (first message or thread ID)
            title = f"Thread {thread_id[:8]}"
            if st.session_state.conversations[thread_id]:
                first_msg = st.session_state.conversations[thread_id][0]
                if isinstance(first_msg, dict) and first_msg.get("role") == "user":
                    title = first_msg.get("content", title)[:30] + "..."
            
            # Select conversation
            if st.button(
                title,
                key=f"thread_{thread_id}",
                use_container_width=True,
                type="primary" if thread_id == st.session_state.current_thread else "secondary",
            ):
                st.session_state.current_thread = thread_id
                st.rerun()
    
    st.divider()
    st.caption("💡 Tip: Each conversation maintains its own context and memory.")

# Main chat area
st.title("Customer Support Agent")

# Initialize current conversation if needed
if st.session_state.current_thread is None:
    import uuid

    st.session_state.current_thread = str(uuid.uuid4())
    st.session_state.conversations[st.session_state.current_thread] = []

current_thread = st.session_state.current_thread
if current_thread not in st.session_state.conversations:
    st.session_state.conversations[current_thread] = []

# Display conversation history
chat_container = st.container()
with chat_container:
    for message in st.session_state.conversations[current_thread]:
        role = message.get("role", "user")
        content = message.get("content", "")
        
        if role == "user":
            with st.chat_message("user"):
                st.write(content)
        else:
            with st.chat_message("assistant"):
                st.write(content)
                
                # Show tool calls if available
                if message and isinstance(message, dict) and "tool_calls" in message and message["tool_calls"]:
                    with st.expander("🔧 Tools Used"):
                        for tool_call in message["tool_calls"]:
                            st.code(f"{tool_call.get('tool', 'unknown')}")

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to conversation
    st.session_state.conversations[current_thread].append({"role": "user", "content": user_input})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.write(user_input)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                logger.info(f"Processing user message in thread: {current_thread}")
                logger.debug(f"User message: {user_input[:200]}")
                
                agent = st.session_state.agent
                human_message = HumanMessage(content=user_input)
                
                input_state = {"messages": [human_message]}
                config = {"configurable": {"thread_id": current_thread}}
                
                # Stream response and track all events for debugging
                final_state = None
                response_text = ""
                tool_calls_list = []
                debug_events = []  # Track all events for debug view
                event_count = 0
                
                logger.debug("Starting agent stream")
                for event in agent.stream(input_state, config):
                    final_state = event
                    event_count += 1
                    logger.debug(f"Agent event {event_count}: {list(event.keys())}")
                    
                    # Collect debug info from each event
                    for node_name, node_output in event.items():
                        try:
                            # Fix: Check None first to avoid "argument of type 'NoneType' is not iterable"
                            if node_output is None:
                                logger.debug(f"Node {node_name} has None output")
                                debug_events.append(
                                    {
                                        "node": node_name,
                                        "has_messages": False,
                                        "has_tool_calls": False,
                                        "tool_calls": [],
                                    }
                                )
                                continue
                            
                            # Now safe to check for keys
                            has_messages = "messages" in node_output
                            has_tool_calls = "tool_calls" in node_output
                            tool_calls = node_output.get("tool_calls", [])
                            
                            debug_events.append(
                                {
                                    "node": node_name,
                                    "has_messages": has_messages,
                                    "has_tool_calls": has_tool_calls,
                                    "tool_calls": tool_calls,
                                }
                            )
                        except Exception as e:
                            logger.error(f"Error processing debug event for node {node_name}: {e}", exc_info=True)
                            debug_events.append(
                                {
                                    "node": node_name,
                                    "has_messages": False,
                                    "has_tool_calls": False,
                                    "tool_calls": [],
                                    "error": str(e),
                                }
                            )
                
                logger.debug(f"Agent stream completed with {event_count} events")

                # Extract response and tool calls
                logger.debug("Extracting response from final state")
                if final_state:
                    try:
                        # Priority 1: Check synthesize node
                        if "synthesize" in final_state:
                            logger.debug("Checking synthesize node for response")
                            synthesize_output = final_state.get("synthesize")
                            if synthesize_output:
                                messages = synthesize_output.get("messages", []) if synthesize_output else []
                                for msg in reversed(messages):
                                    if hasattr(msg, "content") and msg.content:
                                        tool_calls_attr = getattr(msg, "tool_calls", None)
                                        if not tool_calls_attr:
                                            response_text = msg.content
                                            logger.debug(f"Found response in synthesize node (length: {len(response_text)})")
                                            break
                        
                        # Priority 2: Check call_tools node
                        if not response_text and "call_tools" in final_state:
                            logger.debug("Checking call_tools node for response")
                            call_tools_output = final_state.get("call_tools")
                            if call_tools_output:
                                messages = call_tools_output.get("messages", []) if call_tools_output else []
                                for msg in reversed(messages):
                                    if hasattr(msg, "content") and msg.content:
                                        tool_calls_attr = getattr(msg, "tool_calls", None)
                                        if not tool_calls_attr:
                                            response_text = msg.content
                                            logger.debug(f"Found response in call_tools node (length: {len(response_text)})")
                                            break
                        
                        # Priority 3: Check all nodes
                        if not response_text:
                            logger.debug("Checking all nodes for response")
                            for node_name, node_output in final_state.items():
                                if node_name in ["start", "understand_intent"]:
                                    continue  # Skip these nodes
                                
                                if node_output is None:
                                    logger.debug(f"Skipping {node_name} - node_output is None")
                                    continue
                                
                                try:
                                    messages = node_output.get("messages", []) if node_output else []
                                    if messages:
                                        # Find the last AI message (non-tool-call message)
                                        for msg in reversed(messages):
                                            if hasattr(msg, "content") and msg.content:
                                                tool_calls_attr = getattr(msg, "tool_calls", None)
                                                if not tool_calls_attr:
                                                    response_text = msg.content
                                                    logger.debug(f"Found response in {node_name} node (length: {len(response_text)})")
                                                    break
                                        if response_text:
                                            break
                                except Exception as e:
                                    logger.error(f"Error extracting response from node {node_name}: {e}", exc_info=True)
                                    continue

                        # Extract tool calls from state
                        logger.debug("Extracting tool calls from final state")
                        for node_name, node_output in final_state.items():
                            if node_output is None:
                                continue
                            
                            try:
                                if "tool_calls" in node_output:
                                    tool_calls = node_output.get("tool_calls", [])
                                    if isinstance(tool_calls, list):
                                        tool_calls_list.extend(tool_calls)
                                        logger.debug(f"Found {len(tool_calls)} tool calls in {node_name}")

                                # Also check messages for tool calls
                                messages = node_output.get("messages", []) if node_output else []
                                if messages:
                                    for msg in messages:
                                        if hasattr(msg, "tool_calls"):
                                            tool_calls_attr = getattr(msg, "tool_calls", None)
                                            if tool_calls_attr and isinstance(tool_calls_attr, list):
                                                for tc in tool_calls_attr:
                                                    if isinstance(tc, dict):
                                                        tool_calls_list.append(
                                                            {
                                                                "tool": tc.get("name", "unknown"),
                                                                "args": tc.get("args", {}),
                                                                "id": tc.get("id", ""),
                                                            }
                                                        )
                            except Exception as e:
                                logger.error(f"Error extracting tool calls from node {node_name}: {e}", exc_info=True)
                                continue
                    except Exception as e:
                        logger.error(f"Error extracting response from final_state: {e}", exc_info=True)
                        response_text = f"Error processing response: {str(e)}"
                
                if not response_text:
                    logger.warning("No response text extracted from agent")
                    response_text = (
                        "I apologize, but I couldn't generate a response. Please try again."
                    )
                else:
                    logger.info(f"Response extracted successfully (length: {len(response_text)})")
                    logger.debug(f"Response preview: {response_text[:200]}")
                
                # Display response
                st.write(response_text)
                
                # Show tool calls with detailed info
                if tool_calls_list:
                    with st.expander(f"🔧 Tools Used ({len(tool_calls_list)})"):
                        for i, tool_call in enumerate(tool_calls_list, 1):
                            tool_name = tool_call.get("tool", "unknown")
                            tool_args = tool_call.get("args", {})
                            st.markdown(f"**{i}. {tool_name}**")
                            if tool_args:
                                st.json(tool_args)
                else:
                    st.caption("ℹ️ No tools were used for this response")

                # Debug view showing conversation flow
                with st.expander("🐛 Debug View (Conversation Flow)"):
                    st.markdown("### Event Flow")
                    for i, event in enumerate(debug_events, 1):
                        st.markdown(f"**{i}. {event['node']}**")
                        st.text(f"   Messages: {event.get('message_count', 0)}")
                        if event.get("tool_calls"):
                            st.text(f"   Tool calls: {len(event['tool_calls'])}")
                            for tc in event["tool_calls"]:
                                st.code(f"     - {tc.get('tool', 'unknown')}")

                    st.markdown("### Memory State")
                    st.text(f"Thread ID: {current_thread}")
                    st.text(
                        f"Messages in UI state: {len(st.session_state.conversations[current_thread])}"
                    )
                    st.text("✓ Memory maintained via LangGraph checkpointer (thread_id)")
                    st.caption(
                        "Note: LangGraph's MemorySaver maintains conversation history internally using the thread_id"
                    )

                # Debug view
                with st.expander("🐛 Debug View (Conversation Flow)"):
                    st.markdown("### Event Flow")
                    for i, event in enumerate(debug_events, 1):
                        st.markdown(f"**{i}. {event['node']}**")
                        if event["has_tool_calls"] and event["tool_calls"]:
                            st.code(f"Tool calls: {event['tool_calls']}")

                    st.markdown("### Full State")
                    if final_state:
                        for node_name, node_output in final_state.items():
                            st.markdown(f"**{node_name}:**")
                            try:
                                if node_output is not None:
                                    if "messages" in node_output:
                                        msg_count = len(node_output["messages"])
                                        st.text(f"  Messages: {msg_count}")
                                    if "tool_calls" in node_output:
                                        st.text(f"  Tool calls: {len(node_output['tool_calls'])}")
                                else:
                                    st.text("  (No output)")
                            except Exception as e:
                                logger.error(f"Error displaying state for node {node_name}: {e}", exc_info=True)
                                st.text(f"  Error: {str(e)}")

                    st.markdown("### Memory Check")
                    st.text(f"Thread ID: {current_thread}")
                    st.text(
                        f"Conversation messages in UI: {len(st.session_state.conversations[current_thread])}"
                    )
                
                # Add assistant response to conversation
                st.session_state.conversations[current_thread].append(
                    {
                    "role": "assistant",
                    "content": response_text,
                        "tool_calls": tool_calls_list if tool_calls_list else None,
                    }
                )
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                logger.error(f"Error in Streamlit UI: {e}", exc_info=True)
                st.error(error_msg)
                st.session_state.conversations[current_thread].append(
                    {"role": "assistant", "content": error_msg}
                )
    
    st.rerun()
