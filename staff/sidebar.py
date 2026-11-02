from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGO_DIR = PROJECT_ROOT / "assets" / "logo"

NAV_ITEMS = [
    ("Order Queue", "order_queue", "▤"),
    ("Assigned Orders", "assigned_orders", "▣"),
    ("Completed Orders", "completed_orders", "✔"),
]


def render_staff_sidebar():
    """Render the printing staff sidebar and return the selected page."""

    st.session_state.setdefault("staff_page", "order_queue")
    # The shared header toggles this same state for both customer and staff layouts.
    st.session_state.setdefault("customer_sidebar_collapsed", False)

    collapsed = st.session_state["customer_sidebar_collapsed"]
    sidebar_key = "pp-sidebar-collapsed" if collapsed else "pp-sidebar"

    with st.container(key=sidebar_key):
        if collapsed:
            logo_path = LOGO_DIR / "sidebar_close.png"
            if logo_path.is_file():
                st.image(str(logo_path), width=42)
            else:
                st.markdown(
                    '<div class="pp-mini-logo">P</div>',
                    unsafe_allow_html=True,
                )
        else:
            logo_path = LOGO_DIR / "sidebar_open.png"
            if logo_path.is_file():
                st.image(str(logo_path), width="stretch")
            else:
                st.markdown(
                    '<div class="pp-brand">PasaPrint</div>'
                    '<div class="pp-tagline">'
                    'Online Campus Printing Service</div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<div class="pp-nav-gap"></div>',
            unsafe_allow_html=True,
        )

        for label, page_key, symbol in NAV_ITEMS:
            selected = st.session_state["staff_page"] == page_key

            with st.container(key=f"pp-nav-staff-{page_key}"):
                button_label = symbol if collapsed else f"{symbol}  {label}"

                if st.button(
                    button_label,
                    key=f"staff_nav_{page_key}",
                    type="primary" if selected else "secondary",
                    width="stretch",
                    help=label if collapsed else None,
                ):
                    st.session_state["staff_page"] = page_key
                    st.rerun()

    return st.session_state["staff_page"]
