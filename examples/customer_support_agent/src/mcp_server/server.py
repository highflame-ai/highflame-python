"""FastMCP server with database tools."""

import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to import agent modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import warnings
# Suppress websockets deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn.protocols.websockets")

# Import database modules
from src.agent.database.setup import get_session, init_database
from src.agent.database.queries import (
    # Knowledge base
    search_knowledge_base,
    get_knowledge_base_by_category,
    # Orders
    get_order_by_number,
    get_orders_by_customer,
    # Customers
    get_customer_by_email,
    get_customer_by_id,
    get_customer_by_phone,
    create_customer as db_create_customer,
    # Tickets
    create_ticket as db_create_ticket,
    update_ticket as db_update_ticket,
    get_ticket_by_id,
)
from src.agent.database.models import TicketStatus, TicketPriority
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="customer-support-db-server",
    instructions="Database operations server for customer support agent",
)


# ============ Knowledge Base Tools ============


@mcp.tool()
def search_knowledge_base_tool(query: str, category: Optional[str] = None) -> str:
    """
    Search the knowledge base for information relevant to the customer's query.

    Args:
        query: The search query or keywords to search for
        category: Optional category to filter results (e.g., 'policies', 'shipping', 'account')

    Returns:
        A formatted string with relevant knowledge base articles, or a message if no results found.
    """
    logger.info(f"Searching knowledge base - query: {query}, category: {category}")
    db = get_session()
    try:
        articles = search_knowledge_base(db, query, category, limit=5)

        if not articles:
            logger.warning(f"No knowledge base articles found for query: {query}")
            return f"No knowledge base articles found for query: '{query}'"

        logger.info(f"Found {len(articles)} knowledge base articles")
        result = f"Found {len(articles)} relevant article(s):\n\n"
        for i, article in enumerate(articles, 1):
            result += f"{i}. **{article.title}**\n"
            result += f"   Category: {article.category or 'Uncategorized'}\n"
            result += f"   Content: {article.content[:200]}...\n"
            if article.tags:
                result += f"   Tags: {article.tags}\n"
            result += "\n"

        return result
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}", exc_info=True)
        return f"Error searching knowledge base: {str(e)}"
    finally:
        db.close()


@mcp.tool()
def get_knowledge_base_by_category_tool(category: str) -> str:
    """
    Get all knowledge base articles in a specific category.

    Args:
        category: The category to retrieve articles from (e.g., 'policies', 'shipping', 'account', 'orders', 'billing', 'support')

    Returns:
        A formatted string with all articles in the category.
    """
    db = get_session()
    try:
        articles = get_knowledge_base_by_category(db, category)

        if not articles:
            return f"No articles found in category: '{category}'"

        result = f"Found {len(articles)} article(s) in category '{category}':\n\n"
        for i, article in enumerate(articles, 1):
            result += f"{i}. **{article.title}**\n"
            result += f"   {article.content[:300]}...\n\n"

        return result
    except Exception as e:
        return f"Error retrieving knowledge base articles: {str(e)}"
    finally:
        db.close()


# ============ Order Tools ============


@mcp.tool()
def lookup_order_tool(order_number: str, customer_id: Optional[int] = None) -> str:
    """
    Look up order details by order number.

    Args:
        order_number: The order number to look up (e.g., 'ORD-001')
        customer_id: Optional customer ID to verify the order belongs to the customer

    Returns:
        A formatted string with order details, or an error message if not found.
    """
    db = get_session()
    try:
        order = get_order_by_number(db, order_number)
        if not order:
            return f"Error: Order '{order_number}' not found."

        # Verify customer if provided
        if customer_id and order.customer_id != customer_id:
            return f"Error: Order '{order_number}' does not belong to customer {customer_id}."

        customer = get_customer_by_id(db, order.customer_id)
        customer_name = customer.name if customer else "Unknown"

        return (
            f"Order Details:\n"
            f"Order Number: {order.order_number}\n"
            f"Status: {order.status.value}\n"
            f"Total: ${order.total:.2f}\n"
            f"Customer: {customer_name} (ID: {order.customer_id})\n"
            f"Order Date: {order.created_at}"
        )
    except Exception as e:
        return f"Error looking up order: {str(e)}"
    finally:
        db.close()


@mcp.tool()
def get_order_status_tool(order_number: str) -> str:
    """
    Get the current status of an order.

    Args:
        order_number: The order number to check

    Returns:
        The current status of the order.
    """
    db = get_session()
    try:
        order = get_order_by_number(db, order_number)
        if not order:
            return f"Error: Order '{order_number}' not found."

        return (
            f"Order {order_number} Status: {order.status.value}\n"
            f"Last Updated: {order.created_at}"
        )
    except Exception as e:
        return f"Error getting order status: {str(e)}"
    finally:
        db.close()


