
from contextlib import contextmanager
from html import escape

import streamlit as st


@contextmanager
def show_loader(
    message="Loading...",
    subtitle="Please wait while we prepare everything."
):
    """Display a reusable full-screen PasaPrint loading overlay."""

    loader_placeholder = st.empty()

    safe_message = escape(str(message))
    safe_subtitle = escape(str(subtitle))

    loader_placeholder.markdown(
        f"""
        <style>
        .pp-loader-overlay {{
            position: fixed;
            inset: 0;
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(241, 248, 243, 0.97);
            backdrop-filter: blur(5px);
        }}

        .pp-loader-content {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 12px;
            padding: 30px;
        }}

        .pp-loader-spinner {{
            width: 48px;
            height: 48px;
            border: 5px solid #D9E9DC;
            border-top-color: #064B36;
            border-radius: 50%;
            animation: ppLoaderSpin 0.8s linear infinite;
        }}

        .pp-loader-message {{
            color: #064B36;
            font-size: 1.2rem;
            font-weight: 750;
        }}

        .pp-loader-subtitle {{
            color: #668373;
            font-size: 0.88rem;
        }}

        @keyframes ppLoaderSpin {{
            to {{ transform: rotate(360deg); }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            .pp-loader-spinner {{
                animation: none;
            }}
        }}
        </style>

        <div class="pp-loader-overlay">
            <div class="pp-loader-content">
                <div class="pp-loader-spinner"></div>
                <div class="pp-loader-message">{safe_message}</div>
                <div class="pp-loader-subtitle">{safe_subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        yield
    finally:
        loader_placeholder.empty()
