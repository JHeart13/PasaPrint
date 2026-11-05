
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from database.connection import get_connection


class AuthorizationRepository:
    def _hash_code(self, code):
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    def create_code(self, intended_email, manager_id, minutes_valid=10):
        if minutes_valid <= 0:
            raise ValueError("Code duration must be positive.")

        code = f"{secrets.randbelow(100_000_000):08d}"
        code_hash = self._hash_code(code)

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=minutes_valid)
        ).isoformat(timespec="seconds")

        with get_connection() as connection:
            manager = connection.execute(
                """
                SELECT role, account_status
                FROM users
                WHERE user_id = ?
                """,
                (manager_id,),
            ).fetchone()

            if (
                manager is None
                or manager["role"] != "manager"
                or manager["account_status"] != "active"
            ):
                raise PermissionError(
                    "Only an active manager can issue authorization codes."
                )

            connection.execute(
                """
                INSERT INTO staff_authorization_codes (
                    code_hash, intended_email, created_by, expires_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    code_hash,
                    intended_email.strip().lower(),
                    manager_id,
                    expires_at,
                ),
            )

        # Show/send this code only through the authorized flow.
        return code

    def verify_and_consume(self, code, intended_email):
        code_hash = self._hash_code(code.strip())
        email = intended_email.strip().lower()
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        with get_connection() as connection:
            connection.execute("BEGIN IMMEDIATE")

            record = connection.execute(
                """
                SELECT code_id, expires_at, used_at
                FROM staff_authorization_codes
                WHERE code_hash = ? AND intended_email = ?
                """,
                (code_hash, email),
            ).fetchone()

            if record is None:
                return False

            if record["used_at"] is not None:
                return False

            if record["expires_at"] <= now:
                return False

            cursor = connection.execute(
                """
                UPDATE staff_authorization_codes
                SET used_at = ?
                WHERE code_id = ? AND used_at IS NULL
                """,
                (now, record["code_id"]),
            )

            return cursor.rowcount == 1