@mcp.tool()
def get_order_history_tool(customer_id: int) -> str:
    """
    Get all orders for a specific customer.

    Args:
        customer_id: The ID of the customer

    Returns:
        A formatted string with all orders for the customer.
    """
    db = get_session()
    try:
        customer = get_customer_by_id(db, customer_id)
        if not customer:
            return f"Error: Customer with ID {customer_id} not found."

        orders = get_orders_by_customer(db, customer_id)

        if not orders:
            return f"No orders found for customer {customer.name} (ID: {customer_id})."

        result = f"Order History for {customer.name}:\n\n"
        for i, order in enumerate(orders, 1):
            result += (
                f"{i}. Order {order.order_number}\n"
                f"   Status: {order.status.value}\n"
                f"   Total: ${order.total:.2f}\n"
                f"   Date: {order.created_at}\n\n"
            )

        return result
    except Exception as e:
        return f"Error getting order history: {str(e)}"
    finally:
        db.close()


# ============ Customer Tools ============


@mcp.tool()
def lookup_customer_tool(
    email: Optional[str] = None, phone: Optional[str] = None, customer_id: Optional[int] = None
) -> str:
    """
    Look up a customer by email, phone number, or customer ID.

    Args:
        email: Customer email address
        phone: Customer phone number
        customer_id: Customer ID

    Returns:
        Customer information if found, or an error message.
    """
    db = get_session()
    try:
        customer = None

        if customer_id:
            customer = get_customer_by_id(db, customer_id)
        elif email:
            customer = get_customer_by_email(db, email)
        elif phone:
            customer = get_customer_by_phone(db, phone)
        else:
            return "Error: Must provide at least one of: email, phone, or customer_id"

        if not customer:
            identifier = customer_id or email or phone
            return f"Error: Customer not found with identifier: {identifier}"

        return (
            f"Customer Information:\n"
            f"ID: {customer.id}\n"
            f"Name: {customer.name}\n"
            f"Email: {customer.email}\n"
            f"Phone: {customer.phone or 'Not provided'}\n"
            f"Member Since: {customer.created_at}"
        )
    except Exception as e:
        return f"Error looking up customer: {str(e)}"
    finally:
        db.close()


@mcp.tool()
def get_customer_profile_tool(customer_id: int) -> str:
    """
    Get full customer profile including order history and tickets.

    Args:
        customer_id: The ID of the customer

    Returns:
        A comprehensive customer profile with orders and tickets.
    """
    db = get_session()
    try:
        customer = get_customer_by_id(db, customer_id)
        if not customer:
            return f"Error: Customer with ID {customer_id} not found."

        orders = get_orders_by_customer(db, customer_id)
        tickets = customer.tickets

        result = (
            f"Customer Profile:\n"
            f"ID: {customer.id}\n"
            f"Name: {customer.name}\n"
            f"Email: {customer.email}\n"
            f"Phone: {customer.phone or 'Not provided'}\n"
            f"Member Since: {customer.created_at}\n\n"
        )

        # Add order summary
        result += f"Orders: {len(orders)} total\n"
        if orders:
            result += "Recent Orders:\n"
            for order in orders[:5]:  # Show last 5 orders
                result += f"  - {order.order_number}: {order.status.value} (${order.total:.2f})\n"

        result += "\n"

        # Add ticket summary
        result += f"Support Tickets: {len(tickets)} total\n"
        if tickets:
            result += "Recent Tickets:\n"
            for ticket in tickets[:5]:  # Show last 5 tickets
                result += f"  - Ticket #{ticket.id}: {ticket.subject} ({ticket.status.value})\n"

        return result
    except Exception as e:
        return f"Error retrieving customer profile: {str(e)}"
    finally:
        db.close()


@mcp.tool()
def create_customer_tool(name: str, email: str, phone: Optional[str] = None) -> str:
    """
    Create a new customer record.

    Args:
        name: Customer's full name
        email: Customer's email address
        phone: Optional phone number

    Returns:
        A confirmation message with the new customer ID and details.
    """
    db = get_session()
    try:
        # Check if customer already exists
        existing = get_customer_by_email(db, email)
        if existing:
            return f"Error: Customer with email '{email}' already exists (ID: {existing.id})"

        customer = db_create_customer(db, name, email, phone)

        return (
            f"Customer created successfully!\n"
            f"ID: {customer.id}\n"
            f"Name: {customer.name}\n"
            f"Email: {customer.email}\n"
            f"Phone: {customer.phone or 'Not provided'}"
        )
    except Exception as e:
        return f"Error creating customer: {str(e)}"
    finally:
        db.close()


# ============ Ticket Tools ============


