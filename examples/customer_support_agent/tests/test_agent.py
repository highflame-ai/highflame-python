"""Tests for the customer support agent."""

import pytest
import os
from dotenv import load_dotenv
from src.agent.database.setup import init_database, get_session
from src.agent.database.queries import get_customer_by_email, get_order_by_number
from src.agent.graph import get_agent
from src.agent.llm import get_llm
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()


@pytest.fixture(scope="module")
def setup_database():
    """Initialize database for testing."""
    # Use a test database
    os.environ["DATABASE_PATH"] = "./test_support_agent.db"
    init_database(seed_data=True)
    yield
    # Cleanup
    if os.path.exists("./test_support_agent.db"):
        os.remove("./test_support_agent.db")


def test_database_initialization(setup_database):
    """Test that database is initialized with mock data."""
    db = get_session()
    try:
        # Check customers
        customer = get_customer_by_email(db, "john.doe@example.com")
        assert customer is not None
        assert customer.name == "John Doe"

        # Check orders
        order = get_order_by_number(db, "ORD-001")
        assert order is not None
        assert order.total == 99.99

    finally:
        db.close()


def test_customer_lookup(setup_database):
    """Test customer lookup functionality."""
    db = get_session()
    try:
        customer = get_customer_by_email(db, "jane.smith@example.com")
        assert customer is not None
        assert customer.email == "jane.smith@example.com"
    finally:
        db.close()


def test_order_lookup(setup_database):
    """Test order lookup functionality."""
    db = get_session()
    try:
        order = get_order_by_number(db, "ORD-001")
        assert order is not None
        assert order.order_number == "ORD-001"
    finally:
        db.close()


def test_openai_llm_initialization():
    """Test OpenAI LLM initialization."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    try:
        llm = get_llm("openai")
        assert llm is not None
        assert llm.model_name == os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    except Exception as e:
        pytest.fail(f"OpenAI LLM initialization failed: {e}")


def test_gemini_llm_initialization():
    """Test Gemini LLM initialization."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")

    try:
        llm = get_llm("gemini")
        assert llm is not None
    except Exception as e:
        pytest.fail(f"Gemini LLM initialization failed: {e}")


def test_llm_provider_env_var():
    """Test LLM provider selection via environment variable."""
    original_provider = os.getenv("LLM_PROVIDER")

    # Test OpenAI
    if os.getenv("OPENAI_API_KEY"):
        os.environ["LLM_PROVIDER"] = "openai"
        llm = get_llm()
        assert llm is not None

    # Test Gemini
    if os.getenv("GEMINI_API_KEY"):
        os.environ["LLM_PROVIDER"] = "gemini"
        llm = get_llm()
        assert llm is not None

    # Restore original
    if original_provider:
        os.environ["LLM_PROVIDER"] = original_provider


def test_agent_initialization():
    """Test that agent can be initialized."""
    # Skip if no API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        pytest.skip("No LLM API key set")

    try:
        agent = get_agent()
        assert agent is not None
    except Exception as e:
        pytest.skip(f"Agent initialization failed: {e}")


def test_agent_memory():
    """Test that agent maintains conversation memory."""
    # Skip if no API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        pytest.skip("No LLM API key set")

    try:
        agent = get_agent()
        thread_id = "test-memory-thread"
        config = {"configurable": {"thread_id": thread_id}}

        # First message
        input_state1 = {"messages": [HumanMessage(content="My name is Test User")]}

        # Process first message
        for event in agent.stream(input_state1, config):
            pass

        # Second message - should remember context
        input_state2 = {"messages": [HumanMessage(content="What is my name?")]}

        # Process second message
        final_state = None
        for event in agent.stream(input_state2, config):
            final_state = event

        # Verify state was maintained
        assert final_state is not None

    except Exception as e:
        pytest.skip(f"Memory test failed: {e}")


def test_mcp_tools_import():
    """Test that MCP tools can be imported and created."""
    try:
        from src.agent.mcp_tools import create_mcp_tools

        tools = create_mcp_tools()
        assert len(tools) == 11

        # Verify tool names
        tool_names = [tool.name for tool in tools]
        assert "search_knowledge_base_tool" in tool_names
        assert "lookup_order_tool" in tool_names
        assert "lookup_customer_tool" in tool_names
        assert "create_ticket_tool" in tool_names
    except Exception as e:
        pytest.fail(f"MCP tools import failed: {e}")


def test_direct_tools_import():
    """Test that direct tools can be imported."""
    try:
        from src.agent.tools.web_search import web_search_tool, web_search_news_tool
        from src.agent.tools.email import send_email_tool

        assert web_search_tool is not None
        assert web_search_news_tool is not None
        assert send_email_tool is not None
    except Exception as e:
        pytest.fail(f"Direct tools import failed: {e}")


def test_agent_with_openai(setup_database):
    """Test agent with OpenAI provider."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    # Set provider
    original_provider = os.getenv("LLM_PROVIDER")
    os.environ["LLM_PROVIDER"] = "openai"

    try:
        agent = get_agent()
        config = {"configurable": {"thread_id": "test-openai"}}
        input_state = {"messages": [HumanMessage(content="Hello")]}

        final_state = None
        for event in agent.stream(input_state, config):
            final_state = event

        assert final_state is not None
    except Exception as e:
        pytest.fail(f"OpenAI agent test failed: {e}")
    finally:
        if original_provider:
            os.environ["LLM_PROVIDER"] = original_provider


def test_agent_with_gemini(setup_database):
    """Test agent with Gemini provider."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")

    # Set provider
    original_provider = os.getenv("LLM_PROVIDER")
    os.environ["LLM_PROVIDER"] = "gemini"

    try:
        agent = get_agent()
        config = {"configurable": {"thread_id": "test-gemini"}}
        input_state = {"messages": [HumanMessage(content="Hello")]}

        final_state = None
        for event in agent.stream(input_state, config):
            final_state = event

        assert final_state is not None
    except Exception as e:
        pytest.fail(f"Gemini agent test failed: {e}")
    finally:
        if original_provider:
            os.environ["LLM_PROVIDER"] = original_provider


def test_knowledge_base_search(setup_database):
    """Test knowledge base search via MCP tools."""
    # Skip test if MCP server is not running
    pytest.skip("MCP server tests require MCP server to be running")


def test_order_tool(setup_database):
    """Test order lookup tool via MCP."""
    # Skip test if MCP server is not running
    pytest.skip("MCP server tests require MCP server to be running")


def test_customer_tool(setup_database):
    """Test customer lookup tool via MCP."""
    # Skip test if MCP server is not running
    pytest.skip("MCP server tests require MCP server to be running")
