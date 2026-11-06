
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_FOLDER / "pasaprint.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection():
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        schema = file.read()

    with get_connection() as connection:
        connection.executescript(schema)

        default_settings = [
            ("black_white_price", "2.00"),
            ("color_price", "5.00"),
            ("delivery_fee", "10.00"),
            ("pickup_fee", "0.00"),
        ]

        connection.executemany(
            """
            INSERT OR IGNORE INTO settings (setting_key, setting_value)
            VALUES (?, ?)
            """,
            default_settings,
        )


if __name__ == "__main__":
    initialize_database()
    print("PasaPrint database initialized successfully!")