@mcp.tool()
def create_ticket_tool(
    customer_id: int,
    subject: str,
    description: str,
    priority: str = "medium",
    order_id: Optional[int] = None,
) -> str:
    """
    Create a new support ticket for a customer.

    Args:
        customer_id: The ID of the customer creating the ticket
        subject: Brief subject line for the ticket
        description: Detailed description of the issue
        priority: Priority level - 'low', 'medium', 'high', or 'urgent' (default: 'medium')
        order_id: Optional order ID if the ticket is related to a specific order

    Returns:
        A confirmation message with the ticket ID and details.
    """
    db = get_session()
    try:
        # Validate customer exists
        customer = get_customer_by_id(db, customer_id)
        if not customer:
            return f"Error: Customer with ID {customer_id} not found."

        # Map priority string to enum
        priority_map = {
            "low": TicketPriority.LOW,
            "medium": TicketPriority.MEDIUM,
            "high": TicketPriority.HIGH,
            "urgent": TicketPriority.URGENT,
        }
        priority_enum = priority_map.get(priority.lower(), TicketPriority.MEDIUM)

        ticket = db_create_ticket(db, customer_id, subject, description, priority_enum, order_id)

        return (
            f"Support ticket created successfully!\n"
            f"Ticket ID: {ticket.id}\n"
            f"Subject: {ticket.subject}\n"
            f"Priority: {ticket.priority.value}\n"
            f"Status: {ticket.status.value}\n"
            f"Created: {ticket.created_at}"
        )
    except Exception as e:
        return f"Error creating ticket: {str(e)}"
    finally:
        db.close()


@mcp.tool()
def update_ticket_tool(
    ticket_id: int, status: Optional[str] = None, notes: Optional[str] = None
) -> str:
    """
    Update an existing support ticket.

    Args:
        ticket_id: The ID of the ticket to update
        status: New status - 'open', 'in_progress', 'resolved', or 'closed'
        notes: Additional notes or updates to add to the ticket

    Returns:
        A confirmation message with updated ticket details.
    """
    db = get_session()
    try:
        ticket = get_ticket_by_id(db, ticket_id)
        if not ticket:
            return f"Error: Ticket with ID {ticket_id} not found."

        # Map status string to enum
        status_enum = None
        if status:
            status_map = {
                "open": TicketStatus.OPEN,
                "in_progress": TicketStatus.IN_PROGRESS,
                "resolved": TicketStatus.RESOLVED,
                "closed": TicketStatus.CLOSED,
            }
            status_enum = status_map.get(status.lower())
            if not status_enum:
                return f"Error: Invalid status '{status}'. Valid values: open, in_progress, resolved, closed"

        updated_ticket = db_update_ticket(db, ticket_id, status_enum, notes)

        if not updated_ticket:
            return f"Error: Failed to update ticket {ticket_id}"

        return (
            f"Ticket updated successfully!\n"
            f"Ticket ID: {updated_ticket.id}\n"
            f"Subject: {updated_ticket.subject}\n"
            f"Status: {updated_ticket.status.value}\n"
            f"Priority: {updated_ticket.priority.value}\n"
            f"Last Updated: {updated_ticket.updated_at}"
        )
    except Exception as e:
        return f"Error updating ticket: {str(e)}"
    finally:
        db.close()


@mcp.tool()
def get_ticket_tool(ticket_id: int) -> str:
    """
    Retrieve details of a specific support ticket.

    Args:
        ticket_id: The ID of the ticket to retrieve

    Returns:
        A formatted string with ticket details.
    """
    db = get_session()
    try:
        ticket = get_ticket_by_id(db, ticket_id)
        if not ticket:
            return f"Error: Ticket with ID {ticket_id} not found."

        customer = get_customer_by_id(db, ticket.customer_id)
        customer_name = customer.name if customer else "Unknown"

        result = (
            f"Ticket Details:\n"
            f"ID: {ticket.id}\n"
            f"Subject: {ticket.subject}\n"
            f"Description: {ticket.description}\n"
            f"Status: {ticket.status.value}\n"
            f"Priority: {ticket.priority.value}\n"
            f"Customer: {customer_name} (ID: {ticket.customer_id})\n"
        )

        if ticket.order_id:
            result += f"Related Order ID: {ticket.order_id}\n"

        result += f"Created: {ticket.created_at}\n" f"Last Updated: {ticket.updated_at}"

        return result
    except Exception as e:
        return f"Error retrieving ticket: {str(e)}"
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database before starting server
    logger.info("Initializing database...")
    try:
        init_database(seed_data=True)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        logger.warning("Server will continue, but database operations may fail")

    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "9000"))
    logger.info(f"Starting MCP server on {host}:{port}")
    logger.info("Using streamable-http transport for HTTP access")
    logger.info(f"Server will be available at: http://{host}:{port}/mcp/")
    try:
        mcp.run(transport="streamable-http", host=host, port=port)
    except Exception as e:
        logger.error(f"Error starting MCP server: {e}", exc_info=True)
        raise
