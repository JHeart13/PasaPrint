
from database.connection import get_connection


class FileRepository:
    def add_file(
        self,
        order_id,
        uploaded_by,
        file_type,
        original_filename,
        stored_filename,
        file_path,
        page_count=None,
    ):
        if file_type not in ("document", "proof"):
            raise ValueError("File type must be document or proof.")

        if page_count is not None and page_count <= 0:
            raise ValueError("Page count must be greater than zero.")

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO order_files (
                    order_id, uploaded_by, file_type,
                    original_filename, stored_filename,
                    file_path, page_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    uploaded_by,
                    file_type,
                    original_filename,
                    stored_filename,
                    file_path,
                    page_count,
                ),
            )

            return cursor.lastrowid

    def get_order_files(self, order_id):
        with get_connection() as connection:
            return connection.execute(
                """
                SELECT *
                FROM order_files
                WHERE order_id = ?
                ORDER BY uploaded_at ASC, file_id ASC
                """,
                (order_id,),
            ).fetchall()

    def get_files_by_type(self, order_id, file_type):
        if file_type not in ("document", "proof"):
            raise ValueError("Invalid file type.")

        with get_connection() as connection:
            return connection.execute(
                """
                SELECT *
                FROM order_files
                WHERE order_id = ? AND file_type = ?
                ORDER BY uploaded_at DESC, file_id DESC
                """,
                (order_id, file_type),
            ).fetchall()

    def delete_file_record(self, file_id):
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM order_files WHERE file_id = ?",
                (file_id,),
            )

            return cursor.rowcount > 0

    def get_customer_documents(self, customer_id):
        with get_connection() as connection:
            return connection.execute(
                """
                SELECT
                    f.*,
                    o.order_number,
                    o.status AS order_status
                FROM order_files f
                JOIN orders o ON f.order_id = o.order_id
                WHERE o.customer_id = ?
                AND f.file_type = 'document'
                ORDER BY f.uploaded_at DESC, f.file_id DESC
                """,
                (customer_id,)
            ).fetchall()


    def get_customer_proofs(self, customer_id):
        with get_connection() as connection:
            return connection.execute(
                """
                SELECT
                    f.*,
                    o.order_number,
                    o.status AS order_status
                FROM order_files f
                JOIN orders o ON f.order_id = o.order_id
                WHERE o.customer_id = ?
                AND f.file_type = 'proof'
                ORDER BY f.uploaded_at DESC, f.file_id DESC
                """,
                (customer_id,)
            ).fetchall()

    
