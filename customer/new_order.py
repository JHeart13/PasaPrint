from datetime import datetime
from io import BytesIO
import base64
from pathlib import Path
from uuid import uuid4
import re

import streamlit as st
from pypdf import PdfReader

from database.connection import get_connection, PROJECT_ROOT
from database.order_repository import OrderRepository
from database.file_repository import FileRepository
from database.settings_repository import SettingsRepository


UPLOAD_FOLDER = PROJECT_ROOT / "data" / "uploads"
ICON_FOLDER = PROJECT_ROOT / "assets" / "icons"
WELCOME_BACKGROUND = PROJECT_ROOT / "assets" / "backgrounds" / "login_background.png"
MAX_FILES = 20
MAX_FILE_SIZE_MB = 20

DEFAULT_PRICES = {
    "a4_black_white": 2.00,
    "a4_color": 5.00,
    "letter_black_white": 2.00,
    "letter_color": 5.00,
    "legal_black_white": 3.00,
    "legal_color": 7.00,
    "long_black_white": 3.00,
    "long_color": 6.00,
    "a3_black_white": 5.00,
    "a3_color": 12.00,
    "handling_fee": 2.50,
    "delivery_fee": 0.00,
    "pickup_fee": 0.00,
}

PICKUP_LOCATIONS = [
    "Arlegui Campus Entrance Gate",
    "Casal Campus Entrance Gate",
    "Casal Library",
    "Arlegui Library",
    "Casal Study Area",
    "Alregui Study Area",
]

DELIVERY_AREAS = [
    "Arlegui Building",
    "Founders Building",
    "Casal Building",
    "PE Center",
]


def _get_prices():
    """Load configurable prices from the existing settings table."""
    repository = SettingsRepository()
    prices = {}

    for key, default in DEFAULT_PRICES.items():
        try:
            prices[key] = float(repository.get_setting(key, str(default)))
        except (TypeError, ValueError):
            prices[key] = default

    return prices


def _read_pdf(uploaded_file):
    """Read a PDF and return its page count."""
    try:
        pdf = PdfReader(BytesIO(uploaded_file.getvalue()))

        if pdf.is_encrypted:
            raise ValueError("Password-protected PDFs are not supported.")

        page_count = len(pdf.pages)

        if page_count < 1:
            raise ValueError("The PDF contains no pages.")

        return page_count

    except ValueError:
        raise
    except Exception as error:
        raise ValueError(
            f"Could not read {uploaded_file.name}. Please upload a valid PDF."
        ) from error


def _money(amount):
    return f"₱{amount:,.2f}"


def _safe_filename(filename):
    """Keep the original extension while avoiding unsafe path characters."""
    name = Path(filename).name
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "_", name)
    return cleaned or "document.pdf"


def _asset_data_uri(path):
    """Return an embedded data URI for a supported image asset."""
    path = Path(path)
    if not path.is_file():
        return ""

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    mime_type = mime_types.get(path.suffix.lower())
    if not mime_type:
        return ""

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _welcome_background_css():
    """Use the same subtle patterned background as the customer dashboard."""
    image_uri = _asset_data_uri(WELCOME_BACKGROUND)
    if not image_uri:
        return "background-color: #E3F1E7;"

    return (
        "background-image: "
        "linear-gradient(rgba(227,241,231,0.88), rgba(227,241,231,0.88)), "
        f"url('{image_uri}'); "
        "background-size: cover; "
        "background-position: center; "
        "background-repeat: no-repeat;"
    )


