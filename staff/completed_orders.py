import streamlit as st
from pathlib import Path
from datetime import datetime
import re
import html
import base64
from database.order_repository import OrderRepository
from database.file_repository import FileRepository
from database.connection import PROJECT_ROOT
# ==================================================
# CONFIGURATION
# ==================================================
GREEN = "#064B36"
MID_GREEN = "#286B46"
LIGHT_GREEN = "#EAF4EC"
BORDER_GREEN = "#D9E9DC"
# ==================================================
# HELPERS
# ==================================================
def get_value(data, key, default=None):
    try:
        value = data[key]
        return default if value is None else value
    except (KeyError, IndexError, TypeError):
        return default
def safe_text(value):
    return html.escape(str(value if value is not None else "Not available"))
def format_currency(value):
    try:
        return f"₱{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₱0.00"
def render_section_heading(title):
    st.markdown(
        f'<div class="completed-section-title">{safe_text(title)}</div>',
        unsafe_allow_html=True
    )
# ==================================================
# STYLING
# ==================================================
def get_header_background():
    candidates = [
        PROJECT_ROOT / "assets" / "backgrounds" / "login_background.png",
        PROJECT_ROOT / "assets" / "login_background.png",
    ]
    for image_path in candidates:
        if image_path.is_file():
            encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
            return f'url("data:image/png;base64,{encoded}")'
    return "linear-gradient(120deg, #064B36, #286B46)"

