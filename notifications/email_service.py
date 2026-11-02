import smtplib
import streamlit as st

from email.message import EmailMessage
from database.connection import get_connection


def _send_email(message):
    """Send an email using the configured PasaPrint Gmail account."""

    sender_email = st.secrets["email"]["sender_email"]
    app_password = st.secrets["email"]["app_password"]

    message["From"] = sender_email

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, app_password)
        server.send_message(message)


def send_welcome_email(to_email, username, role="customer"):
    """Send a welcome email after successful account registration."""

    message = EmailMessage()
    message["Subject"] = "Welcome to PasaPrint! 💚"
    message["To"] = to_email

    message.set_content(
        f"""Hi {username}!

Welcome to PasaPrint! 💚

Your account has been successfully created.

You can now use PasaPrint to submit your printing files,
customize your printing preferences, and track your orders.

Account type: {role.title()}

Thank you for choosing PasaPrint!

Happy printing,
The PasaPrint Team
"""
    )

    _send_email(message)


def send_staff_authorization_email(to_email, authorization_code):
    """Email a staff registration authorization code."""

    message = EmailMessage()
    message["Subject"] = "PasaPrint Staff Registration Invitation 💚"
    message["To"] = to_email

    message.set_content(
        f"""Hello!

You have been invited to register as a Printing Staff member
of PasaPrint. 💚

Use the authorization code below to create your account:

{authorization_code}

IMPORTANT:
- This code is assigned specifically to your email address.
- It can only be used once.
- It expires after 24 hours.
- Do not share this code with anyone else.

To register, open PasaPrint and select "Printing Staff"
under the account creation page.

We look forward to having you on the team!

Best regards,
The PasaPrint Team
"""
    )

    _send_email(message)


def send_staff_access_request_email(applicant_email):
    """Notify the active manager about a staff access request."""

    with get_connection() as connection:
        manager = connection.execute(
            """
            SELECT email, username
            FROM users
            WHERE role = 'manager'
              AND account_status = 'active'
            ORDER BY user_id
            LIMIT 1
            """
        ).fetchone()

    if manager is None:
        raise ValueError("No active manager account was found.")

    message = EmailMessage()
    message["Subject"] = "PasaPrint Staff Access Request"
    message["To"] = manager["email"]

    message.set_content(
        f"""Hello {manager["username"]},

A new Printing Staff access request has been submitted.

Applicant Email: {applicant_email}

Please review this request.

If you approve the applicant, run generate_staff_code.py
and enter the applicant's email address to issue their
registration authorization code.

Best regards,
PasaPrint
"""
    )

    _send_email(message)


def send_password_reset_email(to_email, reset_code):
    """Send a one-time password reset code."""

    message = EmailMessage()
    message["Subject"] = "PasaPrint Password Reset Code"
    message["To"] = to_email

    message.set_content(
        f"""Hello!

We received a request to reset the password for your PasaPrint account.

Your 6-digit password reset code is:

{reset_code}

IMPORTANT:
- This code expires in 10 minutes.
- It can only be used once.
- You have a maximum of 5 attempts.
- If you did not request this reset, you can ignore this email.

For your security, do not share this code with anyone.

Best regards,
The PasaPrint Team
"""
    )

    _send_email(message)


def send_notification_email(to_email, subject, title, body, order_number=None):
    """Send an order-related notification email."""
    sender_email = st.secrets["email"]["sender_email"]
    app_password = st.secrets["email"]["app_password"]

    order_line = f"Order: {order_number}\\n\\n" if order_number else ""
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email
    message.set_content(
        f"""Hello!

{title}

{body}

{order_line}You can sign in to PasaPrint to view the latest details.

PasaPrint Team
"""
    )

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, app_password)
        server.send_message(message)
