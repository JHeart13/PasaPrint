from pathlib import Path

import streamlit as st

from app.session import set_user

from auth.auth_service import AuthService

from ui.styles import load_styles

from ui.loader import show_loader

from notifications.email_service import (

    send_welcome_email,

    send_staff_access_request_email,

)

BASE_DIR = Path(__file__).resolve().parent.parent

ILLUSTRATION_PATH = BASE_DIR / "assets" / "backgrounds" / "printing_illustration.png"

WORDMARK_PATH = BASE_DIR / "assets" / "logo" / "typography.png"

COMPLETE_LOGO_PATH = BASE_DIR / "assets" / "logo" / "complete.png"

ICON_DIR = BASE_DIR / "assets" / "icons"

def show_logo(width=160, complete=True):

    """Display the appropriate PasaPrint logo, with a text fallback."""

    logo_path = COMPLETE_LOGO_PATH if complete else WORDMARK_PATH

    if not logo_path.is_file():

        logo_path = WORDMARK_PATH if WORDMARK_PATH.is_file() else COMPLETE_LOGO_PATH

    if logo_path.is_file():

        st.image(str(logo_path), width=width)

    else:

        st.markdown(

            '<div style="text-align:center;color:#173D2B;font-size:1.8rem;'

            'font-weight:800;margin:.25rem 0">PasaPrint</div>',

            unsafe_allow_html=True,

        )

def show_login():

    """Render the sign-in screen."""

    notice = st.session_state.pop("auth_notice", None)

    notice_type = st.session_state.pop("auth_notice_type", "success")

    if notice:

        if notice_type == "warning":

            st.warning(notice)

        else:

            st.success(notice)

    _, center, _ = st.columns([1, 4, 1], gap="small")

    with center:

        with st.container(key="login-card"):

            _, logo_col, _ = st.columns([1, 2, 1])

            with logo_col:

                show_logo(width=180, complete=True)

            st.markdown(

                '<div class="login-heading">Get Started</div>',

                unsafe_allow_html=True,

            )

            st.markdown(

                '<div class="login-subheading">'

                'Sign in to your account and start printing</div>',

                unsafe_allow_html=True,

            )

            with st.form("login_form"):

                email = st.text_input(

                    "Email Address",

                    placeholder="Enter your email address",

                )

                password = st.text_input(

                    "Password",

                    placeholder="Enter your password",

                    type="password",

                )

                submitted = st.form_submit_button(

                    "Sign In",

                    type="primary",

                    use_container_width=True,

                )

            if submitted:

                if not email.strip() or not password:

                    st.error("Please enter your email and password.")

                else:

                    try:

                        with show_loader(

                            "Signing in...",

                            "Verifying your account",

                        ):

                            user = AuthService().login(

                                email.strip(),

                                password,

                            )

                        set_user(user)

                        st.session_state["page"] = "dashboard"

                        st.rerun()

                    except (ValueError, PermissionError) as error:

                        st.error(str(error))

                    except Exception:

                        st.error(

                            "We couldn't sign you in. "

                            "Please check your details or try again."

                        )

            if st.button(

                "Forgot password?",

                key="forgot_password",

                use_container_width=True,

            ):

                st.session_state["auth_page"] = "forgot_password"

                st.session_state["password_reset_stage"] = "request"

                st.rerun()

            st.markdown(

                '<div class="login-footer">'

                'New to PasaPrint? Create an account</div>',

                unsafe_allow_html=True,

            )

            if st.button(

                "Create an account",

                key="open_registration",

                use_container_width=True,

            ):

                st.session_state["auth_page"] = "register"

                st.rerun()

