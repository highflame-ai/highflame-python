"""Main entry point for the customer support agent."""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.database.setup import init_database
from src.agent.graph import get_agent


def load_environment():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        # Try current directory
        load_dotenv()

    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_key_here")
        sys.exit(1)


def initialize_database():
    """Initialize the database with tables and sample data."""
    print("Initializing database...")
    try:
        init_database(seed_data=True)
        print("✓ Database initialized successfully.\n")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


def print_separator():
    """Print a separator line."""
    print("\n" + "=" * 80 + "\n")


def print_message(role: str, content: str, tool_calls=None):
    """Print a formatted message."""
    print(f"[{role.upper()}]")
    print(content)
    if tool_calls:
        print(f"\n🔧 Tools Used: {', '.join(tc.get('tool', 'unknown') for tc in tool_calls)}")
    print()


def run_test_conversations():
    """Run automated test conversations to verify functionality."""
    print_separator()
    print("🧪 AUTOMATED TEST SUITE - Multi-Turn Conversations")
    print_separator()

    # Load environment and initialize
    load_environment()
    initialize_database()

    # Get the agent
    try:
        agent = get_agent()
        print("✓ Agent initialized successfully\n")
    except Exception as e:
        print(f"✗ Error creating agent: {e}")
        sys.exit(1)

    # Test scenarios
    test_scenarios = [
        {
            "name": "Order Lookup Test",
            "thread_id": "test_order_lookup",
            "messages": [
                "What is the status of order ORD-001?",
                "Can you tell me the total amount for that order?",
                "What was the last question I asked you?",
            ],
            "expected_tools": ["get_order_status_tool"],
        },
        {
            "name": "Customer Lookup Test",
            "thread_id": "test_customer_lookup",
            "messages": [
                "Who is customer john.doe@example.com?",
                "Show me their order history",
                "What did I ask you first?",
            ],
            "expected_tools": ["lookup_customer_tool", "get_order_history_tool"],
        },
        {
            "name": "Knowledge Base Test",
            "thread_id": "test_knowledge_base",
            "messages": [
                "What is your return policy?",
                "How long does shipping take?",
                "Can you remind me what I asked about shipping?",
            ],
            "expected_tools": ["search_knowledge_base_tool"],
        },
        {
            "name": "Ticket Creation Test",
            "thread_id": "test_ticket_creation",
            "messages": [
                "I need help with my order",
                "My order number is ORD-002",
                "Create a support ticket for this issue",
            ],
            "expected_tools": ["create_ticket_tool"],
        },
        {
            "name": "Memory Test",
            "thread_id": "test_memory",
            "messages": [
                "My name is Test User and my email is test@example.com",
                "What is my name?",
                "What is my email?",
                "What were the first two things I told you?",
            ],
            "expected_tools": [],
        },
        {
            "name": "Multi-Tool Test",
            "thread_id": "test_multi_tool",
            "messages": [
                "I want to check order ORD-001 and also know the return policy",
                "Can you create a ticket for order ORD-001?",
            ],
            "expected_tools": [
                "lookup_order_tool",
                "search_knowledge_base_tool",
                "create_ticket_tool",
            ],
        },
    ]

    # Run each test scenario
    for scenario_idx, scenario in enumerate(test_scenarios, 1):
        print_separator()
        print(f"📋 Test {scenario_idx}: {scenario['name']}")
        print(f"Thread ID: {scenario['thread_id']}")
        print_separator()

        thread_id = scenario["thread_id"]
        config = {"configurable": {"thread_id": thread_id}}

        all_tool_calls = []

        for turn_idx, user_message in enumerate(scenario["messages"], 1):
            print(f"\n--- Turn {turn_idx} ---")
            print_message("user", user_message)

            try:
                # Create human message
                human_message = HumanMessage(content=user_message)
                input_state = {"messages": [human_message]}

                # Get agent response
                print("🤖 Agent processing...")
                final_state = None
                response_text = ""
                tool_calls_list = []

                collected_tool_calls = []

                for event in agent.stream(input_state, config):
                    final_state = event

                    for node_name, node_output in event.items():
                        if not node_output:
                            continue
                        messages = node_output.get("messages", [])

                        # Collect tool calls directly from node output
                        node_tool_calls = node_output.get("tool_calls") or []
                        if node_tool_calls:
                            collected_tool_calls.extend(node_tool_calls)
                            all_tool_calls.extend(node_tool_calls)

                        # Collect tool calls embedded in messages
                        for msg in messages:
                            if getattr(msg, "tool_calls", None):
                                for tc in msg.tool_calls:
                                    tool_call_entry = {
                                        "tool": tc.get("name", "unknown"),
                                        "args": tc.get("args", {}),
                                    }
                                    collected_tool_calls.append(tool_call_entry)
                                    all_tool_calls.append(tool_call_entry)

                # Extract response and tool calls
                if final_state:
                    for node_name, node_output in final_state.items():
                        if not node_output:
                            continue
                        messages = node_output.get("messages", [])
                        if messages:
                            # Find the last AI message (non-tool-call message)
                            for msg in reversed(messages):
                                if hasattr(msg, "content") and msg.content:
                                    if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                        response_text = msg.content
                                        break

                        # Use collected tool calls for this turn
                        if collected_tool_calls:
                            tool_calls_list = collected_tool_calls

                if not response_text:
                    response_text = "No response generated."

                print_message(
                    "assistant", response_text, tool_calls_list if tool_calls_list else None
                )

                # Small delay between turns
                time.sleep(0.5)

            except Exception as e:
                print(f"✗ Error in turn {turn_idx}: {e}")
                import traceback

                traceback.print_exc()
                break

        # Verify expected tools were used
        if scenario.get("expected_tools"):
            used_tools = [tc.get("tool") for tc in all_tool_calls]
            expected = scenario["expected_tools"]
            found = [tool for tool in expected if tool in used_tools]
            print(f"\n✓ Tools Verification:")
            print(f"  Expected: {expected}")
            print(f"  Found: {found}")
            if len(found) == len(expected):
                print(f"  ✅ All expected tools were used!")
            else:
                print(f"  ⚠️  Some expected tools were not used")

        print(f"\n✓ Test '{scenario['name']}' completed")
        time.sleep(1)

    print_separator()
    print("✅ All test scenarios completed!")
    print_separator()


