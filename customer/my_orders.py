from pathlib import Path
from html import escape
import base64

import streamlit as st

from database.order_repository import OrderRepository
from database.file_repository import FileRepository
from ui.order_communication import render_customer_order_communication


def _find_project_root():
    """Find the project folder whether this file is in the root or ui/."""
    current_file = Path(__file__).resolve()

    for parent in current_file.parents:
        if (parent / "assets").is_dir() and (parent / "database").is_dir():
            return parent

    # Fallback for projects whose folders are arranged differently.
    for parent in current_file.parents:
        if (parent / "assets").is_dir():
            return parent

    return current_file.parent


PROJECT_ROOT = _find_project_root()
ICON_FOLDER = PROJECT_ROOT / "assets" / "icons"

# Same faded patterned background used by the Create New Order page.
ORDER_BACKGROUND = PROJECT_ROOT / "assets" / "backgrounds" / "login_background.png"

GREEN = "#064B36"
MID_GREEN = "#286A4B"
LIGHT_GREEN = "#E3F1E7"
PALE_GREEN = "#F3F8F4"
BORDER_GREEN = "#D7E7DB"

STATUS_LABELS = {
    "pending": "Order Submitted",
    "confirmed": "Confirmed by Staff",
    "printing": "Printing",
    "awaiting_review": "Re-checking",
    "correction_requested": "Correction Requested",
    "ready_for_pickup": "Ready for Pickup",
    "out_for_delivery": "Out for Delivery",
    "completed": "Completed",
    "rejected": "Rejected",
    "cancelled": "Cancelled",
}

STATUS_HELP = {
    "pending": "Your order is waiting for staff confirmation.",
    "confirmed": "Staff confirmed your order. Printing will begin soon.",
    "printing": "Your documents are currently being printed.",
    "awaiting_review": (
        "Your printed documents are being checked. "
        "Staff may upload proof for you to review."
    ),
    "correction_requested": (
        "A printing issue was reported. Staff needs to correct the order."
    ),
    "ready_for_pickup": (
        "Your order is ready. Please follow the pickup instructions from staff."
    ),
    "out_for_delivery": (
        "Your order is on its way to the selected campus location."
    ),
    "completed": "Your order has been handed over or delivered.",
    "rejected": (
        "Staff could not accept this order. "
        "Check the reason below or contact support."
    ),
    "cancelled": "This order has been cancelled.",
}

PROGRESS_STEPS = [
    ("pending", "Order Submitted"),
    ("confirmed", "Confirmed"),
    ("printing", "Printing"),
    ("awaiting_review", "Re-checking"),
    ("ready_for_pickup", "Ready / Delivery"),
    ("completed", "Completed"),
]

TERMINAL_STATUSES = {"completed", "rejected", "cancelled"}


def _asset_uri(path):
    """Read an image and embed it as a Base64 data URI."""

    path = Path(path)

    if not path.is_file():
        return ""

    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(path.suffix.lower())

    if not mime_type:
        return ""

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _image_tag(filename, alt, width=48):
    """Create an embedded image tag for an existing icon."""

    image_uri = _asset_uri(ICON_FOLDER / filename)

    if not image_uri:
        return ""

    return (
        f'<img src="{image_uri}" alt="{escape(alt)}" '
        f'style="width:{width}px;height:{width}px;'
        'object-fit:contain;flex-shrink:0;">'
    )


def _background_css():
    """
    Use the same faded, embedded stationery background as new_order.py.
    """

    image_uri = _asset_uri(ORDER_BACKGROUND)

    if not image_uri:
        print(
            "My Orders background not found: "
            f"{ORDER_BACKGROUND}"
        )
        return f"background-color:{LIGHT_GREEN};"

    return (
        "background-image:"
        "linear-gradient("
        "rgba(227,241,231,0.88),"
        "rgba(227,241,231,0.88)"
        "),"
        f"url('{image_uri}');"
        "background-size:cover;"
        "background-position:center;"
        "background-repeat:no-repeat;"
    )


