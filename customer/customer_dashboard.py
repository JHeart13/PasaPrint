from pathlib import Path
from html import escape
import base64
from textwrap import dedent

import streamlit as st

from database.connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ICON_FOLDER = PROJECT_ROOT / "assets" / "icons"
WELCOME_BACKGROUND = (
    PROJECT_ROOT / "assets" / "backgrounds" / "login_background.png"
)


def get_dashboard_data(customer_id):
    """Fetch order counts, recent orders, and uploaded files."""

    with get_connection() as connection:
        active_orders = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM orders
            WHERE customer_id = ?
              AND LOWER(status) NOT IN
                  ('completed', 'rejected', 'cancelled')
            """,
            (customer_id,),
        ).fetchone()["total"]

        completed_orders = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM orders
            WHERE customer_id = ?
              AND LOWER(status) = 'completed'
            """,
            (customer_id,),
        ).fetchone()["total"]

        recent_orders = connection.execute(
            """
            SELECT
                o.order_id,
                o.order_number,
                o.status,
                o.created_at,
                GROUP_CONCAT(DISTINCT f.original_filename) AS file_names
            FROM orders AS o
            LEFT JOIN order_files AS f
                ON f.order_id = o.order_id
                AND f.file_type = 'document'
            WHERE o.customer_id = ?
            GROUP BY
                o.order_id,
                o.order_number,
                o.status,
                o.created_at
            ORDER BY o.created_at DESC, o.order_id DESC
            LIMIT 5
            """,
            (customer_id,),
        ).fetchall()

        saved_files = connection.execute(
            """
            SELECT
                f.file_id,
                f.original_filename,
                f.uploaded_at,
                o.order_number
            FROM order_files AS f
            JOIN orders AS o ON o.order_id = f.order_id
            WHERE o.customer_id = ?
              AND f.file_type = 'document'
            ORDER BY f.uploaded_at DESC, f.file_id DESC
            LIMIT 5
            """,
            (customer_id,),
        ).fetchall()

    return active_orders, completed_orders, recent_orders, saved_files


def _image_data_uri(filename):
    """Load an image from assets/icons as an embedded image URI."""

    path = ICON_FOLDER / filename

    if not path.is_file():
        return ""

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    mime_type = mime_types.get(path.suffix.lower())

    if not mime_type:
        return ""

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _image_html(filename, alt, width=48):
    """Create an image tag for an existing icon."""

    image_uri = _image_data_uri(filename)

    if not image_uri:
        return ""

    return (
        f'<img src="{image_uri}" alt="{escape(alt)}" '
        f'style="width:{width}px;height:{width}px;object-fit:contain;">'
    )


def _welcome_background_css():
    """Create a light version of the printing-pattern background."""

    if not WELCOME_BACKGROUND.is_file():
        return "background-color: #E3F1E7;"

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    mime_type = mime_types.get(WELCOME_BACKGROUND.suffix.lower())

    if not mime_type:
        return "background-color: #E3F1E7;"

    encoded = base64.b64encode(WELCOME_BACKGROUND.read_bytes()).decode("ascii")

    return (
        "background-image: "
        "linear-gradient(rgba(227,241,231,0.88), "
        "rgba(227,241,231,0.88)), "
        f"url('data:{mime_type};base64,{encoded}');"
        "background-size: cover;"
        "background-position: center;"
    )


