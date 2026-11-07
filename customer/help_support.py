
import base64
from pathlib import Path
from textwrap import dedent

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent

WELCOME_BACKGROUND = (
    PROJECT_ROOT / "assets" / "backgrounds" / "login_background.png"
)


def _welcome_background_css():
    """Load the faded printing-pattern background."""

    if not WELCOME_BACKGROUND.is_file():
        return "background-color: #E3F1E7;"

    encoded = base64.b64encode(
        WELCOME_BACKGROUND.read_bytes()
    ).decode("ascii")

    return (
        "background-image: "
        "linear-gradient(rgba(227,241,231,0.88), "
        "rgba(227,241,231,0.88)), "
        f"url('data:image/png;base64,{encoded}');"
        "background-size: cover;"
        "background-position: center;"
    )


def _render_header():
    """Render the Help and Support page header."""

    background = _welcome_background_css()

    header_html = dedent(f"""
        <div style="
            {background}
            background-repeat: no-repeat;
            border: 1px solid #D0E6D5;
            border-radius: 16px;
            padding: 25px 28px;
            margin-bottom: 22px;
            min-height: 130px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h1 style="
                color: #064B36;
                font-size: 1.8rem;
                margin: 0 0 6px 0;
            ">How can we help you?</h1>
            <div style="
                color: #426A53;
                font-size: 0.95rem;
                margin: 0;
            ">
                Find answers to common questions or get assistance
                with your printing orders.
            </div>
        </div>
    """)

    st.markdown(header_html, unsafe_allow_html=True)


def _render_faqs():
    """Render frequently asked questions."""

    st.markdown("### Frequently Asked Questions")

    faqs = [
        (
            "How do I place a printing order?",
            "Go to New Order, upload your document, select your "
            "printing preferences, and submit your order."
        ),
        (
            "How can I check my order status?",
            "Visit My Orders to see the progress of your printing "
            "requests and check their current status."
        ),
        (
            "Can I download my uploaded documents?",
            "Yes! Visit Saved Files to preview or download "
            "the documents you have uploaded."
        ),
        (
            "Can I cancel my printing order?",
            "For assistance with cancelling an order, please "
            "contact PasaPrint support."
        ),
        (
            "What file formats can I upload?",
            "Please refer to the supported file types shown "
            "when uploading a document in New Order."
        ),
        (
            "What should I do if my order has a problem?",
            "Contact our support team or use the support request "
            "form once it becomes available."
        ),
    ]

    for question, answer in faqs:
        with st.expander(question):
            st.write(answer)


def _render_contact_support():
    """Render contact information and support request placeholder."""

    st.markdown("### Still need help?")

    contact_html = dedent("""
        <div style="
            background: #F1F7F2;
            border: 1px solid #E1ECE4;
            border-radius: 12px;
            padding: 16px 18px;
            margin-bottom: 12px;
        ">
            <div style="
                color: #064B36;
                font-size: 1rem;
                font-weight: 700;
                margin-bottom: 8px;
            ">
                ✉ Contact Support
            </div>
            <div style="
                color: #648477;
                font-size: 0.9rem;
                line-height: 1.6;
            ">
                Need assistance with your printing order?
                Contact the PasaPrint support team for help.
            </div>
            <div style="
                color: #286A4B;
                font-size: 0.85rem;
                margin-top: 10px;
            ">
                Support contact details will be available soon.
            </div>
        </div>
    """)

    st.markdown(contact_html, unsafe_allow_html=True)

    form_html = dedent("""
        <div style="
            background: #F1F7F2;
            border: 1px solid #E1ECE4;
            border-radius: 12px;
            padding: 16px 18px;
        ">
            <div style="
                color: #064B36;
                font-size: 1rem;
                font-weight: 700;
                margin-bottom: 8px;
            ">
                📝 Support Request Form
            </div>
            <div style="
                color: #648477;
                font-size: 0.9rem;
                line-height: 1.6;
            ">
                Have a concern or encountered a problem?
                Submit a support request so our team can assist you.
            </div>
            <span style="
                display: inline-block;
                background: #D5F0DD;
                color: #168447;
                font-size: 0.75rem;
                font-weight: 700;
                padding: 4px 10px;
                border-radius: 20px;
                margin-top: 10px;
            ">
                Google Form coming soon
            </span>
        </div>
    """)

    st.markdown(form_html, unsafe_allow_html=True)


def render_help_support_page(user):
    """Render the customer's Help and Support page."""

    _render_header()
    _render_faqs()
    _render_contact_support()