def render_page_styles():
    header_background = get_header_background()
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #F5F8F5;
        }
        .st-key-completed_orders_header {
            background:
                linear-gradient(
                    110deg,
                    rgba(6,75,54,0.88),
                    rgba(6,75,54,0.70)
                ),
                __HEADER_BG__;
            background-color: #064B36;
            background-size: cover;
            background-position: center;
            border: 1px solid #D9E9DC;
            border-radius: 18px;
            padding: 30px 35px;
            margin-bottom: 25px;
            box-shadow: 0 5px 18px rgba(6,75,54,0.10);
        }
        .st-key-completed_orders_header h1 {
            color: white !important;
            font-size: 34px !important;
            font-weight: 800 !important;
        }
        .st-key-completed_orders_header p {
            color: #E4F2E8 !important;
        }
        .st-key-completed_orders_header
        [data-testid="stCaptionContainer"] p {
            color: white !important;
            font-weight: 700;
            letter-spacing: 1.3px;
        }
        .completed-section-title {
            color: #064B36;
            font-size: 18px;
            font-weight: 700;
            line-height: 1.3;
            letter-spacing: -0.2px;
            padding: 0 0 10px 12px;
            margin: 0 0 14px;
            border-left: 3px solid #286B46;
            border-bottom: 1px solid #E4EEE6;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: 1px solid #D9E9DC !important;
            border-radius: 15px !important;
        }
        div[class*="st-key-completed_info_"] {
            background-color: #EAF4EC !important;
            border: 1px solid #C5DDCB !important;
            border-radius: 12px !important;
            padding: 12px 15px !important;
            min-height: 82px;
            margin-bottom: 8px;
        }
        div[class*="st-key-completed_info_"]
        [data-testid="stCaptionContainer"] p {
            color: #668575 !important;
            font-size: 11px !important;
            font-weight: 650 !important;
            letter-spacing: 0.35px;
            text-transform: uppercase;
        }
        div[class*="st-key-completed_info_"] p {
            color: #064B36 !important;
            font-size: 15px !important;
        }
        div[class*="st-key-completed_summary_"] {
            background-color: #EAF4EC !important;
            border: 1px solid #C5DDCB !important;
            border-radius: 13px !important;
            padding: 14px !important;
            min-height: 105px;
        }
        .completed-summary-label {
            color: #668575;
            font-size: 13px;
            font-weight: 600;
        }
        .completed-summary-number {
            color: #064B36;
            font-size: 31px;
            font-weight: 750;
            line-height: 1.2;
        }
        .completed-status-badge {
            display: inline-block;
            background-color: #064B36;
            color: #FFFFFF;
            border-radius: 30px;
            padding: 8px 15px;
            font-size: 11px;
            font-weight: 750;
            letter-spacing: 0.5px;
        }
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input {
            background-color: #F1F8F3 !important;
            border-color: #D9E9DC !important;
            border-radius: 9px !important;
        }
        div.stButton > button {
            border-radius: 10px;
            min-height: 42px;
        }
        div.stDownloadButton > button {
            background-color: #F1F8F3;
            color: #064B36;
            border: 1px solid #D9E9DC;
            border-radius: 9px;
        }
        h2, h3 {
            color: #064B36 !important;
        }
        </style>
        """.replace("__HEADER_BG__", header_background),
        unsafe_allow_html=True
    )
# ==================================================
# PAGE HEADER
# ==================================================
def render_completed_header():
    with st.container(key="completed_orders_header"):
        st.caption("PASAPRINT • STAFF PORTAL")
        st.title("Completed Orders")
        st.write(
            "Review finished printing requests, access previous "
            "order records, and download customer documents and proofs."
        )
# ==================================================
# INFORMATION CARDS
# ==================================================
def render_info_box(label, value, order_id):
    cleaned_label = re.sub(
        r"[^a-zA-Z0-9_]",
        "_",
        label.lower()
    )
    with st.container(
        key=f"completed_info_{order_id}_{cleaned_label}",
        border=True
    ):
        st.caption(label)
        st.markdown(
            f"**{safe_text(value)}**",
            unsafe_allow_html=True
        )
# ==================================================
# COMPLETED ORDERS RETRIEVAL
# ==================================================
def get_completed_orders(repository):
    try:
        orders = repository.get_orders_by_status("completed")
        return list(orders)
    except Exception as error:
        st.error(f"Unable to retrieve completed orders: {error}")
        return []
# ==================================================
# SUMMARY CARDS
# ==================================================
def render_summary_card(label, count):
    key = re.sub(r"[^a-zA-Z0-9_]", "_", label.lower())
    with st.container(key=f"completed_summary_{key}"):
        st.markdown(
            f"""
            <div class="completed-summary-label">{safe_text(label)}</div>
            <div class="completed-summary-number">{count}</div>
            """,
            unsafe_allow_html=True
        )
def render_summary(orders):
    pickup_count = 0
    delivery_count = 0
    for order in orders:
        method = str(
            get_value(order, "fulfillment_method", "pickup")
        ).lower()
        if method == "delivery":
            delivery_count += 1
        else:
            pickup_count += 1
    columns = st.columns(3)
    summary_items = [
        ("Completed Orders", len(orders)),
        ("Campus Pickup", pickup_count),
        ("Campus Delivery", delivery_count),
    ]
    for column, (label, count) in zip(columns, summary_items):
        with column:
            render_summary_card(label, count)
# ==================================================
# CUSTOMER INFORMATION
# ==================================================
def render_customer_information(order):
    order_id = get_value(order, "order_id")
    render_section_heading("Customer Information")
    col1, col2 = st.columns(2)
    with col1:
        render_info_box(
            "Customer Name",
            get_value(order, "username", "Customer"),
            order_id
        )
    with col2:
        render_info_box(
            "Email Address",
            get_value(order, "email", "Not available"),
            order_id
        )
    render_info_box(
        "Customer ID",
        get_value(order, "customer_id", "N/A"),
        order_id
    )
# ==================================================
# PRINTING DETAILS
# ==================================================
def render_printing_details(order):
    order_id = get_value(order, "order_id")
    render_section_heading("Printing Details")
    col1, col2, col3 = st.columns(3)
    details = [
        ("Paper Size", get_value(order, "paper_size", "N/A")),
        ("Print Color", get_value(order, "color_mode", "N/A")),
        ("Print Sides", get_value(order, "print_sides", "N/A")),
        ("Number of Copies", get_value(order, "copies", 1)),
        ("Total Pages", get_value(order, "total_pages", 0)),
        ("Total Amount", format_currency(get_value(order, "total_cost", 0))),
    ]
    columns = [col1, col2, col3, col1, col2, col3]
    for column, (label, value) in zip(columns, details):
        with column:
            render_info_box(label, value, order_id)
# ==================================================
# FULFILLMENT DETAILS
# ==================================================
def render_fulfillment_details(order):
    order_id = get_value(order, "order_id")
    method = str(
        get_value(order, "fulfillment_method", "pickup")
    ).lower()
    render_section_heading("Fulfillment Details")
    render_info_box(
        "Fulfillment Method",
        method.title(),
        order_id
    )
    if method == "delivery":
        col1, col2, col3 = st.columns(3)
        details = [
            ("Building", get_value(order, "building", "N/A")),
            ("Floor", get_value(order, "floor", "N/A")),
            ("Room", get_value(order, "room", "N/A")),
        ]
        for column, (label, value) in zip(
            [col1, col2, col3],
            details
        ):
            with column:
                render_info_box(label, value, order_id)
        render_info_box(
            "Delivery Notes",
            get_value(order, "delivery_notes", "None"),
            order_id
        )
    else:
        col1, col2 = st.columns(2)
        with col1:
            render_info_box(
                "Campus",
                get_value(order, "campus", "N/A"),
                order_id
            )
        with col2:
            render_info_box(
                "Pickup Location",
                get_value(order, "pickup_location", "N/A"),
                order_id
            )
    st.markdown("**Customer Notes**")
    notes = get_value(order, "customer_notes")
    st.write(notes if notes else "No additional instructions.")
# ==================================================
# COMPLETED DATE
# ==================================================
def get_completion_date(order):
    completed_at = get_value(order, "completed_at")
    if completed_at:
        return str(completed_at)
    updated_at = get_value(order, "updated_at")
    return str(updated_at) if updated_at else "Not recorded"
# ==================================================
# FILES AND PROOFS
# ==================================================
def render_order_files(order_id):
    render_section_heading("Documents and Proof Photos")
    file_repository = FileRepository()
    try:
        files = file_repository.get_order_files(order_id)
    except Exception as error:
        st.error(f"Unable to retrieve order files: {error}")
        return
    if not files:
        st.info("No uploaded files were found for this order.")
        return
    for index, uploaded_file in enumerate(files):
        original_name = get_value(
            uploaded_file,
            "original_filename",
            f"File {index + 1}"
        )
        file_type = get_value(
            uploaded_file,
            "file_type",
            "document"
        )
        stored_path = get_value(
            uploaded_file,
            "file_path",
            ""
        )
        file_path = Path(stored_path) if stored_path else None
        if file_path and not file_path.is_absolute():
            file_path = PROJECT_ROOT / file_path
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{original_name}**")
            st.caption(
                "Print Proof" if file_type == "proof"
                else "Customer Document"
            )
        with col2:
            if file_path and file_path.is_file():
                st.download_button(
                    "Download",
                    data=file_path.read_bytes(),
                    file_name=original_name,
                    key=f"completed_download_{order_id}_{index}",
                    use_container_width=True
                )
            else:
                st.warning("File unavailable.")
# ==================================================
# STATUS HISTORY
# ==================================================
def render_status_history(order_id):
    render_section_heading("Order Status History")
    repository = OrderRepository()
    try:
        history = repository.get_status_history(order_id)
    except Exception as error:
        st.error(f"Unable to retrieve status history: {error}")
        return
    if not history:
        st.info("No status history is available.")
        return
    for item in history:
        old_status = get_value(item, "old_status", "New")
        new_status = get_value(item, "new_status", "N/A")
        changed_at = get_value(item, "changed_at", "Unknown date")
        notes = get_value(item, "notes")
        st.markdown(
            f"**{str(old_status).replace('_', ' ').title()} "
            f"→ {str(new_status).replace('_', ' ').title()}**"
        )
        st.caption(changed_at)
        if notes:
            st.write(notes)
        st.divider()
# ==================================================
# SELECTED COMPLETED ORDER
# ==================================================
def render_selected_completed_order(order):
    order_id = get_value(order, "order_id")
    order_number = get_value(
        order,
        "order_number",
        f"Order #{order_id}"
    )
    completed_date = get_completion_date(order)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"## {safe_text(order_number)}")
        st.caption(
            f"Completed: {completed_date}"
        )
    with col2:
        st.markdown(
            """
            <div style="display:flex;justify-content:flex-end;padding-top:8px;">
                <span class="completed-status-badge">
                    COMPLETED
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.write("")
    with st.container(border=True):
        render_customer_information(order)
    with st.container(border=True):
        render_printing_details(order)
    with st.container(border=True):
        render_fulfillment_details(order)
    with st.container(border=True):
        render_order_files(order_id)
    with st.container(border=True):
        render_status_history(order_id)
