import streamlit as st
from pathlib import Path
from uuid import uuid4
import base64
import re
import html
from database.order_repository import OrderRepository
from database.file_repository import FileRepository
from database.connection import PROJECT_ROOT
from ui.order_communication import (
    render_staff_order_communication,
    customer_approved_proof,
)

# ==================================================
# CONFIGURATION

# ==================================================
GREEN = "#064B36"
MID_GREEN = "#286B46"
LIGHT_GREEN = "#EAF4EC"
PALE_GREEN = "#F3F8F4"
BORDER_GREEN = "#D9E9DC"
UPLOAD_FOLDER = PROJECT_ROOT / "data" / "uploads"
MAX_PROOF_SIZE_MB = 10
PROOF_EXTENSIONS = ["png", "jpg", "jpeg", "webp"]
STATUS_LABELS = {
    "confirmed": "Confirmed",
    "printing": "Printing",
    "awaiting_review": "Awaiting Review",
    "correction_requested": "Reprint Required",
    "ready_for_pickup": "Ready for Pickup",
    "out_for_delivery": "Out for Delivery",
    "completed": "Completed",
}
STATUS_OPTIONS = {
    "All Active Orders": None,
    "Confirmed": "confirmed",
    "Printing": "printing",
    "Awaiting Review": "awaiting_review",
    "Reprint Required": "correction_requested",
    "Ready for Pickup": "ready_for_pickup",
    "Out for Delivery": "out_for_delivery",
}
ACTIVE_STATUSES = [
    "confirmed",
    "printing",
    "awaiting_review",
    "correction_requested",
    "ready_for_pickup",
    "out_for_delivery",
]

# ==================================================
# GENERAL HELPERS

# ==================================================

def get_value(data, key, default=None):
    try:
        value = data[key]
        return default if value is None else value
    except (KeyError, IndexError, TypeError):
        return default

def get_logged_in_staff_id(user=None):
    staff_id = get_value(user, "user_id")
    if staff_id is None:
        current_user = st.session_state.get("current_user")
        staff_id = get_value(current_user, "user_id")
    if staff_id is None:
        staff_id = st.session_state.get("user_id")
    return staff_id

def format_currency(value):
    try:
        return f"₱{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₱0.00"

def safe_filename(filename):
    name = Path(filename).name
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "_", name)
    return cleaned or "print_proof"

def safe_text(value):
    return html.escape(str(value if value is not None else "Not available"))
# ==================================================
# SECTION HEADINGS
# ==================================================

