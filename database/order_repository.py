
from database.connection import get_connection
from notifications.notification_service import (
    create_notification,
    notify_order_status_change,
)


class OrderRepository:
    def create_order(self, order_data):
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO orders (
                    order_number, customer_id, status,
                    fulfillment_method, campus, pickup_location,
                    building, floor, room, delivery_notes,
                    color_mode, paper_size, print_sides, copies,
                    total_pages, price_per_page, printing_cost,
                    delivery_fee, total_cost, customer_notes
                )
                VALUES (
                    :order_number, :customer_id, 'pending',
                    :fulfillment_method, :campus, :pickup_location,
                    :building, :floor, :room, :delivery_notes,
                    :color_mode, :paper_size, :print_sides, :copies,
                    :total_pages, :price_per_page, :printing_cost,
                    :delivery_fee, :total_cost, :customer_notes
                )
                """,
                order_data,
            )
            order_id = cursor.lastrowid
            connection.execute(
                """
                INSERT INTO order_status_history (
                    order_id, changed_by, old_status, new_status, notes
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    order_data["customer_id"],
                    None,
                    "pending",
                    "Order submitted.",
                ),
            )
            customer = connection.execute(
                "SELECT email FROM users WHERE user_id = ?",
                (order_data["customer_id"],),
            ).fetchone()

        if customer:
            create_notification(
                user_id=order_data["customer_id"],
                order_id=order_id,
                title="Order Submitted",
                message="Your printing order has been received and is waiting for staff confirmation.",
                notification_type="order_status",
                recipient_email=customer["email"],
                order_number=order_data["order_number"],
            )
        return order_id

    def get_order_by_id(self, order_id):
        with get_connection() as connection:
            return connection.execute(
                "SELECT * FROM orders WHERE order_id = ?",
                (order_id,),
            ).fetchone()

    def get_order_by_number(self, order_number):
        with get_connection() as connection:
            return connection.execute(
                "SELECT * FROM orders WHERE order_number = ?",
                (order_number,),
            ).fetchone()

    def get_customer_orders(self, customer_id):
        with get_connection() as connection:
            return connection.execute(
                """
                SELECT * FROM orders
                WHERE customer_id = ?
                ORDER BY created_at DESC
                """,
                (customer_id,),
            ).fetchall()

    def get_all_orders(self):
        with get_connection() as connection:
            return connection.execute(
                """
                SELECT orders.*, users.username, users.email
                FROM orders
                JOIN users ON orders.customer_id = users.user_id
                ORDER BY orders.created_at DESC
                """
            ).fetchall()

    def get_orders_by_status(self, status):
        with get_connection() as connection:
            return connection.execute(
                """
                SELECT orders.*, users.username, users.email
                FROM orders
                JOIN users ON orders.customer_id = users.user_id
                WHERE orders.status = ?
                ORDER BY orders.created_at ASC
                """,
                (status,),
            ).fetchall()

    def get_status_history(self, order_id):
        with get_connection() as connection:
            return connection.execute(
                """
                SELECT order_status_history.*, users.username
                FROM order_status_history
                LEFT JOIN users
                    ON order_status_history.changed_by = users.user_id
                WHERE order_status_history.order_id = ?
                ORDER BY order_status_history.history_id ASC
                """,
                (order_id,),
            ).fetchall()

    def confirm_order(self, order_id, staff_id):
        with get_connection() as connection:
            order = connection.execute(
                """
                SELECT status
                FROM orders
                WHERE order_id = ?
                """,
                (order_id,),
            ).fetchone()

            if order is None:
                raise ValueError("Order not found.")

            if order["status"] != "pending":
                raise ValueError("This order is no longer awaiting confirmation.")

            connection.execute(
                """
                UPDATE orders
                SET status = 'confirmed',
                    assigned_staff_id = ?,
                    confirmed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
                """,
                (staff_id, order_id),
            )

            connection.execute(
                """
                INSERT INTO order_status_history (
                    order_id, changed_by, old_status, new_status, notes
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    staff_id,
                    "pending",
                    "confirmed",
                    "Order confirmed and assigned to staff.",
                ),
            )

        notify_order_status_change(order_id, "confirmed")
        return True
    
    def update_order_status(
        self,
        order_id,
        new_status,
        changed_by,
        notes=None,
    ):
        allowed_transitions = {
            "pending": {"confirmed", "rejected", "cancelled"},
            "confirmed": {"printing"},
            "printing": {"awaiting_review"},
            "awaiting_review": {
                "correction_requested",
                "ready_for_pickup",
                "out_for_delivery",
            },
            "correction_requested": {"printing"},
            "ready_for_pickup": {"completed"},
            "out_for_delivery": {"completed"},
            "completed": set(),
            "rejected": set(),
            "cancelled": set(),
        }

        valid_statuses = set(allowed_transitions)

        if new_status not in valid_statuses:
            raise ValueError("Invalid order status.")

        with get_connection() as connection:
            order = connection.execute(
                """
                SELECT status
                FROM orders
                WHERE order_id = ?
                """,
                (order_id,),
            ).fetchone()

            if order is None:
                raise ValueError("Order not found.")

            old_status = order["status"]

            if new_status not in allowed_transitions[old_status]:
                raise ValueError(
                    f"Cannot change status from {old_status} "
                    f"to {new_status}."
                )

            if new_status in ("rejected", "cancelled"):
                if not notes or not notes.strip():
                    raise ValueError(
                        "A reason is required for rejection or cancellation."
                    )

            connection.execute(
                """
                UPDATE orders
                SET status = ?,
                    updated_at = CURRENT_TIMESTAMP,
                    confirmed_at = CASE
                        WHEN ? = 'confirmed'
                        THEN CURRENT_TIMESTAMP
                        ELSE confirmed_at
                    END,
                    completed_at = CASE
                        WHEN ? = 'completed'
                        THEN CURRENT_TIMESTAMP
                        ELSE completed_at
                    END
                WHERE order_id = ?
                """,
                (new_status, new_status, new_status, order_id),
            )

            connection.execute(
                """
                INSERT INTO order_status_history (
                    order_id, changed_by, old_status,
                    new_status, notes
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    changed_by,
                    old_status,
                    new_status,
                    notes,
                ),
            )

        notify_order_status_change(order_id, new_status)
        return True
