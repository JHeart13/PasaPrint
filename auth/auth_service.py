import re
import sqlite3

from auth.password_utils import hash_password, verify_password
from database.user_repository import UserRepository
from database.authorization_repository import AuthorizationRepository
from database.password_reset_repository import PasswordResetRepository
from notifications.email_service import send_password_reset_email


class AuthService:
    def __init__(self):
        self.users = UserRepository()
        self.authorization = AuthorizationRepository()
        self.password_resets = PasswordResetRepository()

    def _validate_email(self, email):
        email = email.strip().lower()

        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.match(pattern, email):
            raise ValueError("Please enter a valid email address.")

        return email

    def _validate_password(self, password):
        if not isinstance(password, str) or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        if len(password) > 128:
            raise ValueError("Password must not exceed 128 characters.")

    def register_customer(
        self,
        username,
        student_number,
        email,
        password,
        confirm_password,
    ):
        username = username.strip()
        student_number = student_number.strip()
        email = self._validate_email(email)

        if not username:
            raise ValueError("Username is required.")

        if not student_number:
            raise ValueError("Student number is required.")

        if password != confirm_password:
            raise ValueError("Passwords do not match.")

        self._validate_password(password)

        password_hash = hash_password(password)

        try:
            user_id = self.users.create_user(
                username=username,
                email=email,
                password_hash=password_hash,
                role="customer",
                student_number=student_number,
                account_status="active",
            )
        except sqlite3.IntegrityError as error:
            raise ValueError(
                "This email or student number is already registered."
            ) from error

        return user_id

    def register_staff(
        self,
        username,
        email,
        password,
        confirm_password,
        authorization_code,
    ):
        username = username.strip()
        email = self._validate_email(email)

        if not username:
            raise ValueError("Username is required.")

        if password != confirm_password:
            raise ValueError("Passwords do not match.")

        self._validate_password(password)

        if not authorization_code.strip():
            raise ValueError("Authorization code is required.")

        if self.users.get_by_email(email):
            raise ValueError("This email is already registered.")

        # The code is tied to this email and can only be used once.
        verified = self.authorization.verify_and_consume(
            authorization_code,
            email,
        )

        if not verified:
            raise ValueError(
                "Invalid, expired, or already-used authorization code."
            )

        password_hash = hash_password(password)

        try:
            return self.users.create_user(
                username=username,
                email=email,
                password_hash=password_hash,
                role="staff",
                account_status="active",
            )
        except sqlite3.IntegrityError as error:
            raise ValueError(
                "This account could not be created. "
                "The email may already be registered."
            ) from error

    def login(self, email, password):
        email = self._validate_email(email)
        user = self.users.get_by_email(email)

        if user is None:
            raise ValueError("Invalid email or password.")

        if not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid email or password.")

        if user["account_status"] != "active":
            raise ValueError("This account is not active.")

        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "student_number": user["student_number"],
        }


    def request_password_reset(self, email):
        """Send a reset code when an active account exists for the email.

        The caller should always display a generic response so account
        existence is not disclosed.
        """

        email = self._validate_email(email)
        user = self.users.get_by_email(email)

        if user is None or user["account_status"] != "active":
            return

        reset_code = self.password_resets.create_code(
            email=email,
            minutes_valid=10,
        )

        try:
            send_password_reset_email(
                to_email=email,
                reset_code=reset_code,
            )
        except Exception:
            self.password_resets.invalidate_codes(email)
            raise

    def reset_password(
        self,
        email,
        reset_code,
        new_password,
        confirm_password,
    ):
        """Reset an active user's password with a valid one-time code."""

        email = self._validate_email(email)

        if not reset_code or not reset_code.strip():
            raise ValueError("Please enter the password reset code.")

        if new_password != confirm_password:
            raise ValueError("Your passwords do not match.")

        self._validate_password(new_password)

        password_hash = hash_password(new_password)

        completed = self.password_resets.complete_reset(
            email=email,
            code=reset_code,
            password_hash=password_hash,
            max_attempts=5,
        )

        if not completed:
            raise ValueError(
                "The reset code is invalid, expired, already used, "
                "or has exceeded the maximum number of attempts. "
                "Please request a new code."
            )

        return True
