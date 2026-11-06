
from models.person import Person


class Customer(Person):
    def __init__(self, user_id, username, email, student_number=None):
        super().__init__(user_id, username, email)
        self.student_number = student_number

    def get_dashboard_name(self):
        return "Customer Dashboard"


class Staff(Person):
    def __init__(self, user_id, username, email):
        super().__init__(user_id, username, email)

    def get_dashboard_name(self):
        return "Staff Dashboard"


class Manager(Person):
    def __init__(self, user_id, username, email):
        super().__init__(user_id, username, email)

    def get_dashboard_name(self):
        return "Manager Dashboard"


def create_user_object(user_data):
    role = user_data["role"]

    if role == "customer":
        return Customer(
            user_data["user_id"],
            user_data["username"],
            user_data["email"],
            user_data["student_number"],
        )

    if role == "staff":
        return Staff(
            user_data["user_id"],
            user_data["username"],
            user_data["email"],
        )

    if role == "manager":
        return Manager(
            user_data["user_id"],
            user_data["username"],
            user_data["email"],
        )

    raise ValueError("Invalid user role.")
