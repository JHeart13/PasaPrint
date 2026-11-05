
from database.connection import get_connection


class UserRepository:
    def create_user(
        self,
        username,
        email,
        password_hash,
        role,
        student_number=None,
        account_status="active",
    ):
        if role not in ("customer", "staff", "manager"):
            raise ValueError("Invalid user role.")

        if account_status not in ("pending", "active", "inactive"):
            raise ValueError("Invalid account status.")

        if role == "customer" and not student_number:
            raise ValueError("Customers must provide a student number.")

        if role != "customer":
            student_number = None

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (
                    username, email, password_hash, role,
                    student_number, account_status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    username.strip(),
                    email.strip().lower(),
                    password_hash,
                    role,
                    student_number,
                    account_status,
                ),
            )

            return cursor.lastrowid

    def get_by_email(self, email):
        with get_connection() as connection:
            return connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email.strip().lower(),),
            ).fetchone()

    def get_by_id(self, user_id):
        with get_connection() as connection:
            return connection.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()

    def get_all_users(self):
        with get_connection() as connection:
            return connection.execute(
                """
                SELECT user_id, username, student_number, email,
                       role, account_status, created_at
                FROM users
                ORDER BY created_at DESC
                """
            ).fetchall()

    def update_account_status(self, user_id, account_status):
        if account_status not in ("pending", "active", "inactive"):
            raise ValueError("Invalid account status.")

        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE users
                SET account_status = ?
                WHERE user_id = ?
                """,
                (account_status, user_id),
            )

            return cursor.rowcount > 0


    def update_password_hash(self, email, password_hash):
        """Update a user's stored password hash by email."""

        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE users
                SET password_hash = ?
                WHERE email = ?
                  AND account_status = 'active'
                """,
                (password_hash, email.strip().lower()),
            )

            return cursor.rowcount > 0
