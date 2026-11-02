
from database.connection import initialize_database
from database.user_repository import UserRepository
from database.order_repository import OrderRepository
from database.settings_repository import SettingsRepository


def main():
    initialize_database()
    print("Database initialized.")

    settings = SettingsRepository()
    print("Default settings:", settings.get_all_settings())

    users = UserRepository()
    test_email = "database_test@example.com"

    existing_user = users.get_by_email(test_email)

    if existing_user:
        customer_id = existing_user["user_id"]
        print("Test user already exists:", customer_id)
    else:
        customer_id = users.create_user(
            username="Test Customer",
            email=test_email,
            password_hash="TEST_HASH_ONLY",
            role="customer",
            student_number="TEST-0001",
        )
        print("Test customer created:", customer_id)

    customer = users.get_by_id(customer_id)
    print("Retrieved user:", customer["username"], customer["role"])

    orders = OrderRepository()
    print("Customer orders:", len(orders.get_customer_orders(customer_id)))

    print("Stage 1 database test completed.")


if __name__ == "__main__":
    main()
