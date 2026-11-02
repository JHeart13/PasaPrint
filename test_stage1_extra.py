
from datetime import datetime
from secrets import token_hex

from database.connection import initialize_database
from database.user_repository import UserRepository
from database.order_repository import OrderRepository
from database.file_repository import FileRepository
from database.authorization_repository import AuthorizationRepository
from database.settings_repository import SettingsRepository
from services.pricing_service import PricingService


def main():
    initialize_database()

    users = UserRepository()
    orders = OrderRepository()
    files = FileRepository()
    authorization = AuthorizationRepository()

    # Create or reuse test accounts.
    manager_email = "manager_test@example.com"
    manager = users.get_by_email(manager_email)

    if manager is None:
        manager_id = users.create_user(
            username="Test Manager",
            email=manager_email,
            password_hash="TEST_HASH_ONLY",
            role="manager",
        )
    else:
        manager_id = manager["user_id"]

    customer = users.get_by_email("database_test@example.com")

    if customer is None:
        customer_id = users.create_user(
            username="Test Customer",
            email="database_test@example.com",
            password_hash="TEST_HASH_ONLY",
            role="customer",
            student_number="TEST-0001",
        )
    else:
        customer_id = customer["user_id"]

    # Test pricing.
    pricing = PricingService()
    quote = pricing.calculate_total(
        total_pages=10,
        copies=2,
        color_mode="black_white",
        fulfillment_method="pickup",
    )
    print("Price quote:", quote)

    # Test staff authorization code.
    code = authorization.create_code(
        intended_email="staff_test@example.com",
        manager_id=manager_id,
    )

    first_use = authorization.verify_and_consume(
        code,
        "staff_test@example.com",
    )
    second_use = authorization.verify_and_consume(
        code,
        "staff_test@example.com",
    )

    assert first_use is True
    assert second_use is False
    print("One-time authorization code test passed.")

    # Create a test order.
    order_number = "TEST-" + token_hex(4).upper()

    quote = pricing.calculate_total(
        total_pages=2,
        copies=1,
        color_mode="black_white",
        fulfillment_method="pickup",
    )

    order_data = {
        "order_number": order_number,
        "customer_id": customer_id,
        "fulfillment_method": "pickup",
        "campus": "TIP Manila",
        "pickup_location": "Test Pickup Point",
        "building": None,
        "floor": None,
        "room": None,
        "delivery_notes": None,
        "color_mode": "black_white",
        "paper_size": "A4",
        "print_sides": "single",
        "copies": 1,
        "total_pages": 2,
        "price_per_page": float(quote["price_per_page"]),
        "printing_cost": float(quote["printing_cost"]),
        "delivery_fee": float(quote["delivery_fee"]),
        "total_cost": float(quote["total_cost"]),
        "customer_notes": "Test order only.",
    }

    order_id = orders.create_order(order_data)
    print("Test order created:", order_id)

    # Test file metadata.
    file_id = files.add_file(
        order_id=order_id,
        uploaded_by=customer_id,
        file_type="document",
        original_filename="sample.pdf",
        stored_filename="test_sample.pdf",
        file_path="data/uploads/test_sample.pdf",
        page_count=2,
    )

    assert len(files.get_order_files(order_id)) == 1
    print("File metadata test passed:", file_id)

    # Test status update and history.
    orders.update_order_status(
        order_id=order_id,
        new_status="confirmed",
        changed_by=manager_id,
        notes="Test confirmation.",
    )

    updated_order = orders.get_order_by_id(order_id)
    history = orders.get_status_history(order_id)

    assert updated_order["status"] == "confirmed"
    assert len(history) == 2
    print("Order status and history test passed.")

    # Test that an invalid transition is rejected.
    try:
        orders.update_order_status(
            order_id=order_id,
            new_status="completed",
            changed_by=manager_id,
            notes="Invalid direct completion test.",
        )
    except ValueError:
        print("Invalid status transition correctly rejected.")
    else:
        raise AssertionError("Invalid status transition was accepted.")

    print("All additional Stage 1 tests passed.")


if __name__ == "__main__":
    main()
