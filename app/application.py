import streamlit as st

from app.session import get_current_user, logout
from database.staff_access_repository import StaffAccessRepository
from notifications.email_service import send_staff_authorization_email

from ui.auth_pages import show_auth_page
from ui.styles import load_styles, load_dashboard_styles
from ui.header import render_header
from ui.transitions import load_transition_styles
from ui.loader import show_loader

from customer.sidebar import render_customer_sidebar
from customer.customer_dashboard import render_customer_dashboard
from customer.new_order import render_new_order_page
from customer.my_orders import render_my_orders_page
from customer.saved_files import render_saved_files_page
from customer.help_support import render_help_support_page

from staff.sidebar import render_staff_sidebar
from staff.order_queue import render_order_queue_page
from staff.assigned_orders import render_assigned_orders_page
from staff.completed_orders import render_completed_orders_page
from staff.assigned_orders import render_assigned_orders_page


class Application:

    def run(self):

        st.set_page_config(
            page_title="PasaPrint",
            page_icon="🖨️",
            layout="wide",
            initial_sidebar_state="collapsed",
        )

        approval_token = st.query_params.get("staff_approval")
        if approval_token:
            st.title("PasaPrint Staff Access Approval")
            st.write("A staff registration request is awaiting your approval.")
            st.warning("Applicant approval link: confirm only if you recognize and approve this request.")
            if st.button("Approve Staff Access", type="primary", use_container_width=True):
                try:
                    result = StaffAccessRepository().approve(approval_token)
                    if result is None:
                        st.error("This approval link is invalid, expired, or already used.")
                    else:
                        send_staff_authorization_email(result["email"], result["code"])
                        st.success(f"Approved! An authorization code has been emailed to {result['email']}.")
                    st.query_params.clear()
                except Exception:
                    st.error("Approval was recorded or attempted, but the invitation email could not be sent. Please contact the PasaPrint administrator before retrying.")
            st.stop()

        user = get_current_user()

        # Authentication
        if user is None:
            load_styles()
            show_auth_page()
            return

        # Load dashboard styling
        load_dashboard_styles()
        load_transition_styles()

        # Staff navigation
        if user.get("role") == "staff":

            selected_page = render_staff_sidebar()
            render_header(user)

            # Leave space for the fixed header
            st.markdown(
                "<div style='height: 84px;'></div>",
                unsafe_allow_html=True,
            )

            staff_page_messages = {
                "order_queue": (
                    "Loading Order Queue...",
                    "Fetching incoming printing orders",
                ),
                "assigned_orders": (
                    "Loading Assigned Orders...",
                    "Fetching your assigned printing orders",
                ),
                "completed_orders": (
                    "Loading Completed Orders...",
                    "Fetching your completed printing orders",
                ),
            }

            previous_page = st.session_state.get(
                "pp_last_rendered_page"
            )

            page_changed = previous_page != selected_page

            def render_selected_staff_page():

                with st.container(key=f"pp-page-{selected_page}"):

                    if selected_page == "order_queue":
                        render_order_queue_page(user)

                    elif selected_page == "assigned_orders":
                        render_assigned_orders_page(st.user)

                    elif selected_page == "completed_orders":
                        render_completed_orders_page(user)

            if page_changed:

                message, subtitle = staff_page_messages.get(
                    selected_page,
                    ("Loading page...", "Please wait"),
                )

                with show_loader(message, subtitle):
                    render_selected_staff_page()

                st.session_state["pp_last_rendered_page"] = selected_page

            else:
                render_selected_staff_page()

            return

        # Manager placeholder
        if user.get("role") == "manager":

            # This marker enables Streamlit's native toolbar for managers only.
            st.markdown(
                '<div class="pp-manager-toolbar"></div>',
                unsafe_allow_html=True,
            )

            # Managers use a clean page without the shared customer/staff header.
            st.title(f"Welcome, {user.get('username', 'Manager')}!")

            st.info(
                "The manager dashboard will be added later."
            )

            return

        # Customer navigation
        selected_page = render_customer_sidebar()
        render_header(user)

        # Leave space for the fixed header
        st.markdown(
            "<div style='height: 84px;'></div>",
            unsafe_allow_html=True,
        )

        page_messages = {
            "home": (
                "Loading your dashboard...",
                "Preparing your PasaPrint overview",
            ),
            "new_order": (
                "Preparing New Order...",
                "Getting your printing form ready",
            ),
            "my_orders": (
                "Loading your orders...",
                "Fetching your printing requests",
            ),
            "saved_files": (
                "Loading your documents...",
                "Preparing your saved files",
            ),
            "help_support": (
                "Loading Help & Support...",
                "Preparing assistance and information",
            ),
        }

        previous_page = st.session_state.get(
            "pp_last_rendered_page"
        )

        page_changed = previous_page != selected_page

        def render_selected_customer_page():

            with st.container(key=f"pp-page-{selected_page}"):

                if selected_page == "home":
                    render_customer_dashboard(user)

                elif selected_page == "new_order":
                    render_new_order_page(user)

                elif selected_page == "my_orders":
                    render_my_orders_page(user)

                elif selected_page == "saved_files":
                    render_saved_files_page(user)

                elif selected_page == "help_support":
                    render_help_support_page(user)

        if page_changed:

            message, subtitle = page_messages.get(
                selected_page,
                ("Loading page...", "Please wait"),
            )

            with show_loader(message, subtitle):
                render_selected_customer_page()

            st.session_state["pp_last_rendered_page"] = selected_page

        else:
            render_selected_customer_page()
