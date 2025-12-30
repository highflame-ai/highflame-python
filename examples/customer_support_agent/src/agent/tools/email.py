"""Email sending tool."""

from langchain_core.tools import tool
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


def send_email_smtp(
    to_email: str,
    subject: str,
    body: str,
    smtp_server: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_username: Optional[str] = None,
    smtp_password: Optional[str] = None,
    from_email: Optional[str] = None,
) -> bool:
    """Send email using SMTP."""
    smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
    smtp_username = smtp_username or os.getenv("SMTP_USERNAME")
    smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
    from_email = from_email or os.getenv("EMAIL_FROM") or smtp_username

    if not smtp_username or not smtp_password:
        raise ValueError(
            "SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD in .env"
        )

    try:
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        return True
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")


@tool
def send_email_tool(to: str, subject: str, body: str) -> str:
    """
    Send an email notification to a customer.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content

    Returns:
        Confirmation message if email was sent successfully, or an error message.
    """
    try:
        send_email_smtp(to, subject, body)
        return f"Email sent successfully to {to}\n" f"Subject: {subject}"
    except ValueError as e:
        return (
            f"Email configuration error: {str(e)}\n"
            "Please configure SMTP settings in your .env file:\n"
            "- SMTP_SERVER\n"
            "- SMTP_PORT\n"
            "- SMTP_USERNAME\n"
            "- SMTP_PASSWORD\n"
            "- EMAIL_FROM"
        )
    except Exception as e:
        return f"Error sending email: {str(e)}"
