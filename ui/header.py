from pathlib import Path

import streamlit as st

from notifications.notification_service import (
    get_user_notifications,
    get_unread_count,
    mark_notification_read,
    mark_all_notifications_read,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGO_DIR = PROJECT_ROOT / "assets" / "logo"


def render_header(user):
    """Render the fixed dashboard header and its dropdown panels."""
    username = user.get("username") or "Student"
    email = user.get("email") or username
    role = user.get("role", "customer")
    role_labels = {
        "customer": "Student",
        "staff": "Printing Staff",
        "manager": "Manager",
    }
    role_label = role_labels.get(role, str(role).title())
    user_id = user.get("user_id")
    collapsed = st.session_state.get("customer_sidebar_collapsed", False)
    unread_count = get_unread_count(user_id) if user_id is not None else 0
    bell_label = f"🔔 {unread_count}" if unread_count else "🔔"

    # The keyed container is essential: CSS positions this whole row as the header.
    with st.container(key="pp-header"):
        toggle_col, spacer, bell_col, avatar_col, account_col, menu_col = st.columns(
            [0.6, 5.5, 0.6, 0.6, 2.2, 0.5],
            vertical_alignment="center",
            gap="small",
        )

        with toggle_col:
            if st.button("☰", key="pp_toggle_sidebar", help="Expand or collapse sidebar"):
                st.session_state["customer_sidebar_collapsed"] = not collapsed
                st.rerun()

        with bell_col:
            if st.button(bell_label, key="pp_notifications", help="Notifications"):
                st.session_state["pp_show_notifications"] = not st.session_state.get(
                    "pp_show_notifications", False
                )
                st.session_state["pp_show_profile"] = False
                st.rerun()

        with avatar_col:
            st.markdown(
                '<div class="pp-header-avatar">♟</div>',
                unsafe_allow_html=True,
            )

        with account_col:
            st.markdown(
                f"""
                <div class="pp-header-account">
                    <div class="pp-header-email">{email}</div>
                    <div class="pp-header-role">{role_label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with menu_col:
            if st.button("⏷", key="pp_profile_menu", help="Account menu"):
                st.session_state["pp_show_profile"] = not st.session_state.get(
                    "pp_show_profile", False
                )
                st.session_state["pp_show_notifications"] = False
                st.rerun()

    if st.session_state.get("pp_show_notifications", False):
        with st.container(key="pp-notification-panel"):
            st.markdown("**Notifications**")
            if user_id is None:
                st.info("Sign in again to view notifications.")
            else:
                notifications = get_user_notifications(user_id)
                unread = [item for item in notifications if not item["is_read"]]
                if unread and st.button(
                    "Mark all as read",
                    key="pp_mark_all_notifications_read",
                    width="content",
                ):
                    mark_all_notifications_read(user_id)
                    st.rerun()

                if not notifications:
                    st.caption("You're all caught up! Order updates will appear here.")
                else:
                    for item in notifications:
                        with st.container(border=True):
                            heading = f"● {item['title']}" if not item["is_read"] else item["title"]
                            st.markdown(f"**{heading}**")
                            st.write(item["message"])
                            st.caption(item["created_at"])
                            if not item["is_read"] and st.button(
                                "Mark as read",
                                key=f"pp_notification_read_{item['notification_id']}",
                                width="content",
                            ):
                                mark_notification_read(item["notification_id"], user_id)
                                st.rerun()

    if st.session_state.get("pp_show_profile", False):
        with st.container(key="pp-profile-panel"):
            st.markdown(f"**{username}**")
            st.caption(email)
            st.caption(role_label)
            if st.button("Log Out", key="pp_header_logout"):
                for key in (
                    "current_user",
                    "customer_page",
                    "pp_show_notifications",
                    "pp_show_profile",
                    "customer_sidebar_collapsed",
                ):
                    st.session_state.pop(key, None)
                st.session_state["page"] = "login"
                st.session_state["auth_page"] = "login"
                st.rerun()
