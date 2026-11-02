
from secrets import token_hex

from database.connection import initialize_database
from auth.password_utils import hash_password, verify_password
from auth.auth_service import AuthService


def main():
    initialize_database()

    auth = AuthService()
    unique_id = token_hex(4)

    email = f"auth_test_{unique_id}@example.com"
    student_number = f"TEST-{unique_id.upper()}"
    password = "TestPassword123!"

    # Test password hashing.
    stored_hash = hash_password(password)

    assert stored_hash != password
    assert verify_password(password, stored_hash)
    assert not verify_password("WrongPassword123!", stored_hash)

    print("Password hashing and verification passed.")

    # Test customer registration.
    user_id = auth.register_customer(
        username="Authentication Test",
        student_number=student_number,
        email=email,
        password=password,
        confirm_password=password,
    )

    print("Test customer registered:", user_id)

    # Test successful login.
    user = auth.login(email, password)

    assert user["user_id"] == user_id
    assert user["role"] == "customer"
    assert user["student_number"] == student_number

    print("Successful login passed.")

    # Test incorrect password.
    try:
        auth.login(email, "IncorrectPassword123!")
    except ValueError:
        print("Incorrect password correctly rejected.")
    else:
        raise AssertionError("Incorrect password was accepted.")

    # Test duplicate registration.
    try:
        auth.register_customer(
            username="Duplicate Test",
            student_number=student_number,
            email=email,
            password=password,
            confirm_password=password,
        )
    except ValueError:
        print("Duplicate registration correctly rejected.")
    else:
        raise AssertionError("Duplicate registration was accepted.")

    print("All authentication tests passed.")


if __name__ == "__main__":
    main()
