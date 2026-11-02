
import streamlit as st
from database.connection import get_connection
from database.order_repository import OrderRepository
from notifications.notification_service import (
    create_notification,
    notify_other_order_party,
)


# ==================================================
# GENERAL HELPERS
# ==================================================

def _value(data, key, default=None):
    if data is None:
        return default

    try:
        value = data[key]
        return default if value is None else value
    except (KeyError, IndexError, TypeError):
        pass

    try:
        value = getattr(data, key)
        return default if value is None else value
    except (AttributeError, TypeError):
        return default


def _get_user_id(user=None):
    # First, check the user passed by the page.
    user_id = _value(user, "user_id")

    # Check the application session.
    if user_id is None:
        current_user = st.session_state.get("current_user")
        user_id = _value(current_user, "user_id")

    # Check the standalone session ID.
    if user_id is None:
        user_id = st.session_state.get("user_id")

    return user_id


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

def initialize_communication_tables():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS order_proof_reviews (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                decision TEXT NOT NULL
                    CHECK (
                        decision IN (
                            'approved',
                            'recheck_requested'
                        )
                    ),
                comment TEXT,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id)
                    REFERENCES orders(order_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (customer_id)
                    REFERENCES users(user_id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS order_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id)
                    REFERENCES orders(order_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (sender_id)
                    REFERENCES users(user_id)
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_order_messages_order
            ON order_messages(order_id, created_at)
        """)


# ==================================================
# ORDER ACCESS VALIDATION
# ==================================================

def _check_order_access(order_id, user, role):
    user_id = _get_user_id(user)

    if user_id is None:
        raise ValueError(
            "Your account could not be identified. "
            "Please log out and sign in again."
        )

    with get_connection() as connection:
        order = connection.execute(
            """
            SELECT
                order_id,
                customer_id,
                assigned_staff_id,
                status
            FROM orders
            WHERE order_id = ?
            """,
            (order_id,),
        ).fetchone()

    if order is None:
        raise ValueError("This order could not be found.")

    if role == "customer":
        if str(order["customer_id"]) != str(user_id):
            raise PermissionError(
                "You cannot access this order."
            )

    elif role == "staff":
        if str(order["assigned_staff_id"]) != str(user_id):
            raise PermissionError(
                "You can only access orders assigned to your account."
            )

    else:
        raise PermissionError("Invalid account role.")

    return order


# ==================================================
# PROOF FILES
# ==================================================

def _get_proof_files(order_id):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                file_id,
                original_filename,
                file_path,
                uploaded_at
            FROM order_files
            WHERE order_id = ?
            AND file_type = 'proof'
            ORDER BY uploaded_at ASC
            """,
            (order_id,),
        ).fetchall()


# ==================================================
# PROOF APPROVAL CHECK
# ==================================================

def customer_approved_proof(order_id):
    initialize_communication_tables()

    with get_connection() as connection:
        proof_count = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM order_files
            WHERE order_id = ?
            AND file_type = 'proof'
            """,
            (order_id,),
        ).fetchone()["total"]

        # If staff did not upload proof photos,
        # do not block the existing workflow.
        if proof_count == 0:
            return True

        review = connection.execute(
            """
            SELECT decision
            FROM order_proof_reviews
            WHERE order_id = ?
            """,
            (order_id,),
        ).fetchone()

    return bool(
        review
        and review["decision"] == "approved"
    )


# ==================================================
# SAVE MESSAGE
# ==================================================

def _save_message(order_id, user, role, message):
    message = str(message or "").strip()

    if not message:
        raise ValueError("Please enter a message first.")

    if len(message) > 3000:
        raise ValueError(
            "Messages must be 3,000 characters or fewer."
        )

    _check_order_access(order_id, user, role)

    sender_id = _get_user_id(user)

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO order_messages (
                order_id,
                sender_id,
                message
            )
            VALUES (?, ?, ?)
            """,
            (order_id, sender_id, message),
        )

    notify_other_order_party(
        order_id,
        role,
        "New Order Message",
        "You have a new message about this printing order.",
    )