def _inject_styles():
    banner_background = _welcome_background_css()
    st.markdown(
        f"""
        <style>
        .pp-order-page {{
            color: #064B36;
        }}

        .pp-order-banner {{
            {banner_background}
            border: 1px solid #D0E6D5;
            border-radius: 16px;
            padding: 22px 26px;
            margin-bottom: 18px;
            box-sizing: border-box;
        }}

        .pp-order-banner h1 {{
            color: #064B36;
            font-size: clamp(1.6rem, 2.5vw, 2.4rem);
            font-weight: 800;
            margin: 0;
        }}

        .pp-order-banner p {{
            color: #477B5C;
            margin: 4px 0 0;
        }}

        .pp-order-card {{
            background: white;
            border: 1px solid #E3EEE6;
            border-radius: 14px;
            margin-bottom: 16px;
            overflow: hidden;
        }}

        .pp-order-card-title {{
            color: #286A4B;
            font-size: 1.25rem;
            font-weight: 800;
            padding: 18px 22px;
            border-bottom: 1px solid #E3EEE6;
            display: flex;
            align-items: center;
            gap: 2px;
        }}

        .pp-order-card-body {{
            padding: 20px 22px;
        }}

        .pp-order-upload-note {{
            text-align: center;
            color: #477B5C;
            padding: 10px;
        }}

        .pp-order-total {{
            border-top: 1px solid #DDEBE0;
            padding-top: 18px;
            margin-top: 14px;
            font-size: 1.3rem;
            font-weight: 800;
            color: #064B36;
        }}

        div.stButton > button[kind="primary"] {{
            background: #064B36 !important;
            border: 1px solid #064B36 !important;
            color: white !important;
            border-radius: 10px !important;
            min-height: 48px;
            font-weight: 750 !important;
        }}

        div.stButton > button[kind="primary"]:hover {{
            background: #0A6045 !important;
            border-color: #0A6045 !important;
        }}

        div[data-testid="stFileUploader"] section {{
            border: 2px dashed #6AA477;
            border-radius: 12px;
            background: #FBFDFB;
        }}

        @media (max-width: 700px) {{
            .pp-order-banner {{
                padding: 18px;
            }}

            .pp-order-card-title {{
                padding: 15px;
            }}

            .pp-order-card-body {{
                padding: 15px;
            }}
        }}
        
        /* PasaPrint: replace Streamlit red accents with green */
        .stApp {{
            --pp-primary: #064B36;
            --pp-green: #064B36;
            --pp-green-hover: #0A6045;
            --pp-light-green: #E3F1E7;
        }}

        /* Radio buttons and selected indicators */
        .stApp [data-testid="stRadio"] label div[ data-checked="true" ],
        .stApp [data-testid="stRadio"] input:checked {{
            accent-color: #064B36 !important;
        }}

        /* Checkbox and other native controls */
        .stApp input[type="checkbox"],
        .stApp input[type="radio"] {{
            accent-color: #064B36 !important;
        }}

        /* Sliders */
        .stApp [data-testid="stSlider"] [role="slider"] {{
            background-color: #064B36 !important;
        }}

        /* Focus rings */
        .stApp input:focus,
        .stApp textarea:focus {{
            border-color: #064B36 !important;
            box-shadow: 0 0 0 1px #064B36 !important;
        }}

        /* Primary buttons */
        .stApp button[kind="primary"] {{
            background-color: #064B36 !important;
            border-color: #064B36 !important;
            color: #FFFFFF !important;
        }}

        .stApp button[kind="primary"]:hover {{
            background-color: #0A6045 !important;
            border-color: #0A6045 !important;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


def _card_title(number, title):
    icon_by_title = {
        "Upload Documents": "upload.png",
        "Printing Preferences": None,
        "Delivery Method": "pickup.png",
        "Order Summary": None,
    }
    icon_filename = icon_by_title.get(title)
    icon_uri = _asset_data_uri(ICON_FOLDER / icon_filename) if icon_filename else ""

    icon_html = (
        f'<img src="{icon_uri}" alt="" '
        'style="width:30px;height:30px;object-fit:contain;vertical-align:middle;margin-right:10px;">'
        if icon_uri else ""
    )

    st.markdown(
        f"""
        <div class="pp-order-card-title">
            {icon_html}<span>{number}. {title}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _reset_order_form():
    for key in (
        "pp_order_files",
        "pp_order_review",
        "pp_order_color",
        "pp_order_paper",
        "pp_order_sides",
        "pp_order_copies",
        "pp_order_fulfillment",
        "pp_order_pickup",
        "pp_order_building",
        "pp_order_floor",
        "pp_order_room",
        "pp_order_notes",
    ):
        st.session_state.pop(key, None)


def _submit_order(user, order_data, uploaded_files, page_counts):
    """Save the order and its PDF files."""
    customer_id = user.get("user_id")

    if not customer_id:
        raise ValueError("Your account could not be identified. Please log in again.")

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    order_number = (
        "PP-"
        + datetime.now().strftime("%Y%m%d")
        + "-"
        + uuid4().hex[:6].upper()
    )

    order_data["order_number"] = order_number
    order_data["customer_id"] = customer_id

    order_id = None
    saved_paths = []

    try:
        order_id = OrderRepository().create_order(order_data)

        file_repository = FileRepository()

        for uploaded_file in uploaded_files:
            original_name = _safe_filename(uploaded_file.name)
            stored_name = f"{uuid4().hex}_{original_name}"
            saved_path = UPLOAD_FOLDER / stored_name

            saved_path.write_bytes(uploaded_file.getvalue())
            saved_paths.append(saved_path)

            file_repository.add_file(
                order_id=order_id,
                uploaded_by=customer_id,
                file_type="document",
                original_filename=original_name,
                stored_filename=stored_name,
                file_path=str(saved_path.relative_to(PROJECT_ROOT)),
                page_count=page_counts[uploaded_file.name]
            )

        return order_id, order_number

    except Exception:
        # Remove physical files if the submission fails.
        for path in saved_paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass

        # If file saving failed after order creation, remove the incomplete order.
        if order_id is not None:
            try:
                with get_connection() as connection:
                    connection.execute(
                        "DELETE FROM orders WHERE order_id = ?",
                        (order_id,),
                    )
            except Exception:
                pass

        raise


def render_new_order_page(user):
    """Render the customer Create New Order page."""
    _inject_styles()

    prices = _get_prices()

    st.markdown(
        """
        <div class="pp-order-page">
            <div class="pp-order-banner">
                <h1>Create a New Order</h1>
                <p>Upload your documents and customize your printing preferences.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Step 1: Upload PDFs
    with st.container(border=True):
        _card_title("1", "Upload Documents")

        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            key="pp_order_files",
            help="Upload up to 20 PDF files. Maximum 20 MB per file.",
        )

        valid_files = []
        page_counts = {}
        total_pages = 0

        if uploaded_files:
            if len(uploaded_files) > MAX_FILES:
                st.error(f"You can upload a maximum of {MAX_FILES} files.")
            else:
                for uploaded_file in uploaded_files:
                    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                        st.error(
                            f"{uploaded_file.name} exceeds "
                            f"{MAX_FILE_SIZE_MB} MB."
                        )
                        continue

                    if Path(uploaded_file.name).suffix.lower() != ".pdf":
                        st.error(f"{uploaded_file.name} is not a PDF.")
                        continue

                    try:
                        pages = _read_pdf(uploaded_file)
                        valid_files.append(uploaded_file)
                        page_counts[uploaded_file.name] = pages
                        total_pages += pages

                    except ValueError as error:
                        st.error(str(error))

            if valid_files:
                st.markdown("**Selected documents**")

                for uploaded_file in valid_files:
                    st.write(
                        f"📄 **{uploaded_file.name}** — "
                        f"{page_counts[uploaded_file.name]} page(s)"
                    )

                st.caption(
                    f"{len(valid_files)} file(s) · "
                    f"{total_pages} total page(s) before copies"
                )

    # Step 2: Printing preferences
    with st.container(border=True):
        _card_title("2", "Printing Preferences")

        color_choice = st.radio(
            "Print Color",
            ["Black & White", "Colored"],
            horizontal=True,
            key="pp_order_color",
        )
        color_mode = (
            "black_white"
            if color_choice == "Black & White"
            else "color"
        )

        paper_col, copies_col = st.columns(2)

        with paper_col:
            paper_size = st.selectbox(
                "Paper Size",
                ["A4", "Letter", "Legal", "Long", "A3"],
                key="pp_order_paper",
            )

        with copies_col:
            copies = st.number_input(
                "Copies",
                min_value=1,
                max_value=500,
                value=1,
                step=1,
                key="pp_order_copies",
            )

        print_sides_label = st.radio(
            "Print Sides",
            ["Single-sided", "Double-sided"],
            horizontal=True,
            key="pp_order_sides",
        )
        print_sides = (
            "single"
            if print_sides_label == "Single-sided"
            else "double"
        )

    # Step 3: Delivery
    with st.container(border=True):
        _card_title("3", "Delivery Method")

        fulfillment_label = st.radio(
            "Choose how to receive your prints",
            ["Campus Pickup", "Campus Delivery"],
            horizontal=True,
            key="pp_order_fulfillment",
        )

        fulfillment_method = (
            "pickup"
            if fulfillment_label == "Campus Pickup"
            else "delivery"
        )

        pickup_location = None
        building = None
        floor = None
        room = None
        delivery_notes = None

        if fulfillment_method == "pickup":
            pickup_location = st.selectbox(
                "Choose Pickup Location",
                PICKUP_LOCATIONS,
                key="pp_order_pickup",
            )
        else:
            building_col, floor_col, room_col = st.columns(3)

            with building_col:
                building = st.selectbox(
                    "Building / Area",
                    DELIVERY_AREAS,
                    key="pp_order_building",
                )

            with floor_col:
                floor = st.text_input(
                    "Floor",
                    placeholder="e.g. 3rd floor",
                    key="pp_order_floor",
                )

            with room_col:
                room = st.text_input(
                    "Classroom",
                    placeholder="e.g. A-316",
                    key="pp_order_room",
                )

            delivery_notes = st.text_input(
                "Delivery Remarks / Instructions (Optional)",
                placeholder="Meeting instructions...",
                key="pp_order_notes",
            )

    # Step 4: Calculate the estimate
    paper_price_keys = {
        "A4": "a4",
        "Letter": "letter",
        "Legal": "legal",
        "Long": "long",
        "A3": "a3",
    }
    paper_key = paper_price_keys[paper_size]
    color_key = "black_white" if color_mode == "black_white" else "color"
    price_per_page = prices[f"{paper_key}_{color_key}"]

    printing_subtotal = total_pages * int(copies) * price_per_page
    handling_fee = prices["handling_fee"]
    fulfillment_fee = prices[
        "delivery_fee" if fulfillment_method == "delivery" else "pickup_fee"
    ]
    estimated_total = printing_subtotal + handling_fee + fulfillment_fee

    with st.container(border=True):
        _card_title("4", "Order Summary")

        summary_left, summary_right = st.columns([1.5, 1])

        with summary_left:
            st.write("Printing Subtotal")
            st.write("Handling Fee")
            st.write(
                "Campus Delivery Fee"
                if fulfillment_method == "delivery"
                else "Campus Pickup Fee"
            )

        with summary_right:
            st.write(_money(printing_subtotal))
            st.write(_money(handling_fee))
            st.write(_money(fulfillment_fee))

        st.markdown(
            f"""
            <div class="pp-order-total">
                <span>Estimated Total</span>
                <span style="float:right;">{_money(estimated_total)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "The final amount may be adjusted by printing staff after verification."
        )

        if st.button(
            "Review Order  →",
            type="primary",
            width="stretch",
            key="pp_review_order",
        ):
            errors = []

            if not valid_files:
                errors.append("Upload at least one valid PDF.")
            if len(uploaded_files or []) > MAX_FILES:
                errors.append(f"Upload no more than {MAX_FILES} PDFs.")
            if fulfillment_method == "delivery" and not room.strip():
                errors.append("Enter your classroom for campus delivery.")

            if errors:
                for message in errors:
                    st.error(message)
            else:
                st.session_state["pp_order_review"] = {
                    "order_number_preview": (
                        "PP-" + datetime.now().strftime("%Y%m%d") + "-PENDING"
                    ),
                    "customer_id": user.get("user_id"),
                    "color_mode": color_mode,
                    "paper_size": paper_size,
                    "print_sides": print_sides,
                    "copies": int(copies),
                    "total_pages": total_pages,
                    "price_per_page": price_per_page,
                    "printing_cost": round(printing_subtotal, 2),
                    "handling_fee": handling_fee,
                    "delivery_fee": fulfillment_fee,
                    "total_cost": round(estimated_total, 2),
                    "fulfillment_method": fulfillment_method,
                    "campus": "TIP Manila",
                    "pickup_location": pickup_location,
                    "building": building,
                    "floor": floor,
                    "room": room,
                    "delivery_notes": delivery_notes,
                    "customer_notes": None,
                    "page_counts": page_counts,
                }
                st.rerun()

    # Final review and confirmation
    review = st.session_state.get("pp_order_review")

    if review:
        st.divider()
        st.subheader("Review Your Order")
        st.info(
            "Please check your selected documents and printing preferences "
            "before submitting."
        )

        st.write(f"**Documents:** {len(valid_files)} PDF(s)")
        st.write(f"**Pages:** {review['total_pages']}")
        st.write(f"**Print color:** {color_choice}")
        st.write(f"**Paper size:** {review['paper_size']}")
        st.write(f"**Copies:** {review['copies']}")
        st.write(f"**Print sides:** {print_sides_label}")
        st.write(f"**Method:** {fulfillment_label}")
        st.write(f"**Estimated total:** {_money(review['total_cost'])}")

        confirm_col, cancel_col = st.columns(2)

        with confirm_col:
            if st.button(
                "Confirm & Submit Order",
                type="primary",
                width="stretch",
                key="pp_confirm_order",
            ):
                try:
                    # Existing orders schema stores the service fees in delivery_fee.
                    # The repository update below adds a separate handling_fee field.
                    order_data = {
                        key: value
                        for key, value in review.items()
                        if key not in ("page_counts", "order_number_preview")
                    }

                    order_id, order_number = _submit_order(
                        user,
                        order_data,
                        valid_files,
                        review["page_counts"],
                    )

                    _reset_order_form()
                    st.session_state["customer_page"] = "my_orders"
                    st.session_state["pp_order_success"] = order_number
                    st.rerun()

                except Exception as error:
                    st.error(
                        "We couldn't submit your order. "
                        "Please try again or contact support."
                    )
                    print(
                        "Order submission error: "
                        f"{type(error).__name__}: {error}"
                    )

        with cancel_col:
            if st.button(
                "Back to Editing",
                width="stretch",
                key="pp_cancel_review",
            ):
                st.session_state.pop("pp_order_review", None)
                st.rerun()
