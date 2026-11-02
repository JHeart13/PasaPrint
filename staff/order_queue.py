
import streamlit as st
from pathlib import Path
import base64
import re

from database.order_repository import OrderRepository
from database.file_repository import FileRepository
from database.connection import PROJECT_ROOT


# ==================================================
# COLORS
# ==================================================

GREEN = "#064B36"
GREEN_LIGHT = "#286B46"
BG_LIGHT = "#F1F8F3"
BORDER = "#D9E9DC"


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def get_value(data, key, default=None):
    try:
        return data[key]
    except (KeyError, IndexError, TypeError):
        return default


def format_currency(value):
    try:
        return f"₱{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₱0.00"


def get_background_image():
    candidates = [
        PROJECT_ROOT / "assets" / "backgrounds" / "login_background.png",
        PROJECT_ROOT / "assets" / "login_background.png",
        PROJECT_ROOT / "assets" / "images" / "login_background.png",
        PROJECT_ROOT / "login_background.png",
    ]

    for image_path in candidates:
        if image_path.exists():
            with open(image_path, "rb") as image_file:
                encoded = base64.b64encode(
                    image_file.read()
                ).decode("utf-8")

            return f"data:image/png;base64,{encoded}"

    return None


def make_key(value):
    """Create a safe Streamlit container key."""
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", str(value).lower())
    return f"info_box_{cleaned}"


# ==================================================
# PAGE STYLING
# ==================================================

