
from database.connection import get_connection
from database.authorization_repository import AuthorizationRepository
from notifications.email_service import send_staff_authorization_email


def generate_staff_code():
    print("\n===== PASAPRINT STAFF CODE GENERATOR =====\n")

    email = input("Enter the staff member's email: ").strip().lower()

    if not email or "@" not in email:
        print("Invalid email address.")
        return

    # Find an active manager account
    with get_connection() as connection:
        manager = connection.execute(
            """
            SELECT user_id
            FROM users
            WHERE role = 'manager'
              AND account_status = 'active'
            ORDER BY user_id
            LIMIT 1
            """
        ).fetchone()

        existing_user = connection.execute(
            "SELECT user_id FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    if manager is None:
        print("No active manager account found.")
        return

    if existing_user is not None:
        print("This email is already registered.")
        return

    try:
        repository = AuthorizationRepository()

        # Generate and save the authorization code
        code = repository.create_code(
            intended_email=email,
            manager_id=manager["user_id"],
            minutes_valid=1440,
        )

        # Send the code through Gmail
        send_staff_authorization_email(
            to_email=email,
            authorization_code=code,
        )

        print("\nSTAFF INVITATION SENT SUCCESSFULLY!")
        print("-----------------------------------")
        print(f"Recipient: {email}")
        print("Authorization code sent via email.")
        print("Expiration: 24 hours")
        print("-----------------------------------")

    except Exception as error:
        print("\nUnable to complete the staff invitation.")
        print(f"Error: {error}")
        print(
            "If the code was already saved, it may remain valid "
            "until it expires. Do not assume it was revoked."
        )


if __name__ == "__main__":
    generate_staff_code()