def run_conversation():
    """Run interactive conversation loop with the agent."""
    print("\n" + "=" * 60)
    print("Customer Support Agent - Interactive Mode")
    print("=" * 60)
    print("Type 'quit' or 'exit' to end the conversation.\n")

    # Load environment and initialize
    load_environment()
    initialize_database()

    # Get the agent
    try:
        agent = get_agent()
    except Exception as e:
        print(f"Error creating agent: {e}")
        sys.exit(1)

    # Conversation thread ID for state management
    thread_id = "customer_support_session"
    config = {"configurable": {"thread_id": thread_id}}

    print("Agent ready! How can I help you today?\n")

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nThank you for contacting customer support. Have a great day!")
                break

            # Create human message
            human_message = HumanMessage(content=user_input)

            # Invoke agent with the new message
            # LangGraph will maintain state via checkpointer
            input_state = {"messages": [human_message]}

            # Stream the response
            print("\nAgent: ", end="", flush=True)

            final_state = None
            tool_calls_list = []

            for event in agent.stream(input_state, config):
                final_state = event

            # Extract and print the final response
            response_text = ""
            if final_state:
                for node_name, node_output in final_state.items():
                    messages = node_output.get("messages", [])
                    if messages:
                        # Find the last AI message (non-tool-call message)
                        for msg in reversed(messages):
                            if hasattr(msg, "content") and msg.content:
                                if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                    response_text = msg.content
                                    break

                    # Extract tool calls
                    if "tool_calls" in node_output:
                        tool_calls_list = node_output.get("tool_calls", [])

            if response_text:
                print(response_text)
                if tool_calls_list:
                    print(
                        f"\n🔧 Tools used: {', '.join(tc.get('tool', 'unknown') for tc in tool_calls_list)}"
                    )
            else:
                print("I apologize, but I couldn't generate a response.")

            print()  # New line after response

        except KeyboardInterrupt:
            print("\n\nConversation interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback

            traceback.print_exc()
            print("Please try again or type 'quit' to exit.\n")


def run_single_query(query: str):
    """Run a single query and return the response."""
    load_environment()
    initialize_database()

    try:
        agent = get_agent()
    except Exception as e:
        print(f"Error creating agent: {e}")
        sys.exit(1)

    thread_id = "single_query_session"
    config = {"configurable": {"thread_id": thread_id}}

    human_message = HumanMessage(content=query)
    input_state = {"messages": [human_message]}

    # Get final response
    final_state = None
    for event in agent.stream(input_state, config):
        final_state = event

    # Extract response from final state
    if final_state:
        for node_name, node_output in final_state.items():
            messages = node_output.get("messages", [])
            if messages:
                # Find the last AI message (non-tool-call message)
                for msg in reversed(messages):
                    if hasattr(msg, "content") and msg.content:
                        if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                            return msg.content

    return "No response generated."


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Run automated tests
            run_test_conversations()
        else:
            # Single query mode
            query = " ".join(sys.argv[1:])
            response = run_single_query(query)
            print(response)
    else:
        # Run interactive mode
        run_conversation()
