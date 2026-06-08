import sqlite3
import bcrypt

DB_PATH = "studybuddy.db"

def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Hash the password — never store plain text
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )

        conn.commit()
        conn.close()
        return True, "Account created successfully!"

    except sqlite3.IntegrityError:
        return False, "Username already exists. Try another."

def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        user_id, stored_hash = result
        if bcrypt.checkpw(password.encode(), stored_hash):
            return True, user_id  # Login success, return user_id
        else:
            return False, "Wrong password."
    else:
        return False, "Username not found."