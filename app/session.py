
import streamlit as st


def set_user(user):
    st.session_state["current_user"] = user


def get_current_user():
    return st.session_state.get("current_user")


def is_logged_in():
    return get_current_user() is not None


def logout():
    st.session_state.pop("current_user", None)
    st.session_state["page"] = "login"


def require_login():
    user = get_current_user()

    if user is None:
        st.warning("Please log in to continue.")
        st.stop()

    return user


def require_role(allowed_roles):
    user = require_login()

    if user["role"] not in allowed_roles:
        st.error("You do not have permission to access this page.")
        st.stop()

    return user