def _inject_styles():
    """Apply the PasaPrint My Orders styling."""

    banner_background = _background_css()

    st.markdown(
        f"""
        <style>
        .pp-orders-page {{
            color: {GREEN};
        }}

        /* My Orders banner: faded stationery background */
        .pp-orders-banner {{
            {banner_background}
            border: 1px solid {BORDER_GREEN};
            border-radius: 18px;
            padding: 28px;
            margin: 0 0 20px 0;
            box-sizing: border-box;
            min-height: 145px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .pp-orders-banner h1 {{
            color: {GREEN};
            font-size: clamp(1.65rem, 2.5vw, 2.2rem);
            font-weight: 800;
            line-height: 1.2;
            margin: 0 0 10px 0;
        }}

        .pp-orders-banner p {{
            color: {MID_GREEN};
            font-size: 0.95rem;
            line-height: 1.6;
            margin: 0;
        }}

        /* Order confirmation card */
        .pp-order-success-card {{
            position: relative;
            overflow: hidden;
            background-color: {PALE_GREEN};
            {banner_background}
            border: 1px solid {BORDER_GREEN};
            border-radius: 18px;
            padding: 22px;
            margin-bottom: 20px;
            box-sizing: border-box;
        }}

        /* Ordinary order details */
        .pp-order-card {{
            background: #FFFFFF;
            border: 1px solid {BORDER_GREEN};
            border-radius: 16px;
            padding: 18px 20px;
            margin-bottom: 12px;
            box-sizing: border-box;
        }}

        .pp-order-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .pp-order-number {{
            color: {GREEN};
            font-size: 1.12rem;
            font-weight: 800;
            overflow-wrap: anywhere;
        }}

        .pp-order-meta {{
            color: #6F9582;
            font-size: 0.88rem;
            margin-top: 4px;
        }}

        .pp-status-pill {{
            display: inline-block;
            border-radius: 999px;
            padding: 6px 11px;
            background: {LIGHT_GREEN};
            color: {GREEN};
            font-size: 0.82rem;
            font-weight: 750;
            border: 1px solid {BORDER_GREEN};
        }}

        .pp-order-detail-label {{
            color: #6F9582;
            font-size: 0.82rem;
            margin-bottom: 3px;
        }}

        .pp-order-detail-value {{
            color: {GREEN};
            font-weight: 700;
            overflow-wrap: anywhere;
        }}

        .pp-success-heading {{
            color: {GREEN};
            font-size: clamp(1.35rem, 2.3vw, 1.8rem);
            font-weight: 800;
            line-height: 1.3;
            margin-bottom: 5px;
        }}

        .pp-success-subtitle {{
            color: {MID_GREEN};
            line-height: 1.5;
        }}

        .pp-success-details {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-top: 20px;
        }}

        .pp-success-detail {{
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 0;
            padding: 12px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(215,231,219,0.9);
            border-radius: 12px;
        }}

        /* Order progress tracker */
        .pp-tracker {{
            background: {LIGHT_GREEN};
            border-radius: 15px;
            padding: 18px 12px;
            margin: 14px 0 18px;
        }}

        .pp-tracker-grid {{
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 5px;
        }}

        .pp-step {{
            text-align: center;
            color: {MID_GREEN};
            font-size: 0.78rem;
        }}

        .pp-step-dot {{
            width: 29px;
            height: 29px;
            border-radius: 50%;
            margin: 0 auto 7px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #FFFFFF;
            border: 2px solid #B9D5C1;
            color: {MID_GREEN};
            font-weight: 800;
            box-sizing: border-box;
        }}

        .pp-step.done .pp-step-dot {{
            background: {MID_GREEN};
            border-color: {MID_GREEN};
            color: #FFFFFF;
        }}

        .pp-step.current .pp-step-dot {{
            background: {GREEN};
            border-color: {GREEN};
            color: #FFFFFF;
            box-shadow: 0 0 0 4px #B9DDBF;
        }}

        .pp-step-label {{
            font-weight: 700;
            line-height: 1.3;
        }}

        .pp-empty {{
            background: #FFFFFF;
            border: 1px solid {BORDER_GREEN};
            border-radius: 16px;
            padding: 30px;
            text-align: center;
        }}

        .pp-empty h3 {{
            color: {GREEN};
            margin-bottom: 6px;
        }}

        /* Responsive layouts */
        @media (max-width: 850px) {{
            .pp-success-details {{
                grid-template-columns: 1fr;
            }}

            .pp-tracker-grid {{
                grid-template-columns: repeat(3, minmax(0, 1fr));
                row-gap: 18px;
            }}
        }}

        @media (max-width: 700px) {{
            .pp-orders-banner {{
                padding: 20px;
                min-height: 125px;
            }}

            .pp-order-card,
            .pp-order-success-card {{
                padding: 15px;
            }}

            .pp-success-detail {{
                padding: 10px;
            }}

            .pp-tracker-grid {{
                grid-template-columns: repeat(3, minmax(0, 1fr));
                row-gap: 18px;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_html(markup):
    """Render HTML without Markdown interpreting blank lines as code/text."""
    if hasattr(st, "html"):
        st.html(markup)
    else:
        # Compatibility fallback for older Streamlit versions.
        st.markdown(markup, unsafe_allow_html=True)


def _money(value):
    try:
        return f"₱{float(value or 0):,.2f}"
    except (TypeError, ValueError):
        return "—"


def _format_date(value):
    value = str(value or "").strip()

    if not value:
        return "Date unavailable"

    return value[:16].replace("T", " · ")


def _status_label(status):
    key = str(status or "pending").strip().lower()
    return STATUS_LABELS.get(key, key.replace("_", " ").title())


def _get_customer_files(order_id):
    return FileRepository().get_order_files(order_id)


def _get_rejection_reason(order):
    try:
        return order["rejection_reason"]
    except (KeyError, IndexError, TypeError):
        return None


def _render_tracker(status, fulfillment_method):
    status = str(status or "pending").lower()

    if status in TERMINAL_STATUSES:
        if status == "completed":
            st.success("This order has been completed.")
        elif status == "rejected":
            st.error("This order was rejected.")
        else:
            st.warning("This order was cancelled.")
        return

    steps = list(PROGRESS_STEPS)

    if fulfillment_method == "delivery":
        steps[4] = ("out_for_delivery", "Out for Delivery")

    current_index = 0

    if status == "correction_requested":
        current_index = 3
    else:
        for index, (step_status, _) in enumerate(steps):
            if step_status == status:
                current_index = index
                break

    html_steps = []

    for index, (step_status, label) in enumerate(steps):
        if status == "correction_requested" and index == 3:
            done = False
            current = True
        else:
            done = index < current_index
            current = index == current_index

        classes = "pp-step"

        if done:
            classes += " done"

        if current:
            classes += " current"

        marker = "✓" if done else str(index + 1)

        html_steps.append(
            f'<div class="{classes}">'
            f'<div class="pp-step-dot">{marker}</div>'
            f'<div class="pp-step-label">{escape(label)}</div>'
            "</div>"
        )

    _render_html(
        '<div class="pp-tracker">'
        '<div class="pp-tracker-grid">'
        + "".join(html_steps)
        + "</div></div>"
    )


def _render_order_files(order_id):
    try:
        files = _get_customer_files(order_id)
    except Exception as error:
        print(
            f"Could not load files for order {order_id}: "
            f"{type(error).__name__}: {error}"
        )
        st.caption("Order files could not be loaded right now.")
        return

    documents = [
        item for item in files
        if item["file_type"] == "document"
    ]

    proofs = [
        item for item in files
        if item["file_type"] == "proof"
    ]

    with st.expander(
        f"Documents and proof ({len(documents)} document(s), "
        f"{len(proofs)} proof file(s))"
    ):
        if documents:
            st.markdown("**Uploaded documents**")

            for item in documents:
                try:
                    page_count = item["page_count"]
                except (KeyError, IndexError, TypeError):
                    page_count = None
                page_text = (
                    f" · {page_count} page(s)"
                    if page_count
                    else ""
                )

                st.write(
                    f"📄 {item['original_filename']}{page_text}"
                )

        if proofs:
            st.markdown("**Printing proof from staff**")

            for item in proofs:
                try:
                    stored_path = item["file_path"]
                except (KeyError, IndexError, TypeError):
                    stored_path = ""
                file_path = Path(str(stored_path or ""))

                if not file_path.is_absolute():
                    file_path = PROJECT_ROOT / file_path

                st.write(f"**{item['original_filename']}**")

                if not file_path.is_file():
                    st.caption(
                        "The proof record exists, but the file "
                        "could not be found on this device."
                    )
                    continue

                suffix = file_path.suffix.lower()

                if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
                    st.image(
                        str(file_path),
                        width="stretch",
                    )
                elif suffix in {".mp4", ".webm", ".mov"}:
                    st.video(str(file_path))
                else:
                    st.caption(
                        "This proof format cannot be previewed here."
                    )


def _render_status_history(order_id):
    try:
        history = OrderRepository().get_status_history(order_id)
    except Exception as error:
        print(
            f"Could not load order history {order_id}: "
            f"{type(error).__name__}: {error}"
        )
        return

    if not history:
        return

    with st.expander("Status history"):
        for item in history:
            changed_at = _format_date(item["changed_at"])
            new_status = _status_label(item["new_status"])
            changed_by = item["username"] or "System"
            notes = item["notes"]

            st.markdown(f"**{new_status}** · {changed_at}")
            st.caption(f"Updated by {changed_by}")

            if notes:
                st.write(notes)

            st.divider()


def render_my_orders_page(user):
    """Render the customer's order history and details."""

    _inject_styles()

    customer_id = user.get("user_id") if user else None

    if customer_id is None:
        st.error(
            "Your account could not be identified. Please log in again."
        )
        return

    # The banner uses the same faded pattern as Create New Order.
    _render_html(
        """
        <div class="pp-orders-page pp-orders-banner">
            <h1>My Orders</h1>
            <p>Track your printing requests, check their progress, and review staff proof.</p>
        </div>
        """
    )

    # Display the confirmation after a successful submission.
    success_order = st.session_state.pop("pp_order_success", None)

    if success_order:
        success_icon = _image_tag("bigcheck.png", "Success", 58)
        number_icon = _image_tag("ordernumber.png", "Order number", 44)
        date_icon = _image_tag("data_time.png", "Date and time", 44)
        status_icon = _image_tag("status.png", "Order status", 44)

        _render_html(
            f"""
            <div class="pp-order-success-card">
                <div style="
                    display:flex;
                    align-items:center;
                    gap:14px;
                    flex-wrap:wrap;
                ">
                    {success_icon}
                    <div style="flex:1;min-width:200px;">
                        <div class="pp-success-heading">
                            Order Placed Successfully!
                        </div>
                        <div class="pp-success-subtitle">
                            Your printing request has been received.
                            We'll start processing it shortly.
                        </div>
                    </div>
                </div>

                <div class="pp-success-details">
                    <div class="pp-success-detail">
                        {number_icon}
                        <div>
                            <div class="pp-order-detail-label">
                                Order Number
                            </div>
                            <div class="pp-order-detail-value">
                                {escape(str(success_order))}
                            </div>
                        </div>
                    </div>

                    <div class="pp-success-detail">
                        {date_icon}
                        <div>
                            <div class="pp-order-detail-label">
                                Submitted
                            </div>
                            <div class="pp-order-detail-value">
                                Just now
                            </div>
                        </div>
                    </div>

                    <div class="pp-success-detail">
                        {status_icon}
                        <div>
                            <div class="pp-order-detail-label">
                                Current Status
                            </div>
                            <div class="pp-order-detail-value">
                                Pending Confirmation
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        )

    # Retrieve orders belonging to this customer only.
    try:
        orders = OrderRepository().get_customer_orders(customer_id)
    except Exception as error:
        print(
            f"My Orders database error: "
            f"{type(error).__name__}: {error}"
        )
        st.error(
            "We couldn't load your orders. Please refresh and try again."
        )
        return

    if not orders:
        _render_html(
            """
            <div class="pp-empty">
                <h3>No orders yet</h3>
                <p>
                    Your printing orders will appear here after
                    you submit your first request.
                </p>
            </div>
            """
        )

        if st.button(
            "Create your first order",
            type="primary",
            key="pp_empty_create_order",
        ):
            st.session_state["customer_page"] = "new_order"
            st.rerun()

        return

    statuses = sorted(
        {
            str(order["status"] or "pending").lower()
            for order in orders
        }
    )

    filter_col, refresh_col = st.columns(
        [4, 1],
        vertical_alignment="bottom",
    )

    with filter_col:
        filter_options = ["All orders"] + [
            _status_label(status)
            for status in statuses
        ]

        chosen_filter = st.selectbox(
            "Filter orders",
            filter_options,
            key="pp_my_orders_filter",
        )

    with refresh_col:
        if st.button(
            "Refresh",
            width="stretch",
            key="pp_refresh_orders",
        ):
            st.rerun()

    if chosen_filter == "All orders":
        filtered_orders = orders
    else:
        chosen_status = next(
            (
                status
                for status in statuses
                if _status_label(status) == chosen_filter
            ),
            None,
        )

        filtered_orders = [
            order for order in orders
            if str(order["status"]).lower() == chosen_status
        ]

    st.caption(f"{len(filtered_orders)} order(s)")

    order_options = {
        (
            f"{order['order_number']} · "
            f"{_status_label(order['status'])} · "
            f"{_money(order['total_cost'])}"
        ): order
        for order in filtered_orders
    }

    if not order_options:
        st.info("There are no orders matching this filter.")
        return

    selected_label = st.selectbox(
        "Select an order to view details",
        list(order_options.keys()),
        key="pp_selected_order",
    )

    order = order_options[selected_label]

    order_number = str(
        order["order_number"]
        or f"Order #{order['order_id']}"
    )

    status = str(order["status"] or "pending").lower()
    fulfillment = str(
        order["fulfillment_method"] or "pickup"
    ).lower()

    fulfillment_label = (
        "Campus Delivery"
        if fulfillment == "delivery"
        else "Campus Pickup"
    )

    created_at = _format_date(order["created_at"])

    _render_html(
        f"""
        <div class="pp-order-card">
            <div class="pp-order-top">
                <div>
                    <div class="pp-order-number">
                        {escape(order_number)}
                    </div>
                    <div class="pp-order-meta">
                        Submitted {escape(created_at)}
                    </div>
                </div>

                <span class="pp-status-pill">
                    {escape(_status_label(status))}
                </span>
            </div>

            <div style="
                display:grid;
                grid-template-columns:repeat(
                    auto-fit,minmax(135px,1fr)
                );
                gap:16px;
                margin-top:18px;
            ">
                <div>
                    <div class="pp-order-detail-label">
                        Estimated Total
                    </div>
                    <div class="pp-order-detail-value">
                        {_money(order['total_cost'])}
                    </div>
                </div>

                <div>
                    <div class="pp-order-detail-label">
                        Documents / Pages
                    </div>
                    <div class="pp-order-detail-value">
                        {order['total_pages']} page(s)
                    </div>
                </div>

                <div>
                    <div class="pp-order-detail-label">
                        Print Settings
                    </div>
                    <div class="pp-order-detail-value">
                        {escape(str(order['paper_size']))}
                        ·
                        {escape(str(order['color_mode']).replace('_', ' ').title())}
                    </div>
                </div>

                <div>
                    <div class="pp-order-detail-label">
                        Fulfillment
                    </div>
                    <div class="pp-order-detail-value">
                        {escape(fulfillment_label)}
                    </div>
                </div>
            </div>
        </div>
        """
    )

    _render_tracker(status, fulfillment)

    st.info(
        STATUS_HELP.get(
            status,
            "Check back for updates to your order.",
        )
    )

    if status == "rejected":
        reason = _get_rejection_reason(order)

        if reason:
            st.error(f"Reason: {reason}")

    if fulfillment == "pickup" and order["pickup_location"]:
        st.caption(f"Pickup location: {order['pickup_location']}")

    elif fulfillment == "delivery":
        destination = " · ".join(
            str(value).strip()
            for value in (
                order["building"],
                order["floor"],
                order["room"],
            )
            if value and str(value).strip()
        )

        if destination:
            st.caption(f"Delivery destination: {destination}")

        if order["delivery_notes"]:
            st.caption(
                f"Delivery instructions: {order['delivery_notes']}"
            )

    _render_order_files(order["order_id"])
    _render_status_history(order["order_id"])

    render_customer_order_communication(
        order_id=order["order_id"],
        user=user,
        status=status,
    )
    

    if st.button(
        "Create Another Order",
        type="primary",
        key="pp_create_another_order",
    ):
        st.session_state["customer_page"] = "new_order"
        st.rerun()


show_my_orders = render_my_orders_page
