"""Database setup and initialization."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import (
    Base,
    Customer,
    KnowledgeBase,
    OrderStatus,
    TicketPriority,
)
from .queries import create_customer, create_order, create_ticket
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_database_path() -> str:
    """Get database path from environment or use default."""
    path = os.getenv("DATABASE_PATH", "./src/db/support_agent.db")
    logger.debug(f"Database path: {path}")
    return path


def get_engine():
    """Create SQLAlchemy engine."""
    database_path = get_database_path()
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(database_path)) or ".", exist_ok=True)
    logger.debug(f"Creating database engine for: {database_path}")
    return create_engine(f"sqlite:///{database_path}", echo=False)


def get_session():
    """Create database session."""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def init_database(seed_data: bool = True):
    """Initialize database with tables and optionally seed with sample data."""
    logger.info("Initializing database")
    engine = get_engine()

    # Create all tables
    logger.debug("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

    if seed_data:
        logger.debug("Seeding database with sample data")
        seed_database()


def seed_database():
    """Seed database with sample data for testing."""
    db = get_session()

    try:
        # Check if data already exists
        customer_count = db.query(Customer).count()
        if customer_count > 0:
            logger.info(
                f"Database already contains {customer_count} customers. "
                "Skipping seed."
            )
            return

        logger.info("Seeding database with sample data")

        # Create sample customers
        customers_data = [
            ("John Doe", "john.doe@example.com", "+1-555-0101"),
            ("Jane Smith", "jane.smith@example.com", "+1-555-0102"),
            ("Bob Johnson", "bob.johnson@example.com", "+1-555-0103"),
            ("Alice Williams", "alice.williams@example.com", "+1-555-0104"),
            ("Charlie Brown", "charlie.brown@example.com", "+1-555-0105"),
            ("Diana Prince", "diana.prince@example.com", "+1-555-0106"),
            ("Edward Norton", "edward.norton@example.com", "+1-555-0107"),
            ("Fiona Apple", "fiona.apple@example.com", "+1-555-0108"),
            ("George Lucas", "george.lucas@example.com", "+1-555-0109"),
            ("Helen Mirren", "helen.mirren@example.com", "+1-555-0110"),
        ]

        customers = []
        for name, email, phone in customers_data:
            customers.append(create_customer(db, name, email, phone))

        customer1, customer2, customer3 = customers[0], customers[1], customers[2]

        # Create sample orders
        orders_data = [
            (customer1.id, "ORD-001", 99.99, OrderStatus.SHIPPED),
            (customer1.id, "ORD-002", 149.50, OrderStatus.PROCESSING),
            (customer1.id, "ORD-003", 79.99, OrderStatus.DELIVERED),
            (customer2.id, "ORD-004", 199.99, OrderStatus.SHIPPED),
            (customer2.id, "ORD-005", 299.50, OrderStatus.PROCESSING),
            (customer3.id, "ORD-006", 49.99, OrderStatus.DELIVERED),
            (customer3.id, "ORD-007", 89.99, OrderStatus.CANCELLED),
            (customers[3].id, "ORD-008", 159.99, OrderStatus.SHIPPED),
            (customers[4].id, "ORD-009", 249.99, OrderStatus.PROCESSING),
            (customers[5].id, "ORD-010", 179.99, OrderStatus.DELIVERED),
            (customers[6].id, "ORD-011", 129.99, OrderStatus.SHIPPED),
            (customers[7].id, "ORD-012", 349.99, OrderStatus.PROCESSING),
            (customers[8].id, "ORD-013", 99.99, OrderStatus.RETURNED),
            (customers[9].id, "ORD-014", 219.99, OrderStatus.DELIVERED),
        ]

        orders = []
        for customer_id, order_num, total, status in orders_data:
            orders.append(create_order(db, customer_id, order_num, total, status))

        order1 = orders[0]

        # Create sample tickets
        tickets_data = [
            (
                customer1.id,
                "Order not received",
                "I placed order ORD-001 two weeks ago but haven't received it yet.",
                TicketPriority.HIGH,
                order1.id,
            ),
            (
                customer2.id,
                "Product question",
                "What is the return policy for electronics?",
                TicketPriority.MEDIUM,
                None,
            ),
            (
                customer3.id,
                "Billing issue",
                "I was charged twice for order ORD-006. Please refund one charge.",
                TicketPriority.URGENT,
                orders[5].id,
            ),
            (
                customers[3].id,
                "Technical support",
                "The product I received is not working. It won't turn on.",
                TicketPriority.HIGH,
                orders[7].id,
            ),
            (
                customers[4].id,
                "Shipping delay",
                (
                    "My order ORD-009 was supposed to arrive yesterday but "
                    "hasn't shown up."
                ),
                TicketPriority.MEDIUM,
                orders[8].id,
            ),
            (
                customers[5].id,
                "Return request",
                "I want to return order ORD-010. The item doesn't fit.",
                TicketPriority.LOW,
                orders[9].id,
            ),
            (
                customers[6].id,
                "Account question",
                "How do I change my email address?",
                TicketPriority.LOW,
                None,
            ),
            (
                customers[7].id,
                "Payment failed",
                "My payment for order ORD-012 failed. Can you help?",
                TicketPriority.HIGH,
                orders[11].id,
            ),
            (
                customers[8].id,
                "Refund status",
                "I returned order ORD-013 last week. When will I get my refund?",
                TicketPriority.MEDIUM,
                orders[12].id,
            ),
            (
                customers[9].id,
                "Product inquiry",
                "Do you have this product in a different color?",
                TicketPriority.LOW,
                None,
            ),
        ]

        tickets = []
        for customer_id, subject, desc, priority, order_id in tickets_data:
            tickets.append(
                create_ticket(db, customer_id, subject, desc, priority, order_id)
            )

        # Create sample knowledge base articles
        kb_articles = [
            KnowledgeBase(
                title="Return Policy",
                content=(
                    "Our return policy allows returns within 30 days of purchase. "
                    "Items must be in original condition with tags attached. "
                    "Electronics can be returned for a full refund or exchange. "
                    "To initiate a return, log into your account and go to the "
                    "Orders section, then click 'Return' next to the item you "
                    "wish to return."
                ),
                category="policies",
                tags="returns,refund,policy,exchange",
            ),
            KnowledgeBase(
                title="Shipping Information",
                content=(
                    "Standard shipping takes 5-7 business days. Express shipping "
                    "(2-3 days) and overnight shipping are available at checkout. "
                    "You will receive a tracking number via email once your order "
                    "ships. International shipping is available to most countries "
                    "with delivery times of 10-21 business days."
                ),
                category="shipping",
                tags="shipping,delivery,tracking,international",
            ),
            KnowledgeBase(
                title="Account Management",
                content=(
                    "You can manage your account by logging in at our website. "
                    "From there you can view order history, update your address, "
                    "change your password, and manage payment methods. To update "
                    "your email, go to Account Settings > Profile Information."
                ),
                category="account",
                tags="account,login,profile,settings",
            ),
            KnowledgeBase(
                title="Order Tracking",
                content=(
                    "To track your order, use the order number provided in your "
                    "confirmation email. You can also log into your account to "
                    "see all order statuses and tracking information. If your "
                    "order shows as 'Shipped', click on the tracking number to "
                    "see real-time updates from the carrier."
                ),
                category="orders",
                tags="tracking,order,status,delivery",
            ),
            KnowledgeBase(
                title="Payment Methods",
                content=(
                    "We accept all major credit cards (Visa, MasterCard, "
                    "American Express), PayPal, and Apple Pay. All payments are "
                    "processed securely. We do not store your full credit card "
                    "information. For security, we use SSL encryption for all "
                    "transactions."
                ),
                category="billing",
                tags="payment,credit card,paypal,security",
            ),
            KnowledgeBase(
                title="Technical Support",
                content=(
                    "For technical issues with products, please check the "
                    "troubleshooting guide in the product manual. If the issue "
                    "persists, contact our technical support team with your order "
                    "number and a description of the problem. Our support team "
                    "is available Monday-Friday, 9 AM - 6 PM EST."
                ),
                category="support",
                tags="technical,troubleshooting,help,contact",
            ),
            KnowledgeBase(
                title="Refund Processing",
                content=(
                    "Refunds are typically processed within 5-7 business days "
                    "after we receive your returned item. The refund will be "
                    "issued to the original payment method. You will receive an "
                    "email confirmation once the refund has been processed. For "
                    "credit cards, it may take an additional 3-5 business days "
                    "to appear on your statement."
                ),
                category="billing",
                tags="refund,return,payment,processing",
            ),
            KnowledgeBase(
                title="Order Cancellation",
                content=(
                    "You can cancel an order within 24 hours of placing it if "
                    "it hasn't shipped yet. To cancel, go to your Orders page "
                    "and click 'Cancel Order'. If your order has already shipped, "
                    "you'll need to return it using our standard return process. "
                    "Cancelled orders are refunded immediately."
                ),
                category="orders",
                tags="cancel,order,refund,policy",
            ),
            KnowledgeBase(
                title="Product Warranty",
                content=(
                    "All products come with a manufacturer's warranty. "
                    "Electronics typically have a 1-year warranty covering "
                    "defects in materials and workmanship. Warranty claims must "
                    "be made within the warranty period and require proof of "
                    "purchase. Contact support with your order number to "
                    "initiate a warranty claim."
                ),
                category="support",
                tags="warranty,electronics,defect,claim",
            ),
            KnowledgeBase(
                title="Gift Cards and Promo Codes",
                content=(
                    "Gift cards can be applied at checkout by entering the code "
                    "in the 'Promo Code' field. Gift cards never expire and can "
                    "be used for any purchase. Promo codes are case-sensitive "
                    "and may have expiration dates or minimum purchase "
                    "requirements. Only one promo code can be used per order."
                ),
                category="billing",
                tags="gift card,promo code,discount,coupon",
            ),
            KnowledgeBase(
                title="Shipping Address Changes",
                content=(
                    "You can change your shipping address for an order if it "
                    "hasn't shipped yet. Log into your account, go to Orders, "
                    "and click 'Change Address' next to the order. Once an "
                    "order has shipped, address changes must be made directly "
                    "with the carrier using your tracking number."
                ),
                category="orders",
                tags="address,shipping,change,update",
            ),
            KnowledgeBase(
                title="Damaged or Defective Items",
                content=(
                    "If you receive a damaged or defective item, please contact "
                    "us within 48 hours of delivery. We'll arrange for a "
                    "replacement or full refund at no cost to you. Please "
                    "include photos of the damage when contacting support. We "
                    "may request that you return the item for inspection."
                ),
                category="support",
                tags="damaged,defective,replacement,refund",
            ),
        ]

        for article in kb_articles:
            db.add(article)

        db.commit()
        logger.info(
            f"Database seeded successfully: {len(customers)} customers, "
            f"{len(orders)} orders, {len(tickets)} tickets, "
            f"{len(kb_articles)} KB articles"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database when run directly
    init_database(seed_data=True)