def show_forgot_password():
    """Render the password recovery and reset screens."""

    st.markdown(
        """
        <style>
        .st-key-forgot-password-card {
            background-color: #FFFFFF;
            padding: 2rem 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.10);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="forgot-password-card"):

        """Render the password recovery and reset screens."""

        st.markdown(

            '<div class="login-heading">Reset Your Password</div>',

            unsafe_allow_html=True,

        )

        st.markdown(

            '<div class="login-subheading">'

            'Recover access to your PasaPrint account</div>',

            unsafe_allow_html=True,

        )

        stage = st.session_state.setdefault("password_reset_stage", "request")

        if stage == "request":

            st.write("Enter the email address associated with your account.")

            with st.form("password_reset_request_form"):

                email = st.text_input(

                    "Email Address",

                    placeholder="Enter your registered email address",

                )

                request_submitted = st.form_submit_button(

                    "Send Reset Code",

                    type="primary",

                    use_container_width=True,

                )

            if request_submitted:

                if not email.strip():

                    st.error("Please enter your email address.")

                else:

                    try:

                        with show_loader(

                            "Sending reset code...",

                            "Checking your account and preparing your email",

                        ):

                            AuthService().request_password_reset(email.strip())

                        # This message is intentionally the same whether the

                        # account exists or not, to avoid exposing registered emails.

                        st.session_state["password_reset_email"] = (

                            AuthService()._validate_email(email)

                        )

                        st.session_state["password_reset_stage"] = "verify"

                        st.rerun()

                    except ValueError as error:

                        st.error(str(error))

                    except Exception:

                        st.error(

                            "We couldn't process your request right now. "

                            "Please check your email configuration and try again."

                        )

            st.info(

                "If an active PasaPrint account uses that email address, "

                "a 6-digit reset code will be sent. The code expires in 10 minutes."

            )

        else:

            reset_email = st.session_state.get("password_reset_email", "")

            st.write(f"Enter the reset code sent to **{reset_email}**.")

            with st.form("password_reset_complete_form"):

                reset_code = st.text_input(

                    "6-Digit Reset Code",

                    placeholder="Enter the code from your email",

                    max_chars=6,

                )

                new_password = st.text_input(

                    "New Password",

                    placeholder="Enter your new password",

                    type="password",

                )

                confirm_password = st.text_input(

                    "Confirm New Password",

                    placeholder="Re-enter your new password",

                    type="password",

                )

                reset_submitted = st.form_submit_button(

                    "Reset Password",

                    type="primary",

                    use_container_width=True,

                )

            if reset_submitted:

                try:

                    with show_loader(

                        "Updating password...",

                        "Verifying your reset code",

                    ):

                        AuthService().reset_password(

                            email=reset_email,

                            reset_code=reset_code.strip(),

                            new_password=new_password,

                            confirm_password=confirm_password,

                        )

                    st.session_state["auth_page"] = "login"

                    st.session_state["password_reset_stage"] = "request"

                    st.session_state.pop("password_reset_email", None)

                    st.session_state["auth_notice"] = (

                        "Your password has been reset successfully. "

                        "You can now sign in using your new password."

                    )

                    st.session_state["auth_notice_type"] = "success"

                    st.rerun()

                except ValueError as error:

                    st.error(str(error))

                except Exception:

                    st.error(

                        "We couldn't reset your password. "

                        "Please try again or request a new reset code."

                    )

            if st.button(

                "Send a new reset code",

                key="request_another_password_code",

                use_container_width=True,

            ):

                st.session_state["password_reset_stage"] = "request"

                st.session_state.pop("password_reset_email", None)

                st.rerun()

        if st.button(

            "Back to Sign In",

            key="back_to_login_from_reset",

            use_container_width=True,

        ):

            st.session_state["auth_page"] = "login"

            st.session_state["password_reset_stage"] = "request"

            st.session_state.pop("password_reset_email", None)

            st.rerun()

def show_registration():

    """Render the account registration screen."""

    left, right = st.columns([0.95, 1.75], gap="small")

    with left:

        with st.container(key="register-left-panel"):

            # Centered, smaller PasaPrint logo

            with st.container(key="register-logo"):

                show_logo(width=175, complete=False)

            # Printer illustration below the logo

            with st.container(key="register-illustration"):

                if ILLUSTRATION_PATH.is_file():

                    st.image(str(ILLUSTRATION_PATH), width=280)

            # Benefits below the illustration

            features = [

                (

                    "uploadyourfiles.png",

                    "Upload your files",

                    "Quick and easy file submission",

                ),

                (

                    "trackyourorders.png",

                    "Track your orders",

                    "Follow your printing order status",

                ),

                (

                    "getyourprints.png",

                    "Get your prints",

                    "Convenient campus pickup or delivery",

                ),

            ]

            for index, (icon_name, title, description) in enumerate(features):

                with st.container(key=f"register-benefit-{index}"):

                    icon_col, text_col = st.columns(

                        [0.14, 0.86],

                        gap="small",

                    )

                    with icon_col:

                        icon_path = ICON_DIR / icon_name

                        if icon_path.is_file():

                            st.image(str(icon_path), width=48)

                        else:

                            st.markdown("📄")

                    with text_col:

                        st.markdown(

                            f'<div class="benefit-title">{title}</div>'

                            f'<div class="benefit-description">'

                            f'{description}</div>',

                            unsafe_allow_html=True,

                        )

    with right:

        with st.container(key="register-right-panel"):

            st.markdown(

                '<div class="register-heading">'

                'Create Your Account</div>',

                unsafe_allow_html=True,

            )

            st.markdown(

                '<div class="register-subheading">'

                'Choose the type of account you need</div>',

                unsafe_allow_html=True,

            )

            account_type = st.radio(

                "Account Type",

                ["Customer", "Printing Staff"],

                horizontal=True,

                key="registration_account_type",

            )

            with st.form("registration_form"):

                username = st.text_input(

                    "Username",

                    placeholder="Choose a username",

                )

                email_col, student_col = st.columns(2, gap="medium")

                with email_col:

                    email = st.text_input(

                        "Email Address",

                        placeholder="Enter your email address",

                    )

                with student_col:

                    student_number = ""

                    if account_type == "Customer":

                        student_number = st.text_input(

                            "Student Number",

                            placeholder="Enter your student number",

                        )

                    else:

                        st.caption(

                            "Student number is only required for customers."

                        )

                password_col, confirm_col = st.columns(2, gap="medium")

                with password_col:

                    password = st.text_input(

                        "Password",

                        placeholder="Create a password",

                        type="password",

                    )

                with confirm_col:

                    confirm_password = st.text_input(

                        "Confirm Password",

                        placeholder="Re-enter your password",

                        type="password",

                    )

                authorization_code = ""

                if account_type == "Printing Staff":

                    st.info(

                        "Printing staff need a valid manager-issued "

                        "authorization code to register."

                    )

                    authorization_code = st.text_input(

                        "Staff Authorization Code",

                        placeholder="Enter your authorization code",

                        type="password",

                    )

                agree = st.checkbox(

                    "I agree to the Terms of Service and Privacy Policy",

                    key="agree_to_terms",

                )

                request_access = False

                if account_type == "Printing Staff":

                    request_access = st.form_submit_button(

                        "Request Staff Access",

                        use_container_width=True,

                    )

                submitted = st.form_submit_button(

                    "Create Account",

                    type="primary",

                    use_container_width=True,

                )

            if request_access:

                if not email.strip():

                    st.error("Please enter your email address first.")

                else:

                    try:

                        auth = AuthService()

                        normalized_email = auth._validate_email(email)

                        if auth.users.get_by_email(normalized_email):

                            st.error(

                                "This email is already registered. "

                                "Please sign in instead."

                            )

                        else:

                            with show_loader(

                                "Sending request...",

                                "Notifying the PasaPrint manager",

                            ):

                                send_staff_access_request_email(

                                    applicant_email=normalized_email,

                                )

                            st.success(

                                "Your staff access request has been sent! "

                                "Please wait for the manager to review it. "

                                "If approved, you will receive an authorization "

                                "code by email."

                            )

                    except ValueError as error:

                        st.error(str(error))

                    except Exception:

                        st.error(

                            "We couldn't send your request. "

                            "Please try again later or contact the PasaPrint "

                            "administrator."

                        )

            if submitted:

                # Validate registration details first

                if not agree:

                    st.error(

                        "Please agree to the Terms of Service and "

                        "Privacy Policy before registering."

                    )

                elif not all(

                    (username.strip(), email.strip(), password, confirm_password)

                ):

                    st.error("Please complete all required fields.")

                elif account_type == "Customer" and not student_number.strip():

                    st.error("Please enter your student number.")

                elif password != confirm_password:

                    st.error("Your passwords do not match.")

                elif (

                    account_type == "Printing Staff"

                    and not authorization_code.strip()

                ):

                    st.error("Please enter the staff authorization code.")

                else:

                    try:

                        auth = AuthService()

                        # Display the shared loader during registration

                        with show_loader(

                            "Creating your account...",

                            "Setting up your PasaPrint account",

                        ):

                            if account_type == "Customer":

                                auth.register_customer(

                                    username=username.strip(),

                                    student_number=student_number.strip(),

                                    email=email.strip(),

                                    password=password,

                                    confirm_password=confirm_password,

                                )

                            else:

                                auth.register_staff(

                                    username=username.strip(),

                                    email=email.strip(),

                                    password=password,

                                    confirm_password=confirm_password,

                                    authorization_code=authorization_code.strip(),

                                )

                            # Send the welcome email

                            try:

                                send_welcome_email(

                                    to_email=email.strip(),

                                    username=username.strip(),

                                    role=account_type.lower(),

                                )

                                st.session_state["auth_notice"] = (

                                    "Account created successfully! "

                                    "Your welcome email has been sent."

                                )

                                st.session_state["auth_notice_type"] = "success"

                            except Exception:

                                st.session_state["auth_notice"] = (

                                    "Account created successfully, but the "

                                    "welcome email could not be sent. "

                                    "Please check the email configuration."

                                )

                                st.session_state["auth_notice_type"] = "warning"

                        # Return to login after registration

                        st.session_state["auth_page"] = "login"

                        st.rerun()

                    except (ValueError, PermissionError) as error:

                        st.error(str(error))

                    except Exception:

                        st.error(

                            "We couldn't create your account. "

                            "Please check your details and try again."

                        )

            if st.button(

                "Already have an account? Sign in",

                key="back_to_login",

                use_container_width=True,

            ):

                st.session_state["auth_page"] = "login"

                st.rerun()

def show_auth_page():

    """Load styles and display the selected authentication screen."""

    load_styles()

    st.session_state.setdefault("auth_page", "login")

    if st.session_state["auth_page"] == "register":

        show_registration()

    elif st.session_state["auth_page"] == "forgot_password":

        show_forgot_password()

    else:

        show_login()