def load_dashboard_styles():
    """Apply responsive customer dashboard styling."""

    welcome_background = _welcome_background_css()
    new_order_icon = _image_data_uri("new_order.png")

    st.markdown(
        f"""
        <style>
        .pp-dashboard {{
            width: 100%;
            min-width: 0;
            color: #064B36;
        }}

        /* Welcome banner */
        .st-key-pp-welcome-banner {{
            {welcome_background}
            background-repeat: no-repeat;
            border: 1px solid #D0E6D5;
            border-radius: 16px;
            padding: 28px !important;
            min-height: 164px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .st-key-pp-welcome-banner [data-testid="stVerticalBlock"] {{
            gap: 0.45rem;
        }}

        .pp-welcome-small {{
            color: #064B36;
            font-size: 1.05rem;
            font-weight: 750;
            line-height: 1.4;
            margin: 0 0 4px;
        }}

        .pp-welcome-name {{
            color: #064B36;
            font-size: clamp(1.6rem, 2.6vw, 2.4rem);
            font-weight: 800;
            line-height: 1.2;
            overflow-wrap: anywhere;
            margin: 0;
        }}

        .pp-welcome-caption {{
            color: #286A4B;
            font-size: 0.95rem;
            line-height: 1.5;
            margin-top: 5px;
        }}

        /* Top row: allow columns to shrink without overflowing */
        .st-key-pp-dashboard-top {{
            width: 100%;
            min-width: 0;
        }}

        .st-key-pp-dashboard-top [data-testid="stHorizontalBlock"] {{
            align-items: stretch;
        }}

        .st-key-pp-dashboard-top [data-testid="column"] {{
            min-width: 0 !important;
        }}

        /* Create New Order button */
        .st-key-pp_create_order {{
            width: 100%;
            min-width: 0;
        }}

        .st-key-pp_create_order button {{
            position: relative !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;

            width: 100% !important;
            min-width: 0 !important;
            min-height: 164px !important;
            box-sizing: border-box !important;

            padding: 22px 42px 22px 88px !important;

            background: #064B36 !important;
            background-color: #064B36 !important;
            color: #FFFFFF !important;
            border: 1px solid #064B36 !important;
            border-radius: 20px !important;

            text-align: left !important;
            white-space: normal !important;
            overflow-wrap: break-word !important;
            box-shadow: none !important;

            transition:
                background-color 0.2s ease,
                border-color 0.2s ease,
                transform 0.2s ease !important;
        }}

        .st-key-pp_create_order button [data-testid="stMarkdownContainer"] {{
            width: 100% !important;
            min-width: 0 !important;
            text-align: left !important;
        }}

        .st-key-pp_create_order button p {{
            margin: 0 !important;
            color: #FFFFFF !important;
            font-size: 0.96rem !important;
            font-weight: 600 !important;
            line-height: 1.55 !important;
            white-space: pre-line !important;
            overflow-wrap: anywhere !important;
            word-break: normal !important;
        }}

        .st-key-pp_create_order button:hover {{
            background: #0A6045 !important;
            background-color: #0A6045 !important;
            border-color: #0A6045 !important;
            color: #FFFFFF !important;
            transform: translateY(-2px);
        }}

        .st-key-pp_create_order button:focus-visible {{
            outline: 3px solid #B9DDBF !important;
            outline-offset: 3px !important;
        }}

        .st-key-pp_create_order button::before {{
            content: "";
            position: absolute;
            left: 18px;
            top: 50%;
            transform: translateY(-50%);
            width: 56px;
            height: 56px;
            background-image: url("{new_order_icon}");
            background-repeat: no-repeat;
            background-position: center;
            background-size: contain;
            pointer-events: none;
        }}

        .st-key-pp_create_order button::after {{
            content: "›";
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #FFFFFF;
            font-size: 2rem;
            font-weight: 600;
            line-height: 1;
            pointer-events: none;
        }}

        /* Order count cards */
        .pp-stat-card {{
            position: relative;
            overflow: hidden;
            width: 100%;
            min-width: 0;
            min-height: 110px;
            background: #FFFFFF;
            border: 1px solid #E1ECE4;
            border-radius: 14px;
            padding: 18px 20px;
            display: flex;
            align-items: center;
            gap: 14px;
            box-sizing: border-box;
        }}

        .pp-stat-icon {{
            width: 62px;
            height: 62px;
            flex-shrink: 0;
            border-radius: 12px;
            background: #B9DDBF;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            z-index: 1;
        }}

        .pp-stat-icon img {{
            width: 48px;
            height: 48px;
            object-fit: contain;
        }}

        .pp-stat-copy {{
            position: relative;
            z-index: 1;
            min-width: 0;
        }}

        .pp-stat-number {{
            color: #286A4B;
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 800;
        }}

        .pp-stat-label {{
            color: #064B36;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.4;
            margin-top: 5px;
        }}

        .pp-watermark {{
            position: absolute;
            right: 8px;
            bottom: 0;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            pointer-events: none;
            overflow: hidden;
        }}

        .pp-watermark img {{
            height: 100% !important;
            width: auto !important;
            max-width: none !important;
            object-fit: contain;
        }}

        .pp-printer-watermark,
        .pp-file-watermark {{
            opacity: 0.22;
        }}

        /* Recent Orders and Saved Files panels */
        .st-key-pp-recent-panel,
        .st-key-pp-saved-panel {{
            background: #FFFFFF;
            border: 1px solid #E1ECE4;
            border-radius: 14px;
            overflow: hidden;
            min-width: 0;
            min-height: 340px;
            padding: 0 !important;
        }}

        .st-key-pp-recent-panel [data-testid="stVerticalBlock"],
        .st-key-pp-saved-panel [data-testid="stVerticalBlock"] {{
            gap: 0;
        }}

        .pp-panel-heading {{
            color: #286A4B;
            font-size: 1.2rem;
            font-weight: 800;
            line-height: 1.4;
            padding: 18px 20px 14px;
            margin: 0;
        }}

        .st-key-pp-recent-panel [class*="st-key-pp-view-orders"],
        .st-key-pp-saved-panel [class*="st-key-pp-view-files"] {{
            padding: 8px 14px 0 0 !important;
            min-width: 0;
        }}

        .st-key-pp-recent-panel [class*="st-key-pp-view-orders"] button,
        .st-key-pp-saved-panel [class*="st-key-pp-view-files"] button {{
            width: 100% !important;
            min-height: 36px;
            margin: 0 0 8px !important;
            border-radius: 8px;
            color: #064B36 !important;
            border: 1px solid #D5E3D9 !important;
            background: #FFFFFF !important;
            font-size: 0.86rem;
        }}

        .st-key-pp-recent-panel [class*="st-key-pp-view-orders"] button:hover,
        .st-key-pp-saved-panel [class*="st-key-pp-view-files"] button:hover {{
            background: #E3F1E7 !important;
            border-color: #B9DDBF !important;
            color: #064B36 !important;
        }}

        .pp-panel-empty {{
            color: #719888;
            font-size: 0.9rem;
            line-height: 1.6;
            padding: 20px;
            margin: 0;
        }}

        .pp-file-row {{
            padding: 13px 20px;
            border-top: 1px solid #EAF1EB;
            overflow-wrap: anywhere;
        }}

        .pp-file-name {{
            color: #064B36;
            font-size: 0.92rem;
            font-weight: 700;
        }}

        .pp-muted {{
            color: #719888;
            font-size: 0.82rem;
            margin-top: 4px;
        }}

        .pp-table-wrap {{
            width: 100%;
            overflow-x: auto;
        }}

        .pp-table-header {{
            display: grid;
            grid-template-columns: 0.8fr 1.8fr 0.9fr 0.8fr;
            gap: 8px;
            min-width: 400px;
            padding: 10px 16px;
            background: #E3F1E7;
            color: #286A4B;
            font-size: 0.88rem;
            font-weight: 700;
            box-sizing: border-box;
        }}

        .pp-table-row {{
            display: grid;
            grid-template-columns: 0.8fr 1.8fr 0.9fr 0.8fr;
            gap: 8px;
            min-width: 400px;
            padding: 12px 16px;
            border-top: 1px solid #EAF1EB;
            color: #286A4B;
            font-size: 0.84rem;
            align-items: start;
            box-sizing: border-box;
        }}

        .pp-table-row > div {{
            overflow-wrap: anywhere;
        }}

        .pp-status {{
            display: inline-block;
            padding: 3px 7px;
            border-radius: 7px;
            background: #E3F1E7;
            color: #064B36;
            font-size: 0.78rem;
        }}

        /* Tablet and smaller desktop layouts */
        @media (max-width: 1100px) {{
            .st-key-pp-dashboard-top [data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
                gap: 16px !important;
            }}

            .st-key-pp-dashboard-top [data-testid="column"] {{
                width: 100% !important;
                min-width: 100% !important;
                flex: 1 1 100% !important;
            }}

            .st-key-pp_create_order button {{
                min-height: 120px !important;
                padding: 18px 40px 18px 76px !important;
                border-radius: 16px !important;
            }}

            .st-key-pp_create_order button::before {{
                left: 14px;
                width: 48px;
                height: 48px;
            }}

            .st-key-pp_create_order button::after {{
                right: 12px;
                font-size: 1.8rem;
            }}
        }}

        /* Mobile */
        @media (max-width: 700px) {{
            .st-key-pp-welcome-banner {{
                padding: 22px 18px !important;
                min-height: 145px;
            }}

            .st-key-pp_create_order button {{
                min-height: 112px !important;
                padding: 16px 38px 16px 70px !important;
                border-radius: 16px !important;
            }}

            .st-key-pp_create_order button::before {{
                left: 12px;
                width: 44px;
                height: 44px;
            }}

            .st-key-pp_create_order button::after {{
                right: 10px;
                font-size: 1.6rem;
            }}

            .st-key-pp_create_order button p {{
                font-size: 0.88rem !important;
                line-height: 1.5 !important;
            }}

            .pp-stat-card {{
                min-height: 88px;
                padding: 12px;
                gap: 10px;
            }}

            .pp-stat-icon {{
                width: 44px;
                height: 44px;
            }}

            .pp-stat-icon img {{
                width: 34px;
                height: 34px;
            }}

            .pp-stat-number {{
                font-size: 1.55rem;
            }}

            .pp-stat-label {{
                font-size: 0.82rem;
            }}

            .pp-panel-heading {{
                padding: 14px 12px 10px;
                font-size: 1rem;
            }}

            .pp-panel-empty {{
                padding: 16px 12px;
            }}

            .pp-file-row {{
                padding: 12px;
            }}

            .st-key-pp-recent-panel [class*="st-key-pp-view-orders"],
            .st-key-pp-saved-panel [class*="st-key-pp-view-files"] {{
                padding-right: 8px !important;
            }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            .st-key-pp_create_order button {{
                transition: none !important;
            }}

            .st-key-pp_create_order button:hover {{
                transform: none;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _format_status(status):
    """Convert database statuses into readable labels."""

    return str(status or "pending").replace("_", " ").title()


def render_customer_dashboard(user):
    """Render the customer's home dashboard."""

    load_dashboard_styles()

    customer_id = user.get("user_id")

    if customer_id is None:
        st.error("Your account could not be identified. Please log in again.")
        return

    username = escape(str(user.get("username") or "Student"))

    try:
        (
            active_orders,
            completed_orders,
            recent_orders,
            saved_files,
        ) = get_dashboard_data(customer_id)

    except Exception as error:
        st.error(
            "We couldn't load your dashboard information. "
            "Please check your database connection and try again."
        )
        print(
            f"Customer dashboard database error: "
            f"{type(error).__name__}: {error}"
        )
        return

    st.markdown(
        '<div class="pp-dashboard">',
        unsafe_allow_html=True,
    )

    with st.container(key="pp-dashboard-top"):
        welcome_col, action_col = st.columns(
            [1.85, 1],
            gap="medium",
        )

        with welcome_col:
            with st.container(key="pp-welcome-banner"):
                st.markdown(
                    '<div class="pp-welcome-small">Welcome Back,</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="pp-welcome-name">{username}!</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="pp-welcome-caption">'
                    'Ready to print your documents?</div>',
                    unsafe_allow_html=True,
                )

        with action_col:
            order_button_label = (
                "CREATE NEW ORDER\n"
                "Upload files and choose print settings"
            )

            if st.button(
                order_button_label,
                key="pp_create_order",
                type="primary",
                width="stretch",
                help="Upload your documents and choose your print settings.",
            ):
                st.session_state["customer_page"] = "new_order"
                st.rerun()

    active_col, completed_col = st.columns(2, gap="medium")

    with active_col:
        active_image = _image_html(
            "active_orders.png",
            "Active orders",
        )
        printer_watermark = _image_html(
            "printer_watermark.png",
            "Printer watermark",
            120,
        )

        active_html = dedent(f"""
            <div class="pp-stat-card">
                <div class="pp-stat-icon">{active_image}</div>
                <div class="pp-stat-copy">
                    <div class="pp-stat-number">{active_orders}</div>
                    <div class="pp-stat-label">Active Orders</div>
                </div>
                <div class="pp-watermark pp-printer-watermark">
                    {printer_watermark}
                </div>
            </div>
        """).strip()

        st.markdown(active_html, unsafe_allow_html=True)

    with completed_col:
        completed_image = _image_html(
            "completed_orders.png",
            "Completed orders",
        )
        file_watermark = _image_html(
            "file_watermark.png",
            "File watermark",
            120,
        )

        completed_html = dedent(f"""
            <div class="pp-stat-card">
                <div class="pp-stat-icon">{completed_image}</div>
                <div class="pp-stat-copy">
                    <div class="pp-stat-number">{completed_orders}</div>
                    <div class="pp-stat-label">Completed Orders</div>
                </div>
                <div class="pp-watermark pp-file-watermark">
                    {file_watermark}
                </div>
            </div>
        """).strip()

        st.markdown(completed_html, unsafe_allow_html=True)

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    orders_col, files_col = st.columns(
        [1.2, 1],
        gap="medium",
    )

    with orders_col:
        with st.container(key="pp-recent-panel"):
            title_col, button_col = st.columns(
                [1.5, 0.7],
                gap="small",
            )

            with title_col:
                st.markdown(
                    '<div class="pp-panel-heading">Recent Orders</div>',
                    unsafe_allow_html=True,
                )

            with button_col:
                if st.button(
                    "View all →",
                    key="pp-view-orders",
                    width="stretch",
                ):
                    st.session_state["customer_page"] = "my_orders"
                    st.rerun()

            st.markdown(
                """
                <div class="pp-table-wrap">
                    <div class="pp-table-header">
                        <div>Order#</div>
                        <div>File Name</div>
                        <div>Date</div>
                        <div>Status</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not recent_orders:
                st.markdown(
                    '<p class="pp-panel-empty">'
                    "You haven’t placed any orders yet. "
                    "Your recent orders will appear here."
                    "</p>",
                    unsafe_allow_html=True,
                )
            else:
                for order in recent_orders:
                    order_number = escape(
                        str(
                            order["order_number"]
                            or f'#{order["order_id"]}'
                        )
                    )
                    filenames = escape(
                        str(order["file_names"] or "No file recorded")
                    )
                    date = escape(str(order["created_at"] or "")[:10])
                    status = escape(_format_status(order["status"]))

                    row_html = dedent(f"""
                        <div class="pp-table-wrap">
                            <div class="pp-table-row">
                                <div>{order_number}</div>
                                <div>{filenames}</div>
                                <div>{date}</div>
                                <div><span class="pp-status">{status}</span></div>
                            </div>
                        </div>
                    """).strip()

                    st.markdown(row_html, unsafe_allow_html=True)

    with files_col:
        with st.container(key="pp-saved-panel"):
            title_col, button_col = st.columns(
                [1.5, 0.7],
                gap="small",
            )

            with title_col:
                st.markdown(
                    '<div class="pp-panel-heading">Saved Files</div>',
                    unsafe_allow_html=True,
                )

            with button_col:
                if st.button(
                    "View all →",
                    key="pp-view-files",
                    width="stretch",
                ):
                    st.session_state["customer_page"] = "saved_files"
                    st.rerun()

            if not saved_files:
                st.markdown(
                    '<p class="pp-panel-empty">'
                    "No uploaded documents yet. "
                    "Files from your orders will appear here."
                    "</p>",
                    unsafe_allow_html=True,
                )
            else:
                for saved_file in saved_files:
                    filename = escape(
                        str(
                            saved_file["original_filename"]
                            or "Untitled file"
                        )
                    )
                    order_number = escape(
                        str(saved_file["order_number"] or "—")
                    )
                    uploaded_at = escape(
                        str(saved_file["uploaded_at"] or "")[:10]
                    )

                    file_html = dedent(f"""
                        <div class="pp-file-row">
                            <div class="pp-file-name">📄 {filename}</div>
                            <div class="pp-muted">
                                Order {order_number} · {uploaded_at}
                            </div>
                        </div>
                    """).strip()

                    st.markdown(file_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


show_customer_dashboard = render_customer_dashboard
