"""MCP client wrapper for database tools."""

import os
import asyncio
from fastmcp import Client
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional, List
from src.utils.logger import get_logger

logger = get_logger(__name__)


# MCP client singleton
_mcp_client = None


def get_mcp_client():
    """Get or create MCP client."""
    global _mcp_client
    if _mcp_client is None:
        # FastMCP defaults to port 8000 with SSE transport
        mcp_url = os.getenv("MCP_SERVER_URL", "http://0.0.0.0:9000/mcp")
        _mcp_client = Client(mcp_url)
    return _mcp_client


async def call_mcp_tool_async(tool_name: str, **kwargs):
    """Call MCP tool asynchronously."""
    logger.debug(f"Calling MCP tool: {tool_name} with args: {kwargs}")
    client = get_mcp_client()
    try:
        async with client:
            result = await client.call_tool(tool_name, kwargs)
            if not result:
                logger.error(f"MCP tool {tool_name} returned None result")
                return "Error: Tool returned no result"
            
            if not result.content:
                logger.warning(f"MCP tool {tool_name} returned empty content")
                return ""
            
            if len(result.content) == 0:
                logger.warning(f"MCP tool {tool_name} returned empty content list")
                return ""
            
            first_content = result.content[0]
            if not hasattr(first_content, 'text'):
                logger.error(f"MCP tool {tool_name} content missing text attribute")
                return f"Error: Unexpected response format from tool {tool_name}"
            
            response_text = first_content.text if first_content.text else ""
            logger.debug(f"MCP tool {tool_name} returned response (length: {len(response_text)})")
            return response_text
    except Exception as e:
        logger.error(f"Error calling MCP tool {tool_name}: {e}", exc_info=True)
        raise


def call_mcp_tool(tool_name: str, **kwargs):
    """Call MCP tool synchronously."""
    return asyncio.run(call_mcp_tool_async(tool_name, **kwargs))


# Pydantic Schemas for Tools


class SearchKnowledgeBaseSchema(BaseModel):
    """Search knowledge base input schema."""

    query: str = Field(..., description="The search query or keywords to search for")
    category: Optional[str] = Field(None, description="Optional category to filter results")


class GetKnowledgeBaseByCategorySchema(BaseModel):
    """Get knowledge base by category input schema."""

    category: str = Field(..., description="The category to retrieve articles from")


class LookupOrderSchema(BaseModel):
    """Lookup order input schema."""

    order_number: str = Field(..., description="The order number to look up (e.g., 'ORD-001')")
    customer_id: Optional[int] = Field(None, description="Optional customer ID to verify")


class GetOrderStatusSchema(BaseModel):
    """Get order status input schema."""

    order_number: str = Field(..., description="The order number to check")


class GetOrderHistorySchema(BaseModel):
    """Get order history input schema."""

    customer_id: int = Field(..., description="The ID of the customer")


class LookupCustomerSchema(BaseModel):
    """Lookup customer input schema."""

    email: Optional[str] = Field(None, description="Customer email address")
    phone: Optional[str] = Field(None, description="Customer phone number")
    customer_id: Optional[int] = Field(None, description="Customer ID")


class GetCustomerProfileSchema(BaseModel):
    """Get customer profile input schema."""

    customer_id: int = Field(..., description="The ID of the customer")


class CreateCustomerSchema(BaseModel):
    """Create customer input schema."""

    name: str = Field(..., description="Customer's full name")
    email: str = Field(..., description="Customer's email address")
    phone: Optional[str] = Field(None, description="Optional phone number")


class CreateTicketSchema(BaseModel):
    """Create ticket input schema."""

    customer_id: int = Field(..., description="The ID of the customer creating the ticket")
    subject: str = Field(..., description="Brief subject line for the ticket")
    description: str = Field(..., description="Detailed description of the issue")
    priority: str = Field(
        "medium", description="Priority level - 'low', 'medium', 'high', or 'urgent'"
    )
    order_id: Optional[int] = Field(
        None, description="Optional order ID if related to a specific order"
    )


