import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from database.connection import get_connection
from database.authorization_repository import AuthorizationRepository


class StaffAccessRepository:
    def _hash(self, value):
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _ensure_table(self):
        with get_connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS staff_access_requests (
                    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    applicant_email TEXT NOT NULL,
                    manager_id INTEGER NOT NULL,
                    token_hash TEXT NOT NULL UNIQUE,
                    expires_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending'
                        CHECK(status IN ('pending','approved','expired')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    approved_at TEXT,
                    FOREIGN KEY(manager_id) REFERENCES users(user_id)
                )
            """)

    def create_request(self, applicant_email):
        self._ensure_table()
        email = applicant_email.strip().lower()
        token = secrets.token_urlsafe(32)
        expires = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat(timespec="seconds")
        with get_connection() as connection:
            manager = connection.execute("SELECT user_id,email,username FROM users WHERE role='manager' AND account_status='active' ORDER BY user_id LIMIT 1").fetchone()
            if manager is None:
                raise ValueError("No active manager account was found.")
            connection.execute("UPDATE staff_access_requests SET status='expired' WHERE applicant_email=? AND status='pending'", (email,))
            connection.execute("INSERT INTO staff_access_requests (applicant_email,manager_id,token_hash,expires_at) VALUES (?,?,?,?)", (email, manager['user_id'], self._hash(token), expires))
        return {"token": token, "manager": dict(manager)}

    def approve(self, token):
        self._ensure_table()
        token_hash = self._hash(token)
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with get_connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            request = connection.execute("""SELECT request_id,applicant_email,manager_id,expires_at,status
                FROM staff_access_requests WHERE token_hash=?""", (token_hash,)).fetchone()
            if request is None or request['status'] != 'pending' or request['expires_at'] <= now:
                return None
            manager = connection.execute("SELECT role,account_status FROM users WHERE user_id=?", (request['manager_id'],)).fetchone()
            if manager is None or manager['role'] != 'manager' or manager['account_status'] != 'active':
                return None
            changed = connection.execute("UPDATE staff_access_requests SET status='approved',approved_at=? WHERE request_id=? AND status='pending'", (now, request['request_id']))
            if changed.rowcount != 1:
                return None
            email = request['applicant_email']
            manager_id = request['manager_id']
        code = AuthorizationRepository().create_code(email, manager_id, minutes_valid=1440)
        return {"email": email, "code": code}
