
from database.connection import get_connection


class SettingsRepository:
    def get_setting(self, setting_key, default=None):
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT setting_value
                FROM settings
                WHERE setting_key = ?
                """,
                (setting_key,),
            ).fetchone()

            if row is None:
                return default

            return row["setting_value"]

    def get_all_settings(self):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT setting_key, setting_value FROM settings"
            ).fetchall()

            return {
                row["setting_key"]: row["setting_value"]
                for row in rows
            }

    def update_setting(self, setting_key, setting_value):
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO settings (
                    setting_key, setting_value, updated_at
                )
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(setting_key)
                DO UPDATE SET
                    setting_value = excluded.setting_value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (setting_key, str(setting_value)),
            )
