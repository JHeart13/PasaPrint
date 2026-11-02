
from database.authorization_repository import AuthorizationRepository
from database.user_repository import UserRepository


class StaffAuthorizationService:
    def __init__(self):
        self.authorization = AuthorizationRepository()
        self.users = UserRepository()

    def issue_code(self, manager_id, intended_email):
        manager = self.users.get_by_id(manager_id)

        if manager is None:
            raise PermissionError("Manager account not found.")

        if (
            manager["role"] != "manager"
            or manager["account_status"] != "active"
        ):
            raise PermissionError(
                "Only an active manager can authorize staff."
            )

        intended_email = intended_email.strip().lower()

        if not intended_email:
            raise ValueError("Staff email is required.")

        if self.users.get_by_email(intended_email):
            raise ValueError("This email is already registered.")

        return self.authorization.create_code(
            intended_email=intended_email,
            manager_id=manager_id,
            minutes_valid=10,
        )
