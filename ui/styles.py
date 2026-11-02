import base64
from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
BACKGROUND_PATH = BASE_DIR / "assets" / "backgrounds" / "login_background.png"


def load_styles():
    """Apply shared responsive styling to PasaPrint authentication pages."""
    background_css = "none"
    if BACKGROUND_PATH.is_file():
        encoded = base64.b64encode(BACKGROUND_PATH.read_bytes()).decode("ascii")
        background_css = (
            "linear-gradient(rgba(217, 233, 220, .56), "
            "rgba(217, 233, 220, .56)), "
            f"url('data:image/png;base64,{encoded}')"
        )

    st.markdown(
        f"""
        <style>
        :root {{
            --pp-dark: #173D2B;
            --pp-green: #286B46;
            --pp-pale: #F1F8F3;
            --pp-soft: #D9E9DC;
            --pp-border: #B8D7BE;
            --pp-muted: #66756B;
        }}

        html, body {{ margin: 0; padding: 0; overflow-x: hidden; }}
        .stApp {{ color: var(--pp-dark); background: var(--pp-pale); }}
        [data-testid="stAppViewContainer"] {{
            min-height: 100vh;
            background-color: var(--pp-pale);
            background-image: {background_css};
            background-repeat: repeat;
            background-size: 380px auto;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stToolbar"], footer {{ visibility: hidden; }}
        .block-container {{
            width: 100%; max-width: 1450px; margin: 0 auto !important;
            padding: 3rem 1.5rem 2rem !important; box-sizing: border-box;
            background: transparent !important;
        }}

        /* Keep Streamlit images centered without changing their aspect ratio. */
        [data-testid="stImage"] {{
            width: 100%; display: flex; justify-content: center;
            align-items: center; padding: 0; box-sizing: border-box;
        }}
        [data-testid="stImage"] > div {{
            width: 100%; display: flex; justify-content: center;
            align-items: center; padding: 0; box-sizing: border-box;
        }}
        [data-testid="stImage"] img {{
            display: block; max-width: 100%; height: auto;
            margin: 0 auto; object-fit: contain;
        }}

        /* Sign-in card */
        .st-key-login-card {{
            width: 100% !important;
            max-width: 600px !important;
            margin: 2rem auto 0 !important;
            padding: 1.75rem !important;
            box-sizing: border-box !important;
            background: #fff !important;
            border: 1px solid #edf2ee !important;
            border-radius: 20px !important;
            box-shadow: 0 10px 30px rgba(23, 61, 43, .12) !important;
        }}
        .st-key-login-card [data-testid="stVerticalBlock"] {{
            width: 100% !important;
            max-width: 100% !important;
            gap: 1rem !important;
            box-sizing: border-box !important;
            background: #fff !important;
        }}
        .st-key-login-card [data-testid="stForm"] {{
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            margin: 0 !important;
            padding: 1.25rem !important;
            box-sizing: border-box !important;
            background: #fff !important;
            border: 1px solid #e4ece5 !important;
            border-radius: 15px !important;
            box-shadow: none !important;
        }}
        .st-key-login-card [data-testid="stForm"] [data-testid="stVerticalBlock"],
        .st-key-login-card [data-testid="stForm"] [data-testid="stTextInput"] {{
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            box-sizing: border-box !important;
        }}

       .st-key-login-card [data-testid="stImage"] {{
            width: 100% !important;
            padding-left: 2.5rem;
        }}

        .login-heading {{
            color: var(--pp-green); font-size: 2rem; font-weight: 800;
            line-height: 1.2; text-align: center; margin: .15rem 0 0;
        }}
        .login-subheading {{
            color: var(--pp-muted); font-size: .9rem; text-align: center;
            max-width: 100%; margin: 0 auto .75rem;
        }}
        .login-footer {{
            color: var(--pp-green); font-size: .85rem; text-align: center;
            margin: .6rem 0 0; font-weight: 500;
        }}

    /* Registration: equal-height panels on desktop */
        [data-testid="stHorizontalBlock"]:has(.st-key-register-left-panel) {{
            align-items: stretch !important;
            gap: 1rem !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.st-key-register-left-panel) > [data-testid="column"] {{
            display: flex !important;
            align-items: stretch !important;
            min-width: 0 !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.st-key-register-left-panel) > [data-testid="column"] > div {{
            width: 100% !important;
            min-width: 0 !important;
            box-sizing: border-box !important;
        }}

        .st-key-register-left-panel,
        .st-key-register-right-panel {{
            width: 100% !important;
            min-width: 0 !important;
            min-height: 740px !important;
            height: 100% !important;
            box-sizing: border-box !important;
            border-radius: 19px !important;
        }}

        
        /* Left information panel */
        .st-key-register-left-panel {{
            display: flex !important;
            flex-direction: column !important;
            align-items: stretch !important;
            padding: 2rem 4rem !important;
            background: var(--pp-soft) !important;
            border: 1px solid rgba(40, 107, 70, .08) !important;
            box-sizing: border-box !important;
        }}

        .st-key-register-left-panel > div,
        .st-key-register-left-panel [data-testid="stVerticalBlock"] {{
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            box-sizing: border-box !important;
            background: var(--pp-soft) !important;
        }}

        /* Centered, smaller PasaPrint logo */
        .st-key-register-logo {{
            width: 100% !important;
            margin: 0 auto .5rem !important;
            background: transparent !important;
            align-items: center;
        }}

        .st-key-register-logo [data-testid="stImage"] {{
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 auto !important;
        }}

        .st-key-register-logo [data-testid="stImage"] img {{
            display: block !important;
            width: 200px !important;
            max-width: 100% !important;
            height: auto !important;
            margin: 0 auto !important;
            object-fit: contain !important;
        }}

        /* Printer illustration below the logo */
        .st-key-register-illustration {{
            width: 100% !important;
            margin: 3rem 0 !important;
            background: transparent !important;
            justify-content: center;
            margin: auto;
        }}

        .st-key-register-illustration [data-testid="stImage"] {{
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 auto !important;
        }}

        .st-key-register-illustration [data-testid="stImage"] img {{
            display: block !important;
            width: 320px !important;
            max-width: 100% !important;
            height: auto !important;
            margin: 0 auto !important;
            object-fit: contain !important;
        }}

        /* Benefit rows */
        [class*="st-key-register-benefit-"] {{
            width: 100% !important;
            margin: 0 0 2rem !important;
            background: transparent !important;
        }}

        /* Horizontal spacing between icon and text */
        [class*="st-key-register-benefit-"] [data-testid="stHorizontalBlock"] {{
            align-items: center !important;
            gap: 0.5rem !important;
        }}

        [class*="st-key-register-benefit-"] [data-testid="column"] {{
            min-width: 0 !important;
            padding: 0 !important;
        }}

        /* Icon container */
        [class*="st-key-register-benefit-"] [data-testid="column"]:first-child [data-testid="stImage"] {{
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            padding: 0 !important;
            margin: 0 !important;
        }}

        /* Actual feature icon size */
        [class*="st-key-register-benefit-"] [data-testid="column"]:first-child [data-testid="stImage"] img {{
            display: block !important;
            width: 48px !important;
            max-width: 48px !important;
            height: auto !important;
            margin: 0 auto !important;
            object-fit: contain !important;
        }}

        .benefit-title {{
            color: var(--pp-green) !important;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            margin: 0 0 .2rem !important;
        }}

        .benefit-description {{
            color: var(--pp-muted) !important;
            font-size: .98rem !important;
            line-height: 1.45 !important;
            margin: 0 !important;
        }}

        /* Right registration form panel */
        .st-key-register-right-panel {{
            padding: 1.5rem !important;
            background: #fff !important;
            border: 1px solid #e4ece5 !important;
            box-shadow: 0 10px 30px rgba(23, 61, 43, .10) !important;
        }}

        .st-key-register-right-panel > div,
        .st-key-register-right-panel [data-testid="stVerticalBlock"] {{
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            box-sizing: border-box !important;
            background: #fff !important;
        }}

        .st-key-register-right-panel [data-testid="stForm"] {{
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            padding: 1rem !important;
            box-sizing: border-box !important;
            background: #fff !important;
            border: 1px solid #e4ece5 !important;
            border-radius: 15px !important;
            box-shadow: none !important;
        }}

        .st-key-register-right-panel [data-testid="stForm"] [data-testid="stVerticalBlock"] {{
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            box-sizing: border-box !important;
        }}

        /* Registration headings */
        .register-heading {{
            color: var(--pp-green);
            font-size: 1.75rem;
            font-weight: 800;
            line-height: 1.25;
            margin: 0 0 .2rem;
        }}

        .register-subheading {{
            color: var(--pp-muted);
            font-size: .9rem;
            margin: 0 0 1rem;
        }}

        /* Form controls */
        [data-testid="stTextInput"] {{ width: 100%; min-width: 0; }}
        [data-testid="stTextInput"] label, [data-testid="stRadio"] > label {{
            color: var(--pp-green) !important; font-size: .88rem !important;
            font-weight: 600 !important;
        }}
        [data-testid="stTextInput"] input {{
            width: 100%; min-width: 0; min-height: 44px;
            color: var(--pp-dark) !important; background: #fff !important;
            border: 1px solid #92c29f !important; border-radius: 9px !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stTextInput"] input:focus {{
            border-color: var(--pp-green) !important;
            box-shadow: 0 0 0 2px rgba(40, 107, 70, .15) !important;
        }}
        .st-key-register-right-panel [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {{
            border-color: var(--pp-green) !important;
        }}
        .st-key-register-right-panel [data-testid="stRadio"] label:has(input:checked) {{
            color: var(--pp-dark) !important;
        }}
        [data-testid="stCheckbox"] label {{
            color: var(--pp-dark) !important; font-size: .85rem; font-weight: 500;
        }}
        .stApp button[kind="primary"], .stApp [data-testid="stFormSubmitButton"] button {{
            width: 100%; min-height: 44px; color: #fff !important;
            background: var(--pp-dark) !important; border: 1px solid var(--pp-dark) !important;
            border-radius: 9px !important; font-weight: 700 !important;
        }}
        .stApp button[kind="primary"]:hover,
        .stApp [data-testid="stFormSubmitButton"] button:hover {{
            color: #fff !important; background: var(--pp-green) !important;
            border-color: var(--pp-green) !important;
        }}
        .stApp button[kind="secondary"] {{
            width: 100%; min-height: 40px; color: var(--pp-green) !important;
            background: #fff !important; border: 1px solid var(--pp-border) !important;
            border-radius: 9px !important; font-weight: 600;
        }}
        .stApp button[kind="secondary"]:hover {{
            background: var(--pp-pale) !important; border-color: var(--pp-green) !important;
        }}
        [data-testid="stAlert"] {{ border-radius: 10px; }}

        
        /* Tablets and smaller laptops */
        @media screen and (max-width: 1100px) {{

            .block-container {{
                padding: 2rem 1.25rem 1.5rem !important;
            }}

            /* Registration panels */
            [data-testid="stHorizontalBlock"]:has(.st-key-register-left-panel) {{
                gap: 1rem !important;
            }}

            .st-key-register-left-panel,
            .st-key-register-right-panel {{
                min-height: 680px !important;
            }}

            .st-key-register-left-panel {{
                padding: 1.75rem 1.5rem !important;
            }}

            .st-key-register-logo [data-testid="stImage"] img {{
                width: 160px !important;
                max-width: 100% !important;
            }}

            .st-key-register-illustration [data-testid="stImage"] img {{
                width: 260px !important;
                max-width: 100% !important;
            }}

            .benefit-title {{
                font-size: 1.05rem !important;
            }}

            .benefit-description {{
                font-size: 0.9rem !important;
            }}
        }}

        /* Phones and narrow screens */
        @media screen and (max-width: 768px) {{

            .block-container {{
                padding: 1.25rem 0.75rem 1.5rem !important;
            }}

            /* Login page */
            .st-key-login-card {{
                width: 100% !important;
                max-width: 600px !important;
                margin: 1rem auto !important;
                padding: 1.25rem !important;
                border-radius: 16px !important;
            }}

            .st-key-login-card [data-testid="stForm"] {{
                padding: 1rem !important;
            }}

            .st-key-login-card [data-testid="stImage"] {{
                padding-left: 0 !important;
                justify-content: center !important;
            }}

            .login-heading {{
                font-size: 1.7rem !important;
            }}

            .login-subheading {{
                font-size: 0.9rem !important;
            }}

            /* Stack registration panels vertically */
            [data-testid="stHorizontalBlock"]:has(.st-key-register-left-panel) {{
                flex-direction: column !important;
                align-items: stretch !important;
                gap: 1rem !important;
            }}

            [data-testid="stHorizontalBlock"]:has(.st-key-register-left-panel) > [data-testid="column"] {{
                width: 100% !important;
                min-width: 0 !important;
                flex: 1 1 100% !important;
            }}

            .st-key-register-left-panel,
            .st-key-register-right-panel {{
                width: 100% !important;
                min-width: 0 !important;
                min-height: auto !important;
                height: auto !important;
                border-radius: 16px !important;
            }}

            /* Registration information panel */
            .st-key-register-left-panel {{
                padding: 1.5rem 1.25rem !important;
            }}

            .st-key-register-logo {{
                margin: 0 auto 0.5rem !important;
            }}

            .st-key-register-logo [data-testid="stImage"] img {{
                width: 145px !important;
                max-width: 100% !important;
            }}

            .st-key-register-illustration {{
                margin: 0.75rem 0 1.5rem !important;
            }}

            .st-key-register-illustration [data-testid="stImage"] img {{
                width: 240px !important;
                max-width: 100% !important;
            }}

            [class*="st-key-register-benefit-"] {{
                margin-bottom: 1.25rem !important;
            }}

            [class*="st-key-register-benefit-"] [data-testid="stHorizontalBlock"] {{
                gap: 0.5rem !important;
            }}

            [class*="st-key-register-benefit-"] [data-testid="column"] {{
                min-width: 0 !important;
            }}

            [class*="st-key-register-benefit-"] [data-testid="column"]:first-child [data-testid="stImage"] img {{
                width: 40px !important;
                max-width: 40px !important;
            }}

            .benefit-title {{
                font-size: 1rem !important;
            }}

            .benefit-description {{
                font-size: 0.88rem !important;
                line-height: 1.4 !important;
            }}

            /* Registration form panel */
            .st-key-register-right-panel {{
                padding: 1.1rem !important;
            }}

            .st-key-register-right-panel [data-testid="stForm"] {{
                padding: 0.9rem !important;
            }}

            .register-heading {{
                font-size: 1.5rem !important;
            }}

            .register-subheading {{
                font-size: 0.88rem !important;
            }}

            /* Keep form fields within the available width */
            .st-key-register-right-panel [data-testid="stTextInput"],
            .st-key-register-right-panel [data-testid="stTextInput"] > div,
            .st-key-register-right-panel [data-testid="stTextInput"] input {{
                width: 100% !important;
                min-width: 0 !important;
                box-sizing: border-box !important;
            }}

            /* Stack paired inputs on narrow screens */
            .st-key-register-right-panel [data-testid="stForm"] [data-testid="stHorizontalBlock"] {{
                flex-wrap: wrap !important;
                gap: 0.5rem !important;
            }}

            .st-key-register-right-panel [data-testid="stForm"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
                width: 100% !important;
                min-width: 0 !important;
                flex: 1 1 100% !important;
            }}

            .st-key-register-right-panel button,
            .st-key-login-card button {{
                min-height: 44px !important;
            }}
        }}

        /* Very small phones */
        @media screen and (max-width: 400px) {{

            .block-container {{
                padding: 0.75rem 0.5rem 1rem !important;
            }}

            .st-key-login-card,
            .st-key-register-left-panel,
            .st-key-register-right-panel {{
                padding: 1rem !important;
                border-radius: 14px !important;
            }}

            .st-key-register-logo [data-testid="stImage"] img {{
                width: 125px !important;
            }}

            .st-key-register-illustration [data-testid="stImage"] img {{
                width: 200px !important;
            }}

            .register-heading {{
                font-size: 1.35rem !important;
            }}

            .benefit-description {{
                overflow-wrap: anywhere;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def load_dashboard_styles():
    """Apply the PasaPrint dashboard layout and visual styling."""
    st.markdown(
        """
        <style>
        :root {
            --pp-dark: #064B36;
            --pp-green: #286B46;
            --pp-pale: #F1F8F3;
            --pp-soft: #D9E9DC;
            --pp-border: #C5DDCB;
            --pp-muted: #66756B;
            --pp-sidebar-expanded: 240px;
            --pp-sidebar-collapsed: 84px;
            --pp-header-height: 80px;
        }

        html, body, .stApp {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow-x: clip !important;
            background: #F7F9F7 !important;
            color: var(--pp-dark) !important;
        }

        [data-testid="stAppViewContainer"] {
            width: 100% !important;
            max-width: 100% !important;
            overflow-x: clip !important;
            background: #F7F9F7 !important;
        }

        /* Hide Streamlit toolbar by default */
        [data-testid="stHeader"],
        [data-testid="stToolbar"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Show Streamlit toolbar only on manager pages */
        body:has(.pp-manager-toolbar) [data-testid="stHeader"],
        body:has(.pp-manager-toolbar) [data-testid="stToolbar"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            height: auto !important;
        }

        /* Keep decorative elements hidden */
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
        }

        /* Main content uses one offset only; width shrinks to fit the viewport. */
        [data-testid="stMainBlockContainer"] {
            width: calc(100% - var(--pp-sidebar-expanded)) !important;
            max-width: none !important;
            margin: 0 0 0 var(--pp-sidebar-expanded) !important;
            padding: calc(var(--pp-header-height) - 80px) 40px 40px !important;
            box-sizing: border-box !important;
            overflow-x: clip !important;
        }

        /* Adjust the content when the sidebar is collapsed */
        [data-testid="stMainBlockContainer"]:has(.st-key-pp-sidebar-collapsed) {
            width: calc(100% - var(--pp-sidebar-collapsed)) !important;
            margin-left: var(--pp-sidebar-collapsed) !important;
        }

        /* Remove extra top spacing before the first dashboard element */
        :root {
            --pp-sidebar-expanded: 240px;
            --pp-sidebar-collapsed: 84px;
            --pp-header-height: 80px;
        }

        /* Main content */
        [data-testid="stMainBlockContainer"] {
            width: calc(100% - var(--pp-sidebar-expanded)) !important;
            max-width: none !important;
            margin: 0 0 0 var(--pp-sidebar-expanded) !important;
            padding: -40px 32px 32px !important;
            box-sizing: border-box !important;
            overflow-x: clip !important;
        }

        /* Remove unwanted spacing above the first content element */
        [data-testid="stMainBlockContainer"] > div:first-child {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        /* Header aligned with sidebar */
        .st-key-pp-header {
            left: var(--pp-sidebar-expanded) !important;
            right: 0 !important;
            width: auto !important;
            top: 0 !important;
            z-index: 1200 !important;
        }

        /* Collapsed sidebar */
        body:has(.st-key-pp-sidebar-collapsed) {
            --pp-current-sidebar: var(--pp-sidebar-collapsed);
        }

        body:has(.st-key-pp-sidebar-collapsed)
        [data-testid="stMainBlockContainer"] {
            width: calc(100% - var(--pp-sidebar-collapsed)) !important;
            margin-left: var(--pp-sidebar-collapsed) !important;
        }

        body:has(.st-key-pp-sidebar-collapsed) .st-key-pp-header {
            left: var(--pp-sidebar-collapsed) !important;
        }

        /* Small screens */
        @media screen and (max-width: 768px) {
            .st-key-pp-sidebar {
                width: 200px !important;
            }

            [data-testid="stMainBlockContainer"] {
                width: calc(100% - 200px) !important;
                margin-left: 200px !important;
                padding: -60px 12px 20px !important;
            }

            .st-key-pp-header {
                left: 200px !important;
                padding: 0 8px !important;
            }

            body:has(.st-key-pp-sidebar-collapsed)
            [data-testid="stMainBlockContainer"] {
                width: calc(100% - var(--pp-sidebar-collapsed)) !important;
                margin-left: var(--pp-sidebar-collapsed) !important;
            }

            body:has(.st-key-pp-sidebar-collapsed) .st-key-pp-header {
                left: var(--pp-sidebar-collapsed) !important;
            }
        }

        [data-testid="stAppViewBlockContainer"] {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }

        [data-testid="stMainBlockContainer"]:has(.st-key-pp-sidebar-collapsed) {
            width: calc(100% - var(--pp-sidebar-collapsed)) !important;
            margin-left: var(--pp-sidebar-collapsed) !important;
        }

        /* Fixed sidebar */
        .st-key-pp-sidebar,
        .st-key-pp-sidebar-collapsed {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            bottom: 0 !important;
            height: 100vh !important;
            min-height: 100vh !important;
            margin: 0 !important;
            box-sizing: border-box !important;
            overflow-x: hidden !important;
            overflow-y: auto !important;
            background: var(--pp-soft) !important;
            border: 0 !important;
            border-radius: 0 !important;
            z-index: 1100 !important;
        }

        .st-key-pp-sidebar {
            width: var(--pp-sidebar-expanded) !important;
            padding: 1rem .7rem !important;
        }

        .st-key-pp-sidebar-collapsed {
            width: var(--pp-sidebar-collapsed) !important;
            padding: 1rem .4rem !important;
        }

        .st-key-pp-sidebar [data-testid="stVerticalBlock"],
        .st-key-pp-sidebar-collapsed [data-testid="stVerticalBlock"] {
            gap: .45rem !important;
        }

        .st-key-pp-sidebar [data-testid="stImage"] {
            width: 100% !important;
            text-align: center !important;
        }

        .st-key-pp-sidebar [data-testid="stImage"] img {
            max-width: 100% !important;
            max-height: 100px !important;
            object-fit: contain !important;
        }

        .st-key-pp-sidebar-collapsed [data-testid="stImage"] img {
            width: 55px !important;
            height: 55px !important;
            object-fit: contain !important;
        }

        .pp-brand {
            color: var(--pp-dark) !important;
            font-size: 1.45rem !important;
            font-weight: 800 !important;
            text-align: center !important;
        }

        .pp-tagline {
            color: #426A53 !important;
            text-align: center !important;
            font-size: .65rem !important;
            margin-top: -.25rem !important;
        }

        .pp-mini-logo {
            text-align: center !important;
            color: var(--pp-dark) !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
        }

        .pp-nav-gap { height: 1rem !important; }

        .st-key-pp-sidebar [class*="st-key-pp-nav-"],
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] {
            border-radius: 10px !important;
            margin-bottom: .35rem !important;
            padding: .08rem .2rem !important;
            transition: background .2s ease !important;
        }

        .pp-nav-icon,
        .pp-nav-icon-only {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 42px !important;
        }

        .pp-nav-icon img,
        .pp-nav-icon-only img {
            display: block !important;
            width: 22px !important;
            height: 22px !important;
            object-fit: contain !important;
        }

        .st-key-pp-sidebar [class*="st-key-pp-nav-"]:has(button[kind="primary"]),
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"]:has(button[kind="primary"]) {
            background: var(--pp-dark) !important;
        }

        .st-key-pp-sidebar [class*="st-key-pp-nav-"] .stButton,
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] .stButton {
            width: 100% !important;
            margin: 0 !important;
        }

        .st-key-pp-sidebar [class*="st-key-pp-nav-"] button,
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] button {
            width: 100% !important;
            min-height: 42px !important;
            padding: .45rem .4rem !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            font-weight: 500 !important;
        }

        .st-key-pp-sidebar [class*="st-key-pp-nav-"] button[kind="primary"],
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] button[kind="primary"] {
            background: transparent !important;
            color: #FFFFFF !important;
            border-color: transparent !important;
        }

        .st-key-pp-sidebar [class*="st-key-pp-nav-"] button[kind="secondary"],
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] button[kind="secondary"] {
            background: transparent !important;
            color: var(--pp-dark) !important;
            border-color: transparent !important;
        }

        .st-key-pp-sidebar [class*="st-key-pp-nav-"]:hover,
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"]:hover {
            background: #C8E1CE !important;
        }

        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] button {
            padding: .2rem !important;
        }

        /* Header is a real Streamlit keyed container around the header controls. */
        .st-key-pp-header {
            position: fixed !important;
            top: 0 !important;
            left: var(--pp-sidebar-expanded) !important;
            right: 0 !important;
            width: auto !important;
            height: var(--pp-header-height) !important;
            min-height: var(--pp-header-height) !important;
            margin: 0 !important;
            padding: 0 24px !important;
            box-sizing: border-box !important;
            background: #FFFFFF !important;
            border-bottom: 1px solid #E3ECE5 !important;
            border-radius: 0 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, .04) !important;
            z-index: 1200 !important;
            display: flex !important;
            align-items: center !important;
            overflow: visible !important;
        }

        body:has(.st-key-pp-sidebar-collapsed) .st-key-pp-header {
            left: var(--pp-sidebar-collapsed) !important;
        }

        .st-key-pp-header > div,
        .st-key-pp-header [data-testid="stVerticalBlock"],
        .st-key-pp-header [data-testid="stHorizontalBlock"],
        .st-key-pp-header [data-testid="column"] {
            min-width: 0 !important;
            box-sizing: border-box !important;
            background: #FFFFFF !important;
        }

        .st-key-pp-header [data-testid="stVerticalBlock"],
        .st-key-pp-header [data-testid="stHorizontalBlock"] {
            width: 100% !important;
            align-items: center !important;
        }

        .st-key-pp-header [data-testid="column"] {
            padding: 0 4px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .st-key-pp-header [data-testid="stMarkdownContainer"] p {
            margin: 0 !important;
        }

        .st-key-pp-header .stButton { margin: 0 !important; }

        .st-key-pp-header button {
            min-height: 38px !important;
            min-width: 38px !important;
            padding: .25rem .45rem !important;
            border: 1px solid #D9E3DB !important;
            border-radius: 9px !important;
            background: #FFFFFF !important;
            color: var(--pp-dark) !important;
            box-shadow: none !important;
            font-size: 1rem !important;
        }

        .st-key-pp-header button:hover {
            background: var(--pp-soft) !important;
            border-color: var(--pp-border) !important;
        }

        .pp-header-avatar {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 36px !important;
            height: 36px !important;
            margin: 0 auto !important;
            border-radius: 50% !important;
            background: #426F4D !important;
            color: #FFFFFF !important;
            font-size: 1.2rem !important;
        }

        .pp-header-account { min-width: 0 !important; line-height: 1.2 !important; }
        .pp-header-email {
            overflow: hidden !important;
            color: #173D2B !important;
            font-size: .75rem !important;
            font-weight: 700 !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }
        .pp-header-role {
            margin-top: .1rem !important;
            color: #426A53 !important;
            font-size: .65rem !important;
        }

        /* Floating dropdowns: overlay the dashboard instead of taking page space. */
        .st-key-pp-notification-panel,
        .st-key-pp-profile-panel {
            position: fixed !important;
            top: calc(var(--pp-header-height) + 12px) !important;
            right: 24px !important;
            left: auto !important;
            width: min(340px, calc(100vw - 32px)) !important;
            max-width: calc(100vw - 32px) !important;
            margin: 0 !important;
            padding: 1rem !important;
            box-sizing: border-box !important;
            background: #FFFFFF !important;
            border: 1px solid var(--pp-border) !important;
            border-radius: 12px !important;
            box-shadow: 0 12px 32px rgba(6, 75, 54, .16) !important;
            z-index: 3000 !important;
        }

        .st-key-pp-notification-panel p,
        .st-key-pp-profile-panel p { color: var(--pp-dark) !important; }
        .st-key-pp-profile-panel button { border-radius: 8px !important; }

        /* Consistent vertical alignment for all header controls and account details. */
        .st-key-pp-header {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            overflow: visible !important;
        }

        .st-key-pp-header > div,
        .st-key-pp-header [data-testid="stVerticalBlock"] {
            height: 100% !important;
            min-height: 0 !important;
            justify-content: center !important;
            gap: 0 !important;
        }

        .st-key-pp-header [data-testid="stHorizontalBlock"] {
            height: 100% !important;
            min-height: 0 !important;
            align-items: center !important;
        }

        .st-key-pp-header [data-testid="column"] {
            height: 100% !important;
            min-height: 0 !important;
            align-self: stretch !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .st-key-pp-header [data-testid="column"] > div,
        .st-key-pp-header [data-testid="column"] [data-testid="stMarkdown"] ,
        .st-key-pp-header [data-testid="column"] [data-testid="stMarkdownContainer"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        .st-key-pp-header .stMarkdown,
        .st-key-pp-header [data-testid="stMarkdown"] {
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .st-key-pp-header .pp-header-avatar {
            margin: 0 auto !important;
            transform: translateY(0) !important;
        }

        .st-key-pp-header .pp-header-account {
            align-self: center !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .st-key-pp-header .pp-header-avatar {
                transform: translateY(-8px) !important;
            }
        
            .st-key-pp-header .pp-header-account {
                transform: translateY(-8px) !important;
            }

            /* ===== Keep mobile header controls visible ===== */
            @media screen and (max-width: 600px) {
                .st-key-pp-header [data-testid="stHorizontalBlock"] {
                    display: flex !important;
                    flex-wrap: nowrap !important;
                    align-items: center !important;
                    gap: 3px !important;
                }

                .st-key-pp-header [data-testid="column"] {
                    display: flex !important;
                    min-width: 0 !important;
                    align-items: center !important;
                    justify-content: center !important;
                    padding: 0 1px !important;
                }

                /* Hamburger */
                .st-key-pp-header [data-testid="column"]:nth-child(1) {
                    flex: 0 0 36px !important;
                }

                /* Flexible spacer */
                .st-key-pp-header [data-testid="column"]:nth-child(2) {
                    flex: 1 1 auto !important;
                }

                /* Notifications */
                .st-key-pp-header [data-testid="column"]:nth-child(3) {
                    flex: 0 0 36px !important;
                }

                /* Avatar */
                .st-key-pp-header [data-testid="column"]:nth-child(4) {
                    flex: 0 0 32px !important;
                }

                /* Account text: keep it visible but compact */
                .st-key-pp-header [data-testid="column"]:nth-child(5) {
                    display: flex !important;
                    flex: 0 1 105px !important;
                    min-width: 0 !important;
                    overflow: hidden !important;
                }

                .st-key-pp-header .pp-header-email {
                    max-width: 100% !important;
                    font-size: 9px !important;
                    text-overflow: ellipsis !important;
                    overflow: hidden !important;
                }

                .st-key-pp-header .pp-header-role {
                    font-size: 9px !important;
                }

                /* Account dropdown */
                .st-key-pp-header [data-testid="column"]:nth-child(6) {
                    display: flex !important;
                    flex: 0 0 36px !important;
                }

                .st-key-pp-header button {
                    min-width: 32px !important;
                    width: 32px !important;
                    min-height: 36px !important;
                    height: 36px !important;
                    padding: 0 !important;
                }

                /* Keep popovers floating over the dashboard */
                .st-key-pp-notification-panel,
                .st-key-pp-profile-panel {
                    position: fixed !important;
                    top: calc(var(--pp-header-height) + 8px) !important;
                    right: 8px !important;
                    left: auto !important;
                    width: min(300px, calc(100vw - 80px)) !important;
                    max-width: calc(100vw - 80px) !important;
                    z-index: 3000 !important;
                }
            }

            /* ===== Extra-small mobile screens: 400px and below ===== */
            @media screen and (max-width: 400px) {
                :root {
                    --pp-sidebar-collapsed: 56px;
                    --pp-header-height: 60px;
                }

                /* Compact header */
                .st-key-pp-header {
                    left: 56px !important;
                    right: 0 !important;
                    height: 60px !important;
                    min-height: 60px !important;
                    padding: 0 4px !important;
                }

                /* Keep all header controls on one line */
                .st-key-pp-header [data-testid="stHorizontalBlock"] {
                    display: flex !important;
                    flex-wrap: nowrap !important;
                    align-items: center !important;
                    gap: 1px !important;
                }

                .st-key-pp-header [data-testid="column"] {
                    min-width: 0 !important;
                    padding: 0 !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                }

                /* Hamburger */
                .st-key-pp-header [data-testid="column"]:nth-child(1) {
                    flex: 0 0 32px !important;
                }

                /* Flexible spacer */
                .st-key-pp-header [data-testid="column"]:nth-child(2) {
                    flex: 1 1 0 !important;
                }

                /* Notification bell */
                .st-key-pp-header [data-testid="column"]:nth-child(3) {
                    flex: 0 0 30px !important;
                }

                /* User avatar */
                .st-key-pp-header [data-testid="column"]:nth-child(4) {
                    flex: 0 0 28px !important;
                }

                .st-key-pp-header .pp-header-avatar {
                    width: 26px !important;
                    height: 26px !important;
                    min-width: 26px !important;
                    font-size: 0.9rem !important;
                    transform: none !important;
                }

                /* Account information */
                .st-key-pp-header [data-testid="column"]:nth-child(5) {
                    display: flex !important;
                    flex: 0 1 88px !important;
                    min-width: 0 !important;
                    overflow: hidden !important;
                }

                .st-key-pp-header .pp-header-email {
                    font-size: 8px !important;
                    text-overflow: ellipsis !important;
                    overflow: hidden !important;
                    white-space: nowrap !important;
                }

                .st-key-pp-header .pp-header-role {
                    font-size: 8px !important;
                }

                /* Account dropdown */
                .st-key-pp-header [data-testid="column"]:nth-child(6) {
                    flex: 0 0 30px !important;
                }

                .st-key-pp-header button {
                    width: 28px !important;
                    min-width: 28px !important;
                    height: 32px !important;
                    min-height: 32px !important;
                    padding: 0 !important;
                    font-size: 0.8rem !important;
                }

                /* Keep page content inside the viewport */
                [data-testid="stMainBlockContainer"] {
                    padding: 72px 10px 16px !important;
                    overflow-x: clip !important;
                }

                [data-testid="stMainBlockContainer"] h1 {
                    font-size: 1.65rem !important;
                    line-height: 1.2 !important;
                    overflow-wrap: anywhere !important;
                }

                /* Floating panels remain accessible */
                .st-key-pp-notification-panel,
                .st-key-pp-profile-panel {
                    top: 68px !important;
                    right: 6px !important;
                    width: min(280px, calc(100vw - 68px)) !important;
                    max-width: calc(100vw - 68px) !important;
                    padding: 0.75rem !important;
                    z-index: 3000 !important;
                }
            }

            /* Bring the hamburger closer to the sidebar on small screens */
            @media screen and (max-width: 400px) {
                .st-key-pp-header {
                    left: 56px !important;
                    padding-left: 2px !important;
                    padding-right: 4px !important;
                }

                /* Remove extra spacing around the hamburger column */
                .st-key-pp-header [data-testid="column"]:nth-child(1) {
                    flex: 0 0 32px !important;
                    width: 32px !important;
                    padding: 0 !important;
                    margin-left: 0 !important;
                }

                .st-key-pp-header [data-testid="column"]:nth-child(1) button {
                    margin-left: 0 !important;
                }

                .st-key-pp-header [data-testid="stHorizontalBlock"] {
                    gap: 0 !important;
                }
            }
        /* Customer sidebar navigation buttons */
        .st-key-pp-sidebar [class*="st-key-pp-nav-"] button,
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] button {
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 14px !important;
            width: 100% !important;
            min-height: 52px !important;
            padding: 10px 14px !important;
            border-radius: 10px !important;
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            text-align: left !important;
            line-height: 1.3 !important;
            transition:
                background-color 0.18s ease,
                color 0.18s ease !important;
        }

        /* Selected navigation item */
        .st-key-pp-sidebar [class*="st-key-pp-nav-"]:has(button[kind="primary"]),
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"]:has(button[kind="primary"]) {
            background: #064B36 !important;
            border-radius: 10px !important;
        }

        /* Selected button */
        .st-key-pp-sidebar [class*="st-key-pp-nav-"] button[kind="primary"],
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] button[kind="primary"] {
            background: transparent !important;
            color: #FFFFFF !important;
            border: 1px solid transparent !important;
            font-weight: 700 !important;
        }

        /* Unselected buttons */
        .st-key-pp-sidebar [class*="st-key-pp-nav-"] button[kind="secondary"],
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] button[kind="secondary"] {
            background: transparent !important;
            color: #064B36 !important;
            border: 1px solid transparent !important;
            font-weight: 600 !important;
        }

        /* Hover effect */
        .st-key-pp-sidebar [class*="st-key-pp-nav-"]:hover,
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"]:hover {
            background: #C8E1CE !important;
            border-radius: 10px !important;
        }

        /* Keep selected item dark green on hover */
        .st-key-pp-sidebar [class*="st-key-pp-nav-"]:has(button[kind="primary"]):hover,
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"]:has(button[kind="primary"]):hover {
            background: #064B36 !important;
        }

        /* Expanded sidebar: stronger symbols and readable labels */
        .st-key-pp-sidebar [class*="st-key-pp-nav-"] button {
            font-size: 0.92rem !important;
            font-weight: 650 !important;
        }

        /* Collapsed sidebar: larger, centered symbols */
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] button {
            justify-content: center !important;
            padding: 8px 2px !important;
            min-height: 54px !important;
            font-size: 1.45rem !important;
            font-weight: 800 !important;
            text-align: center !important;
        }

        /* Space below the logo */
        .st-key-pp-sidebar .pp-nav-gap,
        .st-key-pp-sidebar-collapsed .pp-nav-gap {
            height: 1.1rem !important;
        }

        /* Consistent spacing between navigation items */
        .st-key-pp-sidebar [class*="st-key-pp-nav-"],
        .st-key-pp-sidebar-collapsed [class*="st-key-pp-nav-"] {
            margin-bottom: 6px !important;
        }

        /* Prevent horizontal overflow */
        .st-key-pp-sidebar,
        .st-key-pp-sidebar-collapsed {
            overflow-x: hidden !important;
        }

        .st-key-pp-sidebar [data-testid="stVerticalBlock"],
        .st-key-pp-sidebar-collapsed [data-testid="stVerticalBlock"] {
            width: 100% !important;
            min-width: 0 !important;
        }

        /* Larger collapsed logo */
        .st-key-pp-sidebar-collapsed [data-testid="stImage"] img {
            width: 55px !important;
            max-width: 100% !important;
            height: auto !important;
            object-fit: contain !important;
        }


        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def load_manager_toolbar_styles():
    st.markdown("""
        <style>
        [data-testid="stHeader"],
        [data-testid="stToolbar"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        </style>
    """, unsafe_allow_html=True)