# ==================================================
# MAIN PAGE
# ==================================================
def render_completed_orders_page(user):
    render_page_styles()
    render_completed_header()
    repository = OrderRepository()
    try:
        orders = get_completed_orders(repository)
    except Exception as error:
        st.error(f"Unable to load completed orders: {error}")
        return
    # SUMMARY
    with st.container(border=True):
        st.subheader("Completed Order Overview")
        st.caption(
            "A record of all successfully fulfilled printing requests."
        )
        render_summary(orders)
    st.write("")
    # SEARCH AND FILTERS
    with st.container(border=True):
        render_section_heading("Find Completed Orders")
        search_query = st.text_input(
            "Search",
            placeholder="Search order number, customer name, or email...",
            key="completed_search"
        ).strip().lower()
        customer_options = {
            "All Customers": None
        }
        for order in orders:
            customer_id = get_value(order, "customer_id")
            if customer_id is None:
                continue
            customer_name = get_value(
                order,
                "username",
                "Unknown Customer"
            )
            email = get_value(order, "email", "")
            label = (
                f"{customer_name} ({email})"
                if email else customer_name
            )
            customer_options[label] = str(customer_id)
        col1, col2 = st.columns(2)
        with col1:
            selected_customer = st.selectbox(
                "Filter by Customer",
                list(customer_options.keys()),
                key="completed_customer_filter"
            )
        with col2:
            fulfillment_filter = st.selectbox(
                "Fulfillment Method",
                [
                    "All Methods",
                    "Campus Pickup",
                    "Campus Delivery"
                ],
                key="completed_fulfillment_filter"
            )
        date_filter = st.selectbox(
            "Completion Date",
            [
                "All Dates",
                "Today",
                "Last 7 Days",
                "Last 30 Days"
            ],
            key="completed_date_filter"
        )
    # APPLY FILTERS
    filtered_orders = list(orders)
    selected_customer_id = customer_options[selected_customer]
    if selected_customer_id is not None:
        filtered_orders = [
            order for order in filtered_orders
            if str(get_value(order, "customer_id"))
            == selected_customer_id
        ]
    if fulfillment_filter != "All Methods":
        expected_method = (
            "delivery"
            if fulfillment_filter == "Campus Delivery"
            else "pickup"
        )
        filtered_orders = [
            order for order in filtered_orders
            if str(
                get_value(order, "fulfillment_method", "pickup")
            ).lower() == expected_method
        ]
    if search_query:
        filtered_orders = [
            order for order in filtered_orders
            if (
                search_query in str(
                    get_value(order, "order_number", "")
                ).lower()
                or search_query in str(
                    get_value(order, "username", "")
                ).lower()
                or search_query in str(
                    get_value(order, "email", "")
                ).lower()
            )
        ]
    if date_filter != "All Dates":
        today = datetime.now().date()
        days = {
            "Today": 0,
            "Last 7 Days": 7,
            "Last 30 Days": 30
        }[date_filter]
        filtered_by_date = []
        for order in filtered_orders:
            date_value = get_completion_date(order)
            try:
                order_date = datetime.fromisoformat(
                    str(date_value).replace("Z", "")
                ).date()
                difference = (today - order_date).days
                if 0 <= difference <= days:
                    filtered_by_date.append(order)
            except (ValueError, TypeError):
                continue
        filtered_orders = filtered_by_date
    # ORDER LIST
    st.divider()
    render_section_heading("Completed Order Records")
    st.caption(
        f"{len(filtered_orders)} completed order(s) found."
    )
    if not filtered_orders:
        with st.container(border=True):
            st.subheader("No Completed Orders Found")
            st.write(
                "There are no completed orders matching "
                "your selected filters."
            )
        return
    order_options = {}
    for order in filtered_orders:
        order_id = get_value(order, "order_id")
        order_number = get_value(
            order,
            "order_number",
            f"Order #{order_id}"
        )
        customer_name = get_value(
            order,
            "username",
            "Unknown Customer"
        )
        amount = format_currency(
            get_value(order, "total_cost", 0)
        )
        order_options[
            f"{order_number} • {customer_name} • {amount}"
        ] = order
    selected_order_label = st.selectbox(
        "Select an order to review",
        list(order_options.keys()),
        key="completed_selected_order"
    )
    selected_order = order_options[selected_order_label]
    st.divider()
    # DISPLAY ONLY ONE ORDER
    render_selected_completed_order(selected_order)