class UpdateTicketSchema(BaseModel):
    """Update ticket input schema."""

    ticket_id: int = Field(..., description="The ID of the ticket to update")
    status: Optional[str] = Field(
        None, description="New status - 'open', 'in_progress', 'resolved', or 'closed'"
    )
    notes: Optional[str] = Field(None, description="Additional notes or updates")


class GetTicketSchema(BaseModel):
    """Get ticket input schema."""

    ticket_id: int = Field(..., description="The ID of the ticket to retrieve")


# Create LangChain Tools


def create_mcp_tools() -> List[StructuredTool]:
    """Create LangChain tools that wrap MCP server tools."""

    # Knowledge Base Tools
    search_knowledge_base_tool = StructuredTool(
        name="search_knowledge_base_tool",
        description="Search the knowledge base for information relevant to the customer's query.",
        args_schema=SearchKnowledgeBaseSchema,
        func=lambda **kwargs: call_mcp_tool("search_knowledge_base_tool", **kwargs),
    )

    get_knowledge_base_by_category_tool = StructuredTool(
        name="get_knowledge_base_by_category_tool",
        description="Get all knowledge base articles in a specific category.",
        args_schema=GetKnowledgeBaseByCategorySchema,
        func=lambda **kwargs: call_mcp_tool("get_knowledge_base_by_category_tool", **kwargs),
    )

    # Order Tools
    lookup_order_tool = StructuredTool(
        name="lookup_order_tool",
        description="Look up order details by order number.",
        args_schema=LookupOrderSchema,
        func=lambda **kwargs: call_mcp_tool("lookup_order_tool", **kwargs),
    )

    get_order_status_tool = StructuredTool(
        name="get_order_status_tool",
        description="Get the current status of an order.",
        args_schema=GetOrderStatusSchema,
        func=lambda **kwargs: call_mcp_tool("get_order_status_tool", **kwargs),
    )

    get_order_history_tool = StructuredTool(
        name="get_order_history_tool",
        description="Get all orders for a specific customer.",
        args_schema=GetOrderHistorySchema,
        func=lambda **kwargs: call_mcp_tool("get_order_history_tool", **kwargs),
    )

    # Customer Tools
    lookup_customer_tool = StructuredTool(
        name="lookup_customer_tool",
        description="Look up a customer by email, phone number, or customer ID.",
        args_schema=LookupCustomerSchema,
        func=lambda **kwargs: call_mcp_tool("lookup_customer_tool", **kwargs),
    )

    get_customer_profile_tool = StructuredTool(
        name="get_customer_profile_tool",
        description="Get full customer profile including order history and tickets.",
        args_schema=GetCustomerProfileSchema,
        func=lambda **kwargs: call_mcp_tool("get_customer_profile_tool", **kwargs),
    )

    create_customer_tool = StructuredTool(
        name="create_customer_tool",
        description="Create a new customer record.",
        args_schema=CreateCustomerSchema,
        func=lambda **kwargs: call_mcp_tool("create_customer_tool", **kwargs),
    )

    # Ticket Tools
    create_ticket_tool = StructuredTool(
        name="create_ticket_tool",
        description="Create a new support ticket for a customer.",
        args_schema=CreateTicketSchema,
        func=lambda **kwargs: call_mcp_tool("create_ticket_tool", **kwargs),
    )

    update_ticket_tool = StructuredTool(
        name="update_ticket_tool",
        description="Update an existing support ticket.",
        args_schema=UpdateTicketSchema,
        func=lambda **kwargs: call_mcp_tool("update_ticket_tool", **kwargs),
    )

    get_ticket_tool = StructuredTool(
        name="get_ticket_tool",
        description="Retrieve details of a specific support ticket.",
        args_schema=GetTicketSchema,
        func=lambda **kwargs: call_mcp_tool("get_ticket_tool", **kwargs),
    )

    tools = [
        search_knowledge_base_tool,
        get_knowledge_base_by_category_tool,
        lookup_order_tool,
        get_order_status_tool,
        get_order_history_tool,
        lookup_customer_tool,
        get_customer_profile_tool,
        create_customer_tool,
        create_ticket_tool,
        update_ticket_tool,
        get_ticket_tool,
    ]
    logger.info(f"Created {len(tools)} MCP tool wrappers")
    return tools