def render_page_styles():

    background_image = get_background_image()

    if background_image:
        header_background = f"""
            linear-gradient(
                100deg,
                rgba(6, 75, 54, 0.88),
                rgba(6, 75, 54, 0.70)
            ),
            url("{background_image}")
        """
    else:
        header_background = """
            linear-gradient(120deg, #064B36, #286B46)
        """

    st.markdown(
        f"""
        <style>

        /* Main page */

        .stApp {{
            background-color: #F5F8F5;
        }}

        /* Header background */

        .st-key-order_queue_header {{
            background-image: {header_background};
            background-size: cover;
            background-position: center;
            border: 1px solid #D9E9DC;
            border-radius: 18px;
            padding: 30px 35px;
            margin-bottom: 25px;
            box-shadow: 0 5px 18px rgba(6, 75, 54, 0.10);
        }}

        .st-key-order_queue_header h1 {{
            color: #FFFFFF !important;
            font-size: 34px !important;
            font-weight: 800 !important;
            margin-bottom: 8px;
        }}

        .st-key-order_queue_header p {{
            color: #E4F2E8 !important;
        }}

        .st-key-order_queue_header [data-testid="stCaptionContainer"] p {{
            color: #FFFFFF !important;
            font-weight: 700;
            letter-spacing: 1.3px;
        }}

        /* Main section containers */

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: #FFFFFF;
            border: 1px solid #D9E9DC;
            border-radius: 14px;
        }}

        /* Individual light-green information boxes */

        div[class*="st-key-info_box_"] {{
            background-color: #EAF4EC !important;
            border: 1px solid #D9E9DC !important;
            border-radius: 12px !important;
            padding: 12px 15px !important;
            min-height: 78px;
            margin-bottom: 9px;
        }}

        div[class*="st-key-info_box_"] [data-testid="stCaptionContainer"] p {{
            color: #668575 !important;
            font-size: 12px;
            font-weight: 600;
        }}

        div[class*="st-key-info_box_"] p {{
            color: #064B36;
            font-size: 15px;
        }}

        div[class*="st-key-info_box_"] strong {{
            color: #064B36 !important;
        }}

        /* Section headings */

        h2, h3 {{
            color: #064B36 !important;
        }}

        /* Order status */

        .st-key-order_status_badge {{
            background-color: #FFF4D9;
            border-radius: 20px;
            padding: 7px 12px;
        }}

        .st-key-order_status_badge p {{
            color: #956A16 !important;
            font-size: 11px;
            font-weight: 700;
        }}

        /* Green notification containers */

        .st-key-green_notice_files,
        .st-key-green_notice_confirmation {{
            background-color: #EAF4EC !important;
            border: 1px solid #D9E9DC !important;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 12px;
        }}

        .st-key-green_notice_files p,
        .st-key-green_notice_confirmation p {{
            color: #286B46 !important;
        }}

        .st-key-empty_orders {{
            background-color: #F1F8F3;
            border: 1px dashed #C5DDCB;
            border-radius: 12px;
            padding: 20px;
        }}

        /* Buttons */

        div.stButton > button[kind="primary"] {{
            background-color: #064B36;
            color: #FFFFFF;
            border: 1px solid #064B36;
            border-radius: 10px;
            font-weight: 700;
            min-height: 45px;
        }}

        div.stButton > button[kind="primary"]:hover {{
            background-color: #286B46;
            border-color: #286B46;
            color: #FFFFFF;
        }}

        div.stDownloadButton > button {{
            background-color: #F1F8F3;
            color: #064B36;
            border: 1px solid #D9E9DC;
            border-radius: 9px;
        }}

        div.stDownloadButton > button:hover {{
            border-color: #286B46;
            color: #064B36;
        }}

        /* Selectbox */

        div[data-baseweb="select"] > div {{
            background-color: #F1F8F3;
            border-color: #D9E9DC;
            border-radius: 9px;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


# ==================================================
# PAGE HEADER
# ==================================================

def render_order_header():

    with st.container(key="order_queue_header"):

        st.caption("PASAPRINT • STAFF PORTAL")

        st.title("Order Queue")

        st.write(
            "Review incoming printing orders, check uploaded documents, "
            "and confirm requests before processing."
        )


# ==================================================
# INFORMATION BOX
# ==================================================

def render_info_box(label, value):

    key = make_key(label)

    with st.container(key=key):

        st.caption(label)

        st.markdown(
            f"**{value if value is not None else 'Not available'}**"
        )


# ==================================================
# CUSTOMER INFORMATION
# ==================================================

def render_customer_information(order):

    st.subheader("Customer Information")

    # The repository returns users.username and users.email.
    customer_name = get_value(
        order,
        "username",
        get_value(order, "customer_name", "Customer")
    )

    customer_email = get_value(
        order,
        "email",
        get_value(order, "customer_email", "Not available")
    )

    customer_id = get_value(order, "customer_id", "N/A")

    col1, col2 = st.columns(2)

    with col1:
        render_info_box("Customer Name", customer_name)

    with col2:
        render_info_box("Email Address", customer_email)

    render_info_box("Customer ID", customer_id)


# ==================================================
# PRINTING DETAILS
# ==================================================

def render_printing_details(order):

    st.subheader("Printing Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        render_info_box(
            "Paper Size",
            get_value(order, "paper_size", "N/A")
        )

    with col2:
        render_info_box(
            "Print Color",
            get_value(order, "color_mode", "N/A")
        )

    with col3:
        render_info_box(
            "Print Sides",
            get_value(order, "print_sides", "N/A")
        )

    with col1:
        render_info_box(
            "Number of Copies",
            get_value(order, "copies", 1)
        )

    with col2:
        render_info_box(
            "Total Pages",
            get_value(order, "total_pages", 0)
        )

    with col3:
        render_info_box(
            "Total Amount",
            format_currency(get_value(order, "total_cost", 0))
        )


# ==================================================
# FULFILLMENT DETAILS
# ==================================================

def render_fulfillment_details(order):

    st.subheader("Fulfillment Details")

    fulfillment = get_value(
        order,
        "fulfillment_method",
        "pickup"
    )

    render_info_box(
        "Fulfillment Method",
        str(fulfillment).title()
    )

    if fulfillment == "delivery":

        col1, col2, col3 = st.columns(3)

        with col1:
            render_info_box(
                "Building",
                get_value(order, "building", "N/A")
            )

        with col2:
            render_info_box(
                "Floor",
                get_value(order, "floor", "N/A")
            )

        with col3:
            render_info_box(
                "Room",
                get_value(order, "room", "N/A")
            )

        render_info_box(
            "Delivery Notes",
            get_value(
                order,
                "delivery_notes",
                "No additional instructions."
            )
        )

    else:

        col1, col2 = st.columns(2)

        with col1:
            render_info_box(
                "Campus",
                get_value(order, "campus", "N/A")
            )

        with col2:
            render_info_box(
                "Pickup Location",
                get_value(order, "pickup_location", "N/A")
            )

    st.markdown("**Customer Notes**")

    notes = get_value(order, "customer_notes")

    st.write(
        notes if notes else "No additional instructions."
    )


# ==================================================
# UPLOADED FILES
# ==================================================

def render_uploaded_files(order_id):

    st.subheader("Uploaded Files")

    file_repository = FileRepository()

    try:
        uploaded_files = file_repository.get_order_files(order_id)

    except Exception as error:
        st.error(f"Unable to retrieve uploaded files: {error}")
        return

    if not uploaded_files:

        with st.container(key="green_notice_files"):
            st.write("No uploaded files were found for this order.")

        return

    for index, uploaded_file in enumerate(uploaded_files):

        original_name = get_value(
            uploaded_file,
            "original_filename",
            f"Document {index + 1}"
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
            st.caption(f"File type: {str(file_type).title()}")

        with col2:

            if file_path and file_path.exists():

                with open(file_path, "rb") as file:
                    file_data = file.read()

                st.download_button(
                    label="Download",
                    data=file_data,
                    file_name=original_name,
                    key=f"download_{order_id}_{index}",
                    use_container_width=True
                )

            else:
                st.warning("File unavailable.")


# ==================================================
# ORDER CONFIRMATION
# ==================================================

def render_order_confirmation(order, user):

    order_id = get_value(order, "order_id")

    st.subheader("Order Confirmation")

    with st.container(key="green_notice_confirmation"):
        st.write(
            "Review the customer's uploaded documents, printing "
            "specifications, and fulfillment details before confirming."
        )

    if st.button(
        "✓  Confirm Order",
        type="primary",
        use_container_width=True,
        key=f"confirm_order_{order_id}"
    ):

        staff_id = get_value(user, "user_id")

        if staff_id is None:
            staff_id = st.session_state.get("user_id")

        if staff_id is None:
            st.error(
                "Unable to identify the logged-in staff account."
            )
            return

        try:
            repository = OrderRepository()

            repository.confirm_order(order_id, staff_id)

            st.success(
                "Order successfully confirmed and assigned to you!"
            )

            st.rerun()

        except Exception as error:
            st.error(f"Unable to confirm order: {error}")


# ==================================================
# SELECTED ORDER
# ==================================================

def render_selected_order(order, user):

    order_id = get_value(order, "order_id")

    order_number = get_value(
        order,
        "order_number",
        "Order Details"
    )

    created_at = get_value(
        order,
        "created_at",
        "Not available"
    )

    st.write("")

    col1, col2 = st.columns([3, 1])

    with col1:

        st.subheader(order_number)

        st.caption(f"Submitted: {created_at}")

    with col2:

        with st.container(key="order_status_badge"):
            st.caption("AWAITING CONFIRMATION")

    st.write("")

    # Customer Information

    with st.container(border=True):
        render_customer_information(order)

    st.write("")

    # Printing Details

    with st.container(border=True):
        render_printing_details(order)

    st.write("")

    # Fulfillment Details

    with st.container(border=True):
        render_fulfillment_details(order)

    st.write("")

    # Uploaded Files

    with st.container(border=True):
        render_uploaded_files(order_id)

    st.write("")

    # Order Confirmation

    with st.container(border=True):
        render_order_confirmation(order, user)


# ==================================================
# MAIN ORDER QUEUE PAGE
# ==================================================

def render_order_queue_page(user):

    render_page_styles()
    render_order_header()

    repository = OrderRepository()

    try:
        pending_orders = repository.get_orders_by_status("pending")

    except Exception as error:
        st.error(f"Unable to load incoming orders: {error}")
        return

    if pending_orders is None:
        pending_orders = []

    # Incoming Orders

    with st.container(border=True):

        col1, col2 = st.columns([3, 1])

        with col1:

            st.subheader("Incoming Orders")

            st.caption(
                f"{len(pending_orders)} order(s) awaiting confirmation"
            )

        with col2:

            if st.button(
                "↻ Refresh",
                use_container_width=True
            ):
                st.rerun()

        if not pending_orders:

            with st.container(key="empty_orders"):

                st.subheader("No Incoming Orders")

                st.write(
                    "New customer orders will appear here once submitted."
                )

            return

        st.write("**Select an order to review**")

        order_options = {}

        for order in pending_orders:

            order_id = get_value(order, "order_id")

            order_number = get_value(
                order,
                "order_number",
                f"Order #{order_id}"
            )

            customer_name = get_value(
                order,
                "username",
                get_value(order, "customer_name", "Customer")
            )

            total_cost = format_currency(
                get_value(order, "total_cost", 0)
            )

            order_options[order_id] = (
                f"{order_number} • {customer_name} • {total_cost}"
            )

        selected_order_id = st.selectbox(
            "Incoming Orders",
            options=list(order_options.keys()),
            format_func=lambda order_id: order_options[order_id],
            label_visibility="collapsed",
            key="selected_incoming_order"
        )

    # Selected Order

    selected_order = next(
        (
            order for order in pending_orders
            if get_value(order, "order_id") == selected_order_id
        ),
        None
    )

    if selected_order is not None:
        render_selected_order(selected_order, user)
