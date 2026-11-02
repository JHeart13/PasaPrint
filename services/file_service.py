from pathlib import Path

from database.connection import PROJECT_ROOT
from database.file_repository import FileRepository


class FileService:
    """
    Handles file retrieval, validation, and access for PasaPrint.

    File records are stored in the database.
    Actual uploaded files are stored inside the project directory.
    """

    def __init__(self):
        self.file_repository = FileRepository()
        self.project_root = PROJECT_ROOT.resolve()

    def get_customer_documents(self, customer_id):
        """Retrieve all documents uploaded by a customer."""

        if not customer_id:
            return []

        return self.file_repository.get_customer_documents(customer_id)

    def get_customer_proofs(self, customer_id):
        """Retrieve all staff proofs associated with a customer's orders."""

        if not customer_id:
            return []

        return self.file_repository.get_customer_proofs(customer_id)

    def get_recent_customer_documents(self, customer_id, limit=5):
        """Retrieve the most recent uploaded documents."""

        if limit <= 0:
            return []

        documents = self.get_customer_documents(customer_id)
        return documents[:limit]

    def get_order_files(self, order_id):
        """Retrieve all files attached to a specific order."""

        if not order_id:
            return []

        return self.file_repository.get_order_files(order_id)

    def get_order_documents(self, order_id):
        """Retrieve customer-uploaded documents for an order."""

        if not order_id:
            return []

        return self.file_repository.get_files_by_type(
            order_id,
            "document"
        )

    def get_order_proofs(self, order_id):
        """Retrieve staff proofs for an order."""

        if not order_id:
            return []

        return self.file_repository.get_files_by_type(
            order_id,
            "proof"
        )

    def get_file_path(self, file_record):
        """
        Resolve a database file path into an absolute path.

        Prevents paths from accessing files outside the project folder.
        Returns None if the file does not exist or its path is invalid.
        """

        if not file_record:
            return None

        try:
            relative_path = file_record["file_path"]

            if not relative_path:
                return None

            file_path = (self.project_root / relative_path).resolve()

            # Ensure the resolved path stays inside the project directory.
            if not file_path.is_relative_to(self.project_root):
                return None

            if not file_path.is_file():
                return None

            return file_path

        except (KeyError, TypeError, ValueError, OSError):
            return None

    def get_file_bytes(self, file_record):
        """Read a stored file and return its contents as bytes."""

        file_path = self.get_file_path(file_record)

        if file_path is None:
            return None

        try:
            return file_path.read_bytes()
        except OSError:
            return None

    def file_exists(self, file_record):
        """Check whether the physical file exists."""

        return self.get_file_path(file_record) is not None

    def delete_file(self, file_record):
        """
        Delete a physical file and its database record.

        Returns True only when the file record was successfully deleted.
        """

        if not file_record:
            return False

        try:
            file_id = file_record["file_id"]
        except (KeyError, TypeError):
            return False

        file_path = self.get_file_path(file_record)

        if file_path is None:
            return False

        try:
            file_path.unlink()

            deleted = self.file_repository.delete_file_record(file_id)

            return deleted

        except OSError:
            return False