# ==================================================
# ORDER CONVERSATION
# ==================================================

def _render_conversation(order_id, user, role):
    initialize_communication_tables()
    _check_order_access(order_id, user, role)

    st.markdown("### Order Conversation")

    st.caption(
        "Messages about this order are shared between "
        "the customer and assigned printing staff."
    )

    with get_connection() as connection:
        messages = connection.execute(
            """
            SELECT
                m.message_id,
                m.sender_id,
                m.message,
                m.created_at,
                u.username,
                u.role
            FROM order_messages AS m
            JOIN users AS u
                ON u.user_id = m.sender_id
            WHERE m.order_id = ?
            ORDER BY
                m.created_at ASC,
                m.message_id ASC
            """,
            (order_id,),
        ).fetchall()

    current_user_id = _get_user_id(user)

    if not messages:
        st.info(
            "No messages yet. Start the conversation below."
        )

    else:
        for item in messages:
            own_message = (
                str(item["sender_id"])
                == str(current_user_id)
            )

            if own_message:
                sender_label = "You"
            else:
                sender_label = (
                    f"{item['username']} "
                    f"· {item['role'].title()}"
                )

            with st.chat_message(
                "user" if own_message else "assistant"
            ):
                st.caption(
                    f"{sender_label} · {item['created_at']}"
                )
                st.write(item["message"])

    with st.form(
        key=f"order_message_form_{role}_{order_id}"
    ):
        message = st.text_area(
            "Write a message",
            placeholder=(
                "Ask a question or send an update "
                "about this order..."
            ),
            height=90,
            max_chars=3000,
            key=f"order_message_input_{role}_{order_id}",
        )

        submitted = st.form_submit_button(
            "Send Message",
            type="primary",
            width="stretch",
        )

    if submitted:
        try:
            _save_message(
                order_id,
                user,
                role,
                message,
            )

            st.success("Message sent!")
            st.rerun()

        except Exception as error:
            st.error(
                f"Unable to send message: {error}"
            )


# ==================================================
# CUSTOMER PROOF REVIEW
# ==================================================

