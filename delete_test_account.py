import sqlite3

# Replace this with the exact DATABASE_PATH from your project.
DATABASE_PATH = r"data/pasaprint.db"

conn = sqlite3.connect(DATABASE_PATH)
conn.execute("PRAGMA foreign_keys = ON")

try:
    users = conn.execute("""
        SELECT user_id, username, email, student_number, role
        FROM users
        ORDER BY user_id
    """).fetchall()

    print("\nAccounts in this database:")
    for user in users:
        print(user)

    user_id = input(
        "\nEnter the user_id of ONLY your test account to delete: "
    ).strip()

    confirm = input(
        f"Type DELETE {user_id} to confirm: "
    ).strip()

    if confirm == f"DELETE {user_id}":
        conn.execute(
            "DELETE FROM users WHERE user_id = ?",
            (int(user_id),)
        )
        conn.commit()
        print("Account deleted.")
    else:
        print("Cancelled. No account was deleted.")

finally:
    conn.close()