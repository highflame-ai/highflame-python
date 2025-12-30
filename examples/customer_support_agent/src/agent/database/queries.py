"""Database query helper functions."""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .models import (
    Customer,
    Order,
    Ticket,
    KnowledgeBase,
    Conversation,
    TicketStatus,
    TicketPriority,
    OrderStatus,
)


def get_customer_by_email(db: Session, email: str) -> Optional[Customer]:
    """Get customer by email."""
    return db.query(Customer).filter(Customer.email == email).first()


def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
    """Get customer by ID."""
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customer_by_phone(db: Session, phone: str) -> Optional[Customer]:
    """Get customer by phone number."""
    return db.query(Customer).filter(Customer.phone == phone).first()


def create_customer(
    db: Session, name: str, email: str, phone: Optional[str] = None
) -> Customer:
    """Create a new customer."""
    customer = Customer(name=name, email=email, phone=phone)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_order_by_number(db: Session, order_number: str) -> Optional[Order]:
    """Get order by order number."""
    return db.query(Order).filter(Order.order_number == order_number).first()


def get_orders_by_customer(db: Session, customer_id: int) -> List[Order]:
    """Get all orders for a customer."""
    return db.query(Order).filter(Order.customer_id == customer_id).all()


def create_order(
    db: Session,
    customer_id: int,
    order_number: str,
    total: float,
    status: OrderStatus = OrderStatus.PENDING,
) -> Order:
    """Create a new order."""
    order = Order(
        customer_id=customer_id,
        order_number=order_number,
        total=total,
        status=status,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
    """Get ticket by ID."""
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def create_ticket(
    db: Session,
    customer_id: int,
    subject: str,
    description: str,
    priority: TicketPriority = TicketPriority.MEDIUM,
    order_id: Optional[int] = None,
) -> Ticket:
    """Create a new support ticket."""
    ticket = Ticket(
        customer_id=customer_id,
        order_id=order_id,
        subject=subject,
        description=description,
        priority=priority,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket(
    db: Session,
    ticket_id: int,
    status: Optional[TicketStatus] = None,
    notes: Optional[str] = None,
) -> Optional[Ticket]:
    """Update ticket status and add notes."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        return None

    if status:
        ticket.status = status
    if notes:
        # Append notes to description
        ticket.description += f"\n\n[Update]: {notes}"

    from datetime import datetime

    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket


def search_knowledge_base(
    db: Session,
    query: str,
    category: Optional[str] = None,
    limit: int = 5,
) -> List[KnowledgeBase]:
    """Search knowledge base by keyword matching in title and content."""
    search_filter = or_(
        KnowledgeBase.title.ilike(f"%{query}%"),
        KnowledgeBase.content.ilike(f"%{query}%"),
        KnowledgeBase.tags.ilike(f"%{query}%"),
    )

    if category:
        search_filter = search_filter & (KnowledgeBase.category == category)

    return db.query(KnowledgeBase).filter(search_filter).limit(limit).all()


def get_knowledge_base_by_category(db: Session, category: str) -> List[KnowledgeBase]:
    """Get all knowledge base articles in a category."""
    return db.query(KnowledgeBase).filter(KnowledgeBase.category == category).all()


def create_conversation(
    db: Session, messages: List[dict], customer_id: Optional[int] = None
) -> Conversation:
    """Create a new conversation."""
    conversation = Conversation(customer_id=customer_id, messages=messages)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def update_conversation(
    db: Session,
    conversation_id: int,
    messages: List[dict],
) -> Optional[Conversation]:
    """Update conversation messages."""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        return None

    conversation.messages = messages
    from datetime import datetime

    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    return conversation