def render_section_heading(title):
    """Render a clean section heading without decorative icons."""
    st.markdown(
        f"""
        <div class="assigned-section-heading">
            <span class="assigned-section-marker"></span>
            <span class="assigned-section-title">{safe_text(title)}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
# ==================================================
# BACKGROUND IMAGE

# ==================================================

def get_background_image():
    candidates = [
        PROJECT_ROOT / "assets" / "backgrounds" / "login_background.png",
        PROJECT_ROOT / "assets" / "login_background.png",
        PROJECT_ROOT / "assets" / "images" / "login_background.png",
        PROJECT_ROOT / "login_background.png",
    ]
    for image_path in candidates:
        if image_path.is_file():
            encoded = base64.b64encode(
                image_path.read_bytes()
            ).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    return None
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
        .stApp {{
            background-color: #F5F8F5;
        }}
        /* PAGE HEADER */
        .st-key-assigned_orders_header {{
            background-image: {header_background};
            background-size: cover;
            background-position: center;
            border: 1px solid #D9E9DC;
            border-radius: 18px;
            padding: 30px 35px;
            margin-bottom: 25px;
            box-shadow: 0 5px 18px rgba(6,75,54,0.10);
        }}
        .st-key-assigned_orders_header h1 {{
            color: #FFFFFF !important;
            font-size: 34px !important;
            font-weight: 800 !important;
            margin-bottom: 8px;
        }}
        .st-key-assigned_orders_header p {{
            color: #E4F2E8 !important;
        }}
        .st-key-assigned_orders_header
        [data-testid="stCaptionContainer"] p {{
            color: #FFFFFF !important;
            font-weight: 700;
            letter-spacing: 1.3px;
        }}
        /* GENERAL SECTION CONTAINERS */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: #FFFFFF !important;
            border: 1px solid #D9E9DC !important;
            border-radius: 15px !important;
        }}
        /* SECTION HEADINGS */
        .assigned-section-heading {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0 0 14px 0;
            padding: 2px 0 10px;
            border-bottom: 1px solid #E5EEE7;
        }}
        .assigned-section-marker {{
            display: inline-block;
            width: 3px;
            height: 21px;
            flex: 0 0 3px;
            border-radius: 6px;
            background: #286B46;
        }}
        .assigned-section-title {{
            color: #123F30;
            font-size: 18px;
            font-weight: 700;
            line-height: 1.25;
            letter-spacing: -0.2px;
            margin: 0;
            padding: 0;
        }}
        /* PAGE SUBHEADINGS */
        h2, h3 {{
            color: #123F30 !important;
            font-weight: 700 !important;
            letter-spacing: -0.3px;
            line-height: 1.25 !important;
            margin-top: 0.35rem !important;
            margin-bottom: 0.35rem !important;
        }}
        [data-testid="stSubheader"] {{
            margin-bottom: 0.15rem;
        }}
        [data-testid="stCaptionContainer"] {{
            margin-top: 0 !important;
        }}
        [data-testid="stCaptionContainer"] p {{
            color: #718579;
            font-size: 13px;
            line-height: 1.5;
        }}
        /* INFORMATION CARDS */
        div[class*="st-key-assigned_info_"] {{
            background-color: #EAF4EC !important;
            border: 1px solid #C5DDCB !important;
            border-radius: 12px !important;
            padding: 12px 15px !important;
            min-height: 82px;
            margin-bottom: 8px;
        }}
        div[class*="st-key-assigned_info_"]
        [data-testid="stCaptionContainer"] p {{
            color: #668575 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            margin-bottom: 7px !important;
        }}
        div[class*="st-key-assigned_info_"] p {{
            color: #064B36 !important;
            font-size: 15px !important;
        }}
        div[class*="st-key-assigned_info_"] strong {{
            color: #064B36 !important;
            font-weight: 750 !important;
        }}
        /* SUMMARY CARDS */
        div[class*="st-key-summary_"] {{
            background-color: #EAF4EC !important;
            border: 1px solid #C5DDCB !important;
            border-radius: 13px !important;
            padding: 13px !important;
            min-height: 105px;
        }}
        .assigned-summary-label {{
            color: #668575;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .assigned-summary-number {{
            color: #064B36;
            font-size: 31px;
            font-weight: 750;
            line-height: 1.2;
            letter-spacing: -0.5px;
        }}
        /* STATUS BADGE */
        .assigned-status-badge {{
            display: inline-block;
            border-radius: 30px;
            padding: 8px 15px;
            font-size: 11px;
            font-weight: 750;
            letter-spacing: 0.5px;
            border: 1px solid #C5DDCB;
        }}
        /* PROOF UPLOAD */
        div[class*="st-key-assigned_proof_upload_"] {{
            background-color: #F1F8F3 !important;
            border: 1px dashed #A9CDB3 !important;
            border-radius: 13px !important;
            padding: 16px !important;
        }}
        [data-testid="stFileUploader"] {{
            background-color: #F1F8F3;
            border: 1px solid #D9E9DC;
            border-radius: 10px;
            padding: 10px;
        }}
        /* BUTTONS */
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
        div.stButton > button {{
            border-radius: 10px;
            min-height: 42px;
        }}
        div.stDownloadButton > button {{
            background-color: #F1F8F3;
            color: #064B36;
            border: 1px solid #D9E9DC;
            border-radius: 9px;
        }}
        /* SELECTBOX */
        div[data-baseweb="select"] > div {{
            background-color: #F1F8F3;
            border-color: #D9E9DC;
            border-radius: 9px;
        }}
        /* TEXT INPUT */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {{
            background-color: #F1F8F3;
            border-color: #D9E9DC;
            border-radius: 9px;
        }}
        h2, h3 {{
            color: #064B36 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
# ==================================================
# PAGE HEADER

# ==================================================

def render_assigned_header():
    with st.container(key="assigned_orders_header"):
        st.caption("PASAPRINT • STAFF PORTAL")
        st.title("Assigned Orders")
        st.write(
            "Manage your confirmed printing orders, update production "
            "progress, and prepare completed requests for fulfillment."
        )
# ==================================================
# INFORMATION BOXES

# ==================================================

def render_info_box(label, value, order_id):
    cleaned_label = re.sub(
        r"[^a-zA-Z0-9_]",
        "_",
        label.lower()
    )
    key = f"assigned_info_{order_id}_{cleaned_label}"
    with st.container(key=key, border=True):
        st.caption(label)
        st.markdown(
            f"**{safe_text(value)}**",
            unsafe_allow_html=True
        )
# ==================================================
# CUSTOMER INFORMATION

# ==================================================

def render_customer_information(order):
    order_id = get_value(order, "order_id")
    render_section_heading("Customer Information")
    customer_name = get_value(
        order,
        "username",
        "Customer"
    )
    customer_email = get_value(
        order,
        "email",
        "Not available"
    )
    customer_id = get_value(
        order,
        "customer_id",
        "N/A"
    )
    col1, col2 = st.columns(2)
    with col1:
        render_info_box(
            "Customer Name",
            customer_name,
            order_id
        )
    with col2:
        render_info_box(
            "Email Address",
            customer_email,
            order_id
        )
    render_info_box(
        "Customer ID",
        customer_id,
        order_id
    )
# ==================================================
# PRINTING DETAILS

# ==================================================

def render_printing_details(order):
    order_id = get_value(order, "order_id")
    render_section_heading("Printing Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_info_box(
            "Paper Size",
            get_value(order, "paper_size", "N/A"),
            order_id
        )
    with col2:
        render_info_box(
            "Print Color",
            get_value(order, "color_mode", "N/A"),
            order_id
        )
    with col3:
        render_info_box(
            "Print Sides",
            get_value(order, "print_sides", "N/A"),
            order_id
        )
    with col1:
        render_info_box(
            "Number of Copies",
            get_value(order, "copies", 1),
            order_id
        )
    with col2:
        render_info_box(
            "Total Pages",
            get_value(order, "total_pages", 0),
            order_id
        )
    with col3:
        render_info_box(
            "Total Amount",
            format_currency(get_value(order, "total_cost", 0)),
            order_id
        )
# ==================================================
# FULFILLMENT DETAILS

# ==================================================

def render_fulfillment_details(order):
    order_id = get_value(order, "order_id")
    fulfillment = str(
        get_value(order, "fulfillment_method", "pickup")
    ).lower()
    render_section_heading("Fulfillment Details")
    render_info_box(
        "Fulfillment Method",
        fulfillment.title(),
        order_id
    )
    if fulfillment == "delivery":
        col1, col2, col3 = st.columns(3)
        with col1:
            render_info_box(
                "Building",
                get_value(order, "building", "N/A"),
                order_id
            )
        with col2:
            render_info_box(
                "Floor",
                get_value(order, "floor", "N/A"),
                order_id
            )
        with col3:
            render_info_box(
                "Room",
                get_value(order, "room", "N/A"),
                order_id
            )
        render_info_box(
            "Delivery Notes",
            get_value(
                order,
                "delivery_notes",
                "No additional instructions."
            ),
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
    st.write(
        notes if notes else "No additional instructions."
    )
# ==================================================
# UPLOADED CUSTOMER DOCUMENTS

# ==================================================

def render_uploaded_files(order_id):
    render_section_heading("Uploaded Files")
    file_repository = FileRepository()
    try:
        uploaded_files = file_repository.get_files_by_type(
            order_id,
            "document"
        )
    except Exception as error:
        st.error(f"Unable to retrieve files: {error}")
        return
    if not uploaded_files:
        st.info("No uploaded documents were found for this order.")
        return
    for index, uploaded_file in enumerate(uploaded_files):
        original_name = get_value(
            uploaded_file,
            "original_filename",
            f"Document {index + 1}"
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
            st.caption("Customer document")
        with col2:
            if file_path and file_path.is_file():
                st.download_button(
                    "Download",
                    data=file_path.read_bytes(),
                    file_name=original_name,
                    key=f"assigned_document_{order_id}_{index}",
                    width="stretch"
                )
            else:
                st.warning("File unavailable.")
# ==================================================
# OPTIONAL PRINT PROOF UPLOAD

# ==================================================

def render_proof_upload(order, user):
    order_id = get_value(order, "order_id")
    staff_id = get_logged_in_staff_id(user)
    render_section_heading("Print Preview / Customer Proof")
    st.caption(
        "Optional: Upload photos of the finished printed output "
        "if the customer requests a preview."
    )
    with st.container(
        key=f"assigned_proof_upload_{order_id}",
        border=True
    ):
        st.markdown("**Upload Print Proof Photos**")
        st.write(
            "You can upload one or more photos of the finished "
            "printed documents. These will be saved as customer proofs."
        )
        uploaded_proofs = st.file_uploader(
            "Choose image files",
            type=PROOF_EXTENSIONS,
            accept_multiple_files=True,
            key=f"assigned_proofs_{order_id}",
            help="PNG, JPG, JPEG, or WEBP. Maximum 10 MB per image."
        )
        if not uploaded_proofs:
            st.caption(
                "No photos selected. You can skip this section."
            )
            return
        valid_proofs = []
        for uploaded_file in uploaded_proofs:
            extension = Path(uploaded_file.name).suffix.lower()
            if extension not in (
                ".png", ".jpg", ".jpeg", ".webp"
            ):
                st.error(
                    f"{uploaded_file.name} has an unsupported format."
                )
                continue
            if uploaded_file.size > MAX_PROOF_SIZE_MB * 1024 * 1024:
                st.error(
                    f"{uploaded_file.name} exceeds the "
                    f"{MAX_PROOF_SIZE_MB} MB limit."
                )
                continue
            valid_proofs.append(uploaded_file)
        if not valid_proofs:
            return
        st.caption(
            f"{len(valid_proofs)} photo(s) selected."
        )
        with st.expander("Preview selected photos"):
            for uploaded_file in valid_proofs:
                st.image(
                    uploaded_file,
                    caption=uploaded_file.name,
                    width="stretch"
                )
        if st.button(
            "Upload Proof Photos",
            type="primary",
            width="stretch",
            key=f"save_proofs_{order_id}"
        ):
            if staff_id is None:
                st.error("Unable to identify the staff account.")
                return
            UPLOAD_FOLDER.mkdir(
                parents=True,
                exist_ok=True
            )
            file_repository = FileRepository()
            saved_paths = []
            saved_records = []
            try:
                for uploaded_file in valid_proofs:
                    original_name = safe_filename(
                        uploaded_file.name
                    )
                    stored_name = (
                        f"{uuid4().hex}_{original_name}"
                    )
                    saved_path = UPLOAD_FOLDER / stored_name
                    saved_path.write_bytes(
                        uploaded_file.getvalue()
                    )
                    saved_paths.append(saved_path)
                    relative_path = str(
                        saved_path.relative_to(PROJECT_ROOT)
                    )
                    file_id = file_repository.add_file(
                        order_id=order_id,
                        uploaded_by=staff_id,
                        file_type="proof",
                        original_filename=original_name,
                        stored_filename=stored_name,
                        file_path=relative_path,
                        page_count=None
                    )
                    saved_records.append(file_id)
                st.success(
                    "Print proof photos uploaded successfully!"
                )
                st.rerun()
            except Exception as error:
                for file_id in saved_records:
                    try:
                        file_repository.delete_file_record(file_id)
                    except Exception:
                        pass
                for saved_path in saved_paths:
                    try:
                        saved_path.unlink(missing_ok=True)
                    except OSError:
                        pass
                st.error(
                    f"Unable to upload proof photos: {error}"
                )
# ==================================================
# ORDER STATUS UPDATE

# ==================================================

def update_status(
    repository,
    order,
    user,
    new_status,
    notes=None
):
    order_id = get_value(order, "order_id")
    staff_id = get_logged_in_staff_id(user)
    if staff_id is None:
        st.error("Unable to identify the logged-in staff account.")
        return
    try:
        repository.update_order_status(
            order_id=order_id,
            new_status=new_status,
            changed_by=staff_id,
            notes=notes
        )
        st.success(
            f"Order updated to "
            f"{STATUS_LABELS.get(new_status, new_status)}!"
        )
        st.rerun()
    except Exception as error:
        st.error(
            f"Unable to update order status: {error}"
        )
# ==================================================
# ORDER ACTIONS

# ==================================================

def render_order_actions(order, user, repository):
    order_id = get_value(order, "order_id")
    status = get_value(order, "status")
    fulfillment = str(
        get_value(order, "fulfillment_method", "pickup")
    ).lower()
    render_section_heading("Order Actions")
    notes = st.text_area(
        "Staff Notes (Optional)",
        placeholder="Add a note about this order...",
        key=f"assigned_notes_{order_id}",
        height=80
    )
    if status == "confirmed":
        st.info(
            "This order has been confirmed and is ready for printing."
        )
        if st.button(
            "Start Printing",
            type="primary",
            width="stretch",
            key=f"start_printing_{order_id}"
        ):
            update_status(
                repository,
                order,
                user,
                "printing",
                notes
            )
    elif status == "printing":
        st.info(
            "Once printing is finished, send this order for quality checking."
        )
        if st.button(
            "Send to Quality Review",
            type="primary",
            width="stretch",
            key=f"quality_review_{order_id}"
        ):
            update_status(
                repository,
                order,
                user,
                "awaiting_review",
                notes
            )
    elif status == "awaiting_review":
        st.info(
            "Check the printed documents for missing pages, "
            "incorrect colors, alignment, and print quality. "
            "You may upload optional proof photos above."
        )

        proof_approved = customer_approved_proof(order_id)

        if not proof_approved:
            st.warning(
                "Waiting for the customer to review and approve "
                "the uploaded proof photos."
            )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Mark Reprint Required",
                width="stretch",
                key=f"reprint_{order_id}",
            ):
                update_status(
                    repository,
                    order,
                    user,
                    "correction_requested",
                    notes,
                )

        with col2:
            if proof_approved:
                if fulfillment == "delivery":
                    button_label = "Ready for Delivery"
                    next_status = "out_for_delivery"
                else:
                    button_label = "Ready for Pickup"
                    next_status = "ready_for_pickup"

                if st.button(
                    button_label,
                    type="primary",
                    width="stretch",
                    key=f"fulfillment_{order_id}",
                ):
                    update_status(
                        repository,
                        order,
                        user,
                        next_status,
                        notes,
                    )
            else:
                st.button(
                    "Waiting for Approval",
                    disabled=True,
                    width="stretch",
                    key=f"waiting_approval_{order_id}",
                )

    elif status == "correction_requested":
        st.info(
            "This order requires another printing attempt."
        )
        if st.button(
            "Resume Printing",
            type="primary",
            width="stretch",
            key=f"resume_printing_{order_id}"
        ):
            update_status(
                repository,
                order,
                user,
                "printing",
                notes
            )
    elif status == "ready_for_pickup":
        st.success(
            "This order is ready for the customer to collect."
        )
        if st.button(
            "Mark as Completed",
            type="primary",
            width="stretch",
            key=f"complete_pickup_{order_id}"
        ):
            update_status(
                repository,
                order,
                user,
                "completed",
                notes
            )
    elif status == "out_for_delivery":
        st.info(
            "This order is currently out for delivery."
        )
        if st.button(
            "Confirm Delivery / Complete Order",
            type="primary",
            width="stretch",
            key=f"complete_delivery_{order_id}"
        ):
            update_status(
                repository,
                order,
                user,
                "completed",
                notes
            )
# ==================================================
# SELECTED ORDER DISPLAY

# ==================================================

def render_assigned_order(order, user, repository):
    order_id = get_value(order, "order_id")
    order_number = get_value(
        order,
        "order_number",
        f"Order #{order_id}"
    )
    created_at = get_value(
        order,
        "created_at",
        "Not available"
    )
    status = get_value(order, "status", "confirmed")
    status_label = STATUS_LABELS.get(
        status,
        status.replace("_", " ").title()
    )
    status_colors = {
        "confirmed": ("#E2F2E8", "#17633F", "#B9DEC8"),
        "printing": ("#E5F0FA", "#245B8F", "#C5DDF1"),
        "awaiting_review": ("#FFF4D9", "#8A6415", "#F0DDAA"),
        "correction_requested": ("#FCE9E7", "#A33D35", "#EFC8C3"),
        "ready_for_pickup": ("#E2F4F1", "#176D61", "#B8E1D9"),
        "out_for_delivery": ("#EDEAFB", "#5B4A9A", "#D2CBEF"),
        "completed": ("#EDF1EE", "#52645A", "#D4DED7"),
    }
    background, foreground, status_border = status_colors.get(
        status,
        ("#EDF3EF", "#365B46", "#D5E2D9")
    )
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"## {safe_text(order_number)}"
        )
        st.caption(f"Submitted: {created_at}")
    with col2:
        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: flex-end;
                padding-top: 8px;
            ">
                <span class="assigned-status-badge"
                    style="
                        background-color: {background};
                        color: {foreground};
                        border-color: {status_border};
                    ">
                    {safe_text(status_label.upper())}
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
        render_uploaded_files(order_id)
    with st.container(border=True):
        render_proof_upload(order, user)

    render_staff_order_communication(
        order_id=order_id,
        user=user,
    )

    with st.container(border=True):
        render_order_actions(order, user, repository)
# ==================================================
# GET STAFF ASSIGNED ORDERS

# ==================================================

def get_staff_orders(repository, staff_id):
    assigned_orders = []
    seen_order_ids = set()
    for status in ACTIVE_STATUSES:
        orders = repository.get_orders_by_status(status)
        for order in orders:
            assigned_staff_id = get_value(
                order,
                "assigned_staff_id"
            )
            order_id = get_value(
                order,
                "order_id"
            )
            if (
                assigned_staff_id is not None
                and str(assigned_staff_id) == str(staff_id)
                and order_id not in seen_order_ids
            ):
                assigned_orders.append(order)
                seen_order_ids.add(order_id)
    assigned_orders.sort(
        key=lambda order: str(
            get_value(order, "created_at", "")
        ),
        reverse=True
    )
    return assigned_orders
# ==================================================
# SUMMARY CARDS

# ==================================================

def render_summary_card(label, count, card_key):
    with st.container(key=f"summary_{card_key}"):
        st.markdown(
            f"""
            <div class="assigned-summary-label">{safe_text(label)}</div>
            <div class="assigned-summary-number">{count}</div>
            """,
            unsafe_allow_html=True
        )

def render_order_summary(orders):
    counts = {
        "confirmed": 0,
        "printing": 0,
        "awaiting_review": 0,
        "ready_delivery": 0,
    }
    for order in orders:
        status = get_value(order, "status")
        if status == "confirmed":
            counts["confirmed"] += 1
        elif status == "printing":
            counts["printing"] += 1
        elif status == "awaiting_review":
            counts["awaiting_review"] += 1
        elif status in (
            "ready_for_pickup",
            "out_for_delivery"
        ):
            counts["ready_delivery"] += 1
    columns = st.columns(4)
    summary_items = [
        ("Confirmed", counts["confirmed"], "active_orders"),
        ("Printing", counts["printing"], "printingstaff"),
        ("Quality Review", counts["awaiting_review"], "status"),
        ("Ready / Delivery", counts["ready_delivery"], "completed_orders"),
    ]
    for column, (label, count, icon_name) in zip(
        columns,
        summary_items
    ):
        with column:
            render_summary_card(
                label,
                count,
                icon_name
            )
# ==================================================
# MAIN ASSIGNED ORDERS PAGE

# ==================================================

def render_assigned_orders_page(user):
    render_page_styles()
    render_assigned_header()
    repository = OrderRepository()
    staff_id = get_logged_in_staff_id(user)
    if staff_id is None:
        st.error(
            "Unable to identify the logged-in staff account. "
            "Please log out and sign in again."
        )
        return
    try:
        assigned_orders = get_staff_orders(
            repository,
            staff_id
        )
    except Exception as error:
        st.error(
            f"Unable to retrieve assigned orders: {error}"
        )
        return
    # ==================================================
    # SUMMARY AND FILTERS
    # ==================================================
    with st.container(border=True):
        st.subheader("My Assigned Orders")
        st.caption(
            f"You currently have {len(assigned_orders)} "
            f"active order(s) assigned to you."
        )
        render_order_summary(assigned_orders)
        st.divider()
        # CUSTOMER FILTER
        customer_options = {}
        for order in assigned_orders:
            customer_id = get_value(order, "customer_id")
            if customer_id is None:
                continue
            customer_name = get_value(
                order,
                "username",
                "Unknown Customer"
            )
            customer_email = get_value(
                order,
                "email",
                ""
            )
            customer_label = (
                f"{customer_name} ({customer_email})"
                if customer_email
                else customer_name
            )
            customer_options[str(customer_id)] = customer_label
        customer_labels = {
            "All Customers": None
        }
        for customer_id, label in customer_options.items():
            customer_labels[label] = customer_id
        customer_choices = list(customer_labels.keys())
        selected_customer = st.selectbox(
            "Filter by Customer",
            customer_choices,
            key="assigned_customer_filter"
        )
        # STATUS FILTER
        selected_filter = st.selectbox(
            "Filter by Order Status",
            options=list(STATUS_OPTIONS.keys()),
            key="assigned_order_filter"
        )
        selected_status = STATUS_OPTIONS[selected_filter]
        # SEARCH
        search_query = st.text_input(
            "Search Orders",
            placeholder="Search order number, customer name, or email...",
            key="assigned_order_search"
        ).strip().lower()
    # ==================================================
    # APPLY FILTERS
    # ==================================================
    filtered_orders = assigned_orders
    selected_customer_id = customer_labels[selected_customer]
    if selected_customer_id is not None:
        filtered_orders = [
            order for order in filtered_orders
            if str(
                get_value(order, "customer_id")
            ) == str(selected_customer_id)
        ]
    if selected_status is not None:
        filtered_orders = [
            order for order in filtered_orders
            if get_value(order, "status") == selected_status
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
    # ==================================================
    # ORDER SELECTOR
    # ==================================================
    st.divider()
    render_section_heading("Order List")
    st.caption(
        f"{len(filtered_orders)} matching order(s). "
        "Select one order to view its details."
    )
    if not filtered_orders:
        with st.container(border=True):
            st.subheader("No Orders Found")
            st.write(
                "No orders match your selected customer, "
                "status, or search keyword."
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
        status = get_value(
            order,
            "status",
            "confirmed"
        )
        label = (
            f"{order_number}  |  "
            f"{customer_name}  |  "
            f"{STATUS_LABELS.get(status, status.title())}"
        )
        order_options[label] = order
    selected_order_label = st.selectbox(
        "Select an Order",
        options=list(order_options.keys()),
        key="assigned_selected_order"
    )
    selected_order = order_options[selected_order_label]
    # ==================================================
    # DISPLAY ONE SELECTED ORDER
    # ==================================================
    st.divider()
    render_assigned_order(
        selected_order,
        user,
        repository
    )
# ==================================================
# COMPATIBILITY WITH APPLICATION ROUTER

# ==================================================
render_assigned_orders = render_assigned_orders_page
