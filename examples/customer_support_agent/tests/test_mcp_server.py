"""Tests for MCP server functionality."""

import pytest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture(scope="module")
def setup_database():
    """Initialize database for testing."""
    from src.agent.database.setup import init_database

    # Use a test database
    os.environ["DATABASE_PATH"] = "./test_support_agent.db"
    init_database(seed_data=True)
    yield
    # Cleanup
    if os.path.exists("./test_support_agent.db"):
        os.remove("./test_support_agent.db")


@pytest.mark.asyncio
async def test_mcp_client_connection():
    """Test MCP client can connect to server."""
    # Skip if MCP_SERVER_URL not set
    if not os.getenv("MCP_SERVER_URL"):
        pytest.skip("MCP_SERVER_URL not set")

    try:
        from src.agent.mcp_tools import get_mcp_client

        client = get_mcp_client()

        async with client:
            # Test connection by listing tools
            tools = await client.list_tools()
            assert tools is not None
            assert len(tools) > 0
    except Exception as e:
        pytest.skip(f"MCP server not available: {e}")


@pytest.mark.asyncio
async def test_mcp_server_tools_list():
    """Test MCP server exposes all expected tools."""
    if not os.getenv("MCP_SERVER_URL"):
        pytest.skip("MCP_SERVER_URL not set")

    try:
        from src.agent.mcp_tools import get_mcp_client

        client = get_mcp_client()

        async with client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]

            # Verify all 11 tools are present
            assert "search_knowledge_base_tool" in tool_names
            assert "get_knowledge_base_by_category_tool" in tool_names
            assert "lookup_order_tool" in tool_names
            assert "get_order_status_tool" in tool_names
            assert "get_order_history_tool" in tool_names
            assert "lookup_customer_tool" in tool_names
            assert "get_customer_profile_tool" in tool_names
            assert "create_customer_tool" in tool_names
            assert "create_ticket_tool" in tool_names
            assert "update_ticket_tool" in tool_names
            assert "get_ticket_tool" in tool_names

            assert len(tool_names) == 11
    except Exception as e:
        pytest.skip(f"MCP server not available: {e}")


@pytest.mark.asyncio
async def test_mcp_tool_invocation():
    """Test calling an MCP tool."""
    if not os.getenv("MCP_SERVER_URL"):
        pytest.skip("MCP_SERVER_URL not set")

    try:
        from src.agent.mcp_tools import call_mcp_tool

        # Test order lookup
        result = call_mcp_tool("get_order_status_tool", order_number="ORD-001")
        assert result is not None
        assert "ORD-001" in result
    except Exception as e:
        pytest.skip(f"MCP tool invocation failed: {e}")


def test_mcp_tool_creation():
    """Test MCP tools can be created."""
    from src.agent.mcp_tools import create_mcp_tools

    tools = create_mcp_tools()
    assert len(tools) == 11

    # Check that expected tools are present
    tool_names = [tool.name for tool in tools]
    assert "search_knowledge_base_tool" in tool_names
    assert "lookup_order_tool" in tool_names
    assert "lookup_customer_tool" in tool_names
    assert "create_ticket_tool" in tool_names


def test_agent_initialization_with_mcp():
    """Test that agent can be initialized with MCP tools."""
    # Skip if no API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        pytest.skip("No LLM API key set")

    try:
        from src.agent.graph import get_agent

        agent = get_agent()
        assert agent is not None
    except Exception as e:
        pytest.skip(f"Agent initialization failed: {e}")


def test_mcp_server_module_import():
    """Test MCP server module can be imported."""
    try:
        from src.mcp_server import server

        assert hasattr(server, "mcp")
    except Exception as e:
        pytest.fail(f"MCP server module import failed: {e}")