def render_customer_proof_review(
    order_id,
    user,
    status,
):
    initialize_communication_tables()
    _check_order_access(order_id, user, "customer")

    if status != "awaiting_review":
        return

    proofs = _get_proof_files(order_id)

    if not proofs:
        return

    with get_connection() as connection:
        review = connection.execute(
            """
            SELECT
                decision,
                comment,
                updated_at
            FROM order_proof_reviews
            WHERE order_id = ?
            """,
            (order_id,),
        ).fetchone()

    st.markdown("### Review Your Printed Output")

    if review and review["decision"] == "approved":
        st.success(
            "You approved the print proof."
        )
        st.caption(
            f"Approved on {review['updated_at']}"
        )

        if review["comment"]:
            st.write(
                f"Your note: {review['comment']}"
            )

        return

    if review and review["decision"] == "recheck_requested":
        st.warning(
            "You requested a recheck. "
            "Staff needs to review your concern."
        )

        if review["comment"]:
            st.write(
                f"Your note: {review['comment']}"
            )

        return

    st.info(
        "Please check the proof photos uploaded by staff. "
        "You can approve the output or request a recheck."
    )

    comment = st.text_area(
        "Comment",
        placeholder=(
            "Example: The text on page 2 looks faded..."
        ),
        key=f"customer_proof_comment_{order_id}",
        max_chars=1000,
    )

    approve_col, recheck_col = st.columns(2)

    # APPROVE PROOF

    with approve_col:
        if st.button(
            "Approve Print",
            type="primary",
            width="stretch",
            key=f"customer_approve_proof_{order_id}",
        ):
            try:
                user_id = _get_user_id(user)

                with get_connection() as connection:
                    connection.execute(
                        """
                        INSERT INTO order_proof_reviews (
                            order_id,
                            customer_id,
                            decision,
                            comment,
                            updated_at
                        )
                        VALUES (
                            ?, ?, 'approved', ?,
                            CURRENT_TIMESTAMP
                        )
                        ON CONFLICT(order_id)
                        DO UPDATE SET
                            customer_id = excluded.customer_id,
                            decision = 'approved',
                            comment = excluded.comment,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (
                            order_id,
                            user_id,
                            comment.strip() or None,
                        ),
                    )

                notify_other_order_party(
                    order_id,
                    "customer",
                    "Customer Approved Print Proof",
                    "The customer approved the print proof. You can continue with fulfillment.",
                )
                st.success(
                    "Thank you! Your approval has been recorded."
                )
                st.rerun()

            except Exception as error:
                st.error(
                    f"Unable to save your approval: {error}"
                )

    # REQUEST RECHECK

    with recheck_col:
        if st.button(
            "Request Recheck",
            width="stretch",
            key=f"customer_request_recheck_{order_id}",
        ):
            try:
                if not comment.strip():
                    st.warning(
                        "Please explain what needs to be "
                        "checked again."
                    )

                else:
                    user_id = _get_user_id(user)

                    # Validate that this is the customer's order.
                    _check_order_access(
                        order_id,
                        user,
                        "customer",
                    )

                    # Save the review decision.
                    with get_connection() as connection:
                        connection.execute(
                            """
                            INSERT INTO order_proof_reviews (
                                order_id,
                                customer_id,
                                decision,
                                comment,
                                updated_at
                            )
                            VALUES (
                                ?, ?, 'recheck_requested', ?,
                                CURRENT_TIMESTAMP
                            )
                            ON CONFLICT(order_id)
                            DO UPDATE SET
                                customer_id = excluded.customer_id,
                                decision = 'recheck_requested',
                                comment = excluded.comment,
                                updated_at = CURRENT_TIMESTAMP
                            """,
                            (
                                order_id,
                                user_id,
                                comment.strip(),
                            ),
                        )

                    # Update the order status.
                    repository = OrderRepository()

                    repository.update_order_status(
                        order_id=order_id,
                        new_status="correction_requested",
                        changed_by=user_id,
                        notes=(
                            "Customer requested a recheck: "
                            f"{comment.strip()}"
                        ),
                    )

                    notify_other_order_party(
                        order_id,
                        "customer",
                        "Customer Requested a Recheck",
                        "The customer requested a recheck. Please review the customer's note.",
                    )
                    st.success(
                        "Your recheck request has been sent to staff."
                    )
                    st.rerun()

            except Exception as error:
                st.error(
                    f"Unable to request a recheck: {error}"
                )


# ==================================================
# CUSTOMER COMMUNICATION SECTION
# ==================================================

def render_customer_order_communication(
    order_id,
    user,
    status,
):
    initialize_communication_tables()

    with st.container(border=True):
        render_customer_proof_review(
            order_id,
            user,
            status,
        )

    with st.container(border=True):
        _render_conversation(
            order_id,
            user,
            "customer",
        )


# ==================================================
# STAFF COMMUNICATION SECTION
# ==================================================

def render_staff_order_communication(
    order_id,
    user,
):
    initialize_communication_tables()

    # Validate the assigned staff account.
    _check_order_access(
        order_id,
        user,
        "staff",
    )

    with get_connection() as connection:
        review = connection.execute(
            """
            SELECT
                decision,
                comment,
                updated_at
            FROM order_proof_reviews
            WHERE order_id = ?
            """,
            (order_id,),
        ).fetchone()

    with st.container(border=True):
        st.markdown("### Customer Proof Review")

        if review is None:
            st.info(
                "The customer has not submitted "
                "a proof decision yet."
            )

        elif review["decision"] == "approved":
            st.success(
                "The customer approved the print proof."
            )

            st.caption(
                f"Updated: {review['updated_at']}"
            )

            if review["comment"]:
                st.write(
                    f"Customer note: {review['comment']}"
                )

        else:
            st.warning(
                "The customer requested a recheck."
            )

            st.write(
                review["comment"] or "No additional comment."
            )

    with st.container(border=True):
        _render_conversation(
            order_id,
            user,
            "staff",
        )
