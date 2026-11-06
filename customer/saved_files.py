import base64
from pathlib import Path
from html import escape

import streamlit as st

from services.file_service import FileService


PROJECT_ROOT = Path(__file__).resolve().parent.parent

WELCOME_BACKGROUND = (
    PROJECT_ROOT / "assets" / "backgrounds" / "login_background.png"
)


def _format_date(value):
    """Format the uploaded date for display."""

    if not value:
        return "Date unavailable"

    return str(value)[:16].replace("T", " · ")


def _welcome_background_css():
    """Create a light version of the printing-pattern background."""

    if not WELCOME_BACKGROUND.is_file():
        return "background-color: #E3F1E7;"

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }

    mime_type = mime_types.get(WELCOME_BACKGROUND.suffix.lower())

    if not mime_type:
        return "background-color: #E3F1E7;"

    encoded = base64.b64encode(
        WELCOME_BACKGROUND.read_bytes()
    ).decode("ascii")

    return (
        "background-image: "
        "linear-gradient(rgba(227,241,231,0.88), "
        "rgba(227,241,231,0.88)), "
        f"url('data:{mime_type};base64,{encoded}');"
        "background-size: cover;"
        "background-position: center;"
    )


def _show_document_preview(file_record):
    """Display a PDF preview in a Streamlit dialog."""

    file_service = FileService()
    file_bytes = file_service.get_file_bytes(file_record)

    @st.dialog("Document Preview", width="large")
    def preview_dialog():
        filename = file_record["original_filename"] or "Untitled document"

        st.markdown(f"**{escape(str(filename))}**")

        if not file_bytes:
            st.error(
                "This document could not be found. "
                "It may have been moved or deleted."
            )
        else:
            st.pdf(
                file_bytes,
                height=650,
                key=f"pp-pdf-preview-{file_record['file_id']}",
            )

            st.download_button(
                label="Download Original PDF",
                data=file_bytes,
                file_name=filename,
                mime="application/pdf",
                key=f"pp-library-download-{file_record['file_id']}",
                width="stretch",
            )

        if st.button("Close Preview", width="stretch"):
            st.session_state["pp_preview_file_id"] = None
            st.rerun()

    preview_dialog()


def render_saved_files_page(user):
    """Render the customer's complete uploaded document library."""

    customer_id = user.get("user_id")

    if customer_id is None:
        st.error("Your account could not be identified. Please log in again.")
        return

    file_service = FileService()

    # Header background
    welcome_background = _welcome_background_css()

    st.markdown(
        f"""
    <div style="
        {welcome_background}
        background-repeat: no-repeat;
        border: 1px solid #D0E6D5;
        border-radius: 16px;
        padding: 25px 28px;
        margin-bottom: 20px;
        min-height: 130px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
    ">
    <h1 style="
        color: #064B36;
        font-size: 1.8rem;
        margin: 0 0 6px 0;
    ">Saved Files</h1>
    <div style="
        color: #426A53;
        margin: 0;
        font-size: 0.95rem;
    ">
    View and manage the documents you've uploaded through your printing orders.
    </div>
    </div>
        """,
        unsafe_allow_html=True,
    )

    # Back to Home
    if st.button("← Back to Home", key="pp-saved-files-home"):
        st.session_state["customer_page"] = "home"
        st.session_state["pp_preview_file_id"] = None
        st.rerun()

    st.divider()

    # Retrieve customer documents
    try:
        documents = list(
            file_service.get_customer_documents(customer_id)
        )

    except Exception as error:
        st.error("We couldn't load your saved documents.")
        print(
            f"Saved files error: {type(error).__name__}: {error}"
        )
        return

    if not documents:
        st.info(
            "You haven't uploaded any documents yet. "
            "Documents from your printing orders will appear here."
        )
        return

    st.markdown(f"### Your Documents ({len(documents)})")

    # Search and sorting controls
    search_col, sort_col = st.columns([2, 1])

    with search_col:
        search_term = st.text_input(
            "Search documents",
            placeholder="Search by filename or order number...",
            key="pp-saved-files-search",
        )

    with sort_col:
        sort_option = st.selectbox(
            "Sort by",
            ["Newest first", "Oldest first", "Filename A–Z"],
            key="pp-saved-files-sort",
        )

    # Filter documents
    filtered_documents = documents

    if search_term.strip():
        term = search_term.strip().lower()

        filtered_documents = [
            item for item in filtered_documents
            if term in str(item["original_filename"] or "").lower()
            or term in str(item["order_number"] or "").lower()
        ]

    # Sort documents
    if sort_option == "Oldest first":
        filtered_documents = sorted(
            filtered_documents,
            key=lambda item: str(item["uploaded_at"] or ""),
        )

    elif sort_option == "Filename A–Z":
        filtered_documents = sorted(
            filtered_documents,
            key=lambda item: str(
                item["original_filename"] or ""
            ).lower(),
        )

    else:
        filtered_documents = sorted(
            filtered_documents,
            key=lambda item: str(item["uploaded_at"] or ""),
            reverse=True,
        )

    st.caption(
        f"Showing {len(filtered_documents)} of "
        f"{len(documents)} document(s)"
    )

    if not filtered_documents:
        st.warning("No documents matched your search.")
        return

    # Document cards
    for item in filtered_documents:
        file_id = item["file_id"]
        filename = item["original_filename"] or "Untitled document"
        order_number = item["order_number"] or "—"
        uploaded_at = _format_date(item["uploaded_at"])
        page_count = item["page_count"]

        with st.container(border=True):
            info_col, action_col = st.columns([4, 1])

            with info_col:
                st.markdown(
                    f"📄 **{escape(str(filename))}**"
                )

                st.caption(
                    f"Order {escape(str(order_number))} · "
                    f"{escape(uploaded_at)}"
                )

                if page_count:
                    st.caption(f"{page_count} page(s)")

            with action_col:
                if st.button(
                    "Preview",
                    key=f"pp-preview-file-{file_id}",
                    width="stretch",
                ):
                    st.session_state["pp_preview_file_id"] = file_id
                    st.rerun()

                file_bytes = file_service.get_file_bytes(item)

                if file_bytes:
                    st.download_button(
                        "Download",
                        data=file_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key=f"pp-download-file-{file_id}",
                        width="stretch",
                    )
                else:
                    st.caption("File unavailable")

    # Open selected document preview
    selected_file_id = st.session_state.get("pp_preview_file_id")

    if selected_file_id is not None:
        selected_file = next(
            (
                item for item in documents
                if item["file_id"] == selected_file_id
            ),
            None,
        )

        if selected_file:
            _show_document_preview(selected_file)

        else:
            st.session_state["pp_preview_file_id"] = None
