from database.connection import get_connection


def initialize_notification_table():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_id INTEGER,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT NOT NULL DEFAULT 'order',
                is_read INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
            )
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user
            ON notifications(user_id, is_read, created_at)
        """)


def create_notification(user_id, title, message, order_id=None,
                        notification_type="order", send_email=True,
                        recipient_email=None, order_number=None):
    if user_id is None:
        return None

    initialize_notification_table()
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO notifications (
                user_id, order_id, title, message, notification_type
            )
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, order_id, title, message, notification_type))
        notification_id = cursor.lastrowid

    if send_email and recipient_email:
        try:
            from notifications.email_service import send_notification_email
            send_notification_email(
                recipient_email,
                f"PasaPrint: {title}",
                title,
                message,
                order_number,
            )
        except Exception as error:
            # Email failure must never undo an in-app notification or order update.
            print(f"PasaPrint email notification failed: {type(error).__name__}: {error}")

    return notification_id


def get_user_notifications(user_id, limit=20):
    initialize_notification_table()
    with get_connection() as connection:
        return connection.execute("""
            SELECT notification_id, order_id, title, message,
                   notification_type, is_read, created_at
            FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC, notification_id DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()


def get_unread_count(user_id):
    initialize_notification_table()
    with get_connection() as connection:
        row = connection.execute("""
            SELECT COUNT(*) AS total
            FROM notifications
            WHERE user_id = ? AND is_read = 0
        """, (user_id,)).fetchone()
    return int(row["total"] or 0)


def mark_notification_read(notification_id, user_id):
    initialize_notification_table()
    with get_connection() as connection:
        connection.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE notification_id = ? AND user_id = ?
        """, (notification_id, user_id))


def mark_all_notifications_read(user_id):
    initialize_notification_table()
    with get_connection() as connection:
        connection.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = ? AND is_read = 0
        """, (user_id,))


def notify_order_status_change(order_id, new_status):
    """Notify the customer when staff changes an order's production status."""
    status_messages = {
        "confirmed": ("Order Confirmed", "Your printing order has been confirmed by staff."),
        "printing": ("Printing Started", "Your documents are now being printed."),
        "awaiting_review": ("Print Proof Ready", "Your printed output is ready for quality review. Please check the proof in My Orders."),
        "correction_requested": ("Reprint Required", "A recheck was requested for your order. Staff will review and correct the print output."),
        "ready_for_pickup": ("Ready for Pickup", "Your order is ready for pickup."),
        "out_for_delivery": ("Out for Delivery", "Your order is now out for delivery."),
        "completed": ("Order Completed", "Your order has been marked as completed. Thank you for using PasaPrint!"),
        "rejected": ("Order Rejected", "Your order could not be accepted. Please check the reason in My Orders."),
        "cancelled": ("Order Cancelled", "Your order has been cancelled."),
    }
    if new_status not in status_messages:
        return

    initialize_notification_table()
    with get_connection() as connection:
        order = connection.execute("""
            SELECT o.order_id, o.order_number, o.customer_id,
                   u.email, u.username
            FROM orders o
            JOIN users u ON u.user_id = o.customer_id
            WHERE o.order_id = ?
        """, (order_id,)).fetchone()

    if not order:
        return

    title, message = status_messages[new_status]
    create_notification(
        user_id=order["customer_id"],
        order_id=order_id,
        title=title,
        message=message,
        notification_type="order_status",
        recipient_email=order["email"],
        order_number=order["order_number"],
    )


def notify_other_order_party(order_id, sender_role, title, message):
    """Notify the other participant when a customer or staff sends an update."""
    initialize_notification_table()
    with get_connection() as connection:
        order = connection.execute("""
            SELECT o.order_id, o.order_number, o.customer_id,
                   o.assigned_staff_id,
                   customer.email AS customer_email,
                   staff.email AS staff_email
            FROM orders o
            JOIN users customer ON customer.user_id = o.customer_id
            LEFT JOIN users staff ON staff.user_id = o.assigned_staff_id
            WHERE o.order_id = ?
        """, (order_id,)).fetchone()

    if not order:
        return

    if sender_role == "customer":
        recipient_id = order["assigned_staff_id"]
        recipient_email = order["staff_email"]
    else:
        recipient_id = order["customer_id"]
        recipient_email = order["customer_email"]

    if recipient_id is None:
        return

    create_notification(
        user_id=recipient_id,
        order_id=order_id,
        title=title,
        message=message,
        notification_type="order_message",
        recipient_email=recipient_email,
        order_number=order["order_number"],
    )
