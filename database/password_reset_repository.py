import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from database.connection import get_connection


class PasswordResetRepository:
    """Create and consume short-lived, one-time password reset codes."""

    def __init__(self):
        # Ensure older local databases receive the new table automatically.
        with get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS password_reset_codes (
                    reset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    code_hash TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0
                        CHECK (attempts >= 0),
                    used_at TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_password_reset_email
                ON password_reset_codes(email)
                """
            )

    def _hash_code(self, code):
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    def create_code(self, email, minutes_valid=10):
        if minutes_valid <= 0:
            raise ValueError("Reset-code duration must be positive.")

        normalized_email = email.strip().lower()
        code = f"{secrets.randbelow(1_000_000):06d}"
        code_hash = self._hash_code(code)
        now = datetime.now(timezone.utc)
        expires_at = (
            now + timedelta(minutes=minutes_valid)
        ).isoformat(timespec="seconds")

        with get_connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            # Only the newest code for an email remains valid.
            connection.execute(
                """
                DELETE FROM password_reset_codes
                WHERE email = ?
                """,
                (normalized_email,),
            )
            connection.execute(
                """
                INSERT INTO password_reset_codes (
                    email, code_hash, expires_at, attempts
                )
                VALUES (?, ?, ?, 0)
                """,
                (normalized_email, code_hash, expires_at),
            )

        return code

    def invalidate_codes(self, email):
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM password_reset_codes WHERE email = ?",
                (email.strip().lower(),),
            )

    def complete_reset(self, email, code, password_hash, max_attempts=5):
        """Validate the code and update the password in one transaction."""

        normalized_email = email.strip().lower()
        normalized_code = code.strip()
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        code_hash = self._hash_code(normalized_code)

        with get_connection() as connection:
            connection.execute("BEGIN IMMEDIATE")

            record = connection.execute(
                """
                SELECT reset_id, code_hash, expires_at, attempts, used_at
                FROM password_reset_codes
                WHERE email = ?
                ORDER BY reset_id DESC
                LIMIT 1
                """,
                (normalized_email,),
            ).fetchone()

            if record is None or record["used_at"] is not None:
                return False

            if record["attempts"] >= max_attempts:
                return False

            if record["expires_at"] <= now:
                return False

            if record["code_hash"] != code_hash:
                connection.execute(
                    """
                    UPDATE password_reset_codes
                    SET attempts = attempts + 1
                    WHERE reset_id = ?
                    """,
                    (record["reset_id"],),
                )
                return False

            user_cursor = connection.execute(
                """
                UPDATE users
                SET password_hash = ?
                WHERE email = ?
                  AND account_status = 'active'
                """,
                (password_hash, normalized_email),
            )

            if user_cursor.rowcount != 1:
                return False

            connection.execute(
                """
                UPDATE password_reset_codes
                SET used_at = ?
                WHERE reset_id = ?
                  AND used_at IS NULL
                """,
                (now, record["reset_id"]),
            )

            return True
