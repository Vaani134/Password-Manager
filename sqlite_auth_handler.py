import sqlite3
from app.services.encryption import generate_salt, derive_key
from typing import Optional

DB_NAME = "password_manager.db"

def init_user_table():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                salt BLOB NOT NULL
            )
        """)

def register_user(username: str, master_password: str) -> bool:
    init_user_table()
    salt = generate_salt()
    key = derive_key(master_password, salt)

    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO users (username, salt) VALUES (?, ?)", (username, salt))
        print("✅ User registered.")
        return True
    except sqlite3.IntegrityError:
        print("❌ User already exists.")
        return False

def verify_user(username: str, master_password: str) -> Optional[bytes]:
    with sqlite3.connect(DB_NAME) as conn:
        result = conn.execute("SELECT salt FROM users WHERE username = ?", (username,)).fetchone()

    if result:
        salt = result[0]
        key = derive_key(master_password, salt)
        return key
    else:
        print("❌ User not found.")
        return None
