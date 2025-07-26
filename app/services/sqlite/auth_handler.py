import sqlite3
from ..encryption import generate_salt, derive_key
from typing import Optional

DB_NAME = "instance/password_manager.db"
print(f"[DEBUG] Using database file: {DB_NAME}")

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

def init_profile_tables():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                item TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                filename TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                username TEXT PRIMARY KEY,
                language TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

# Favorites

def add_favorite(username, item):
    init_profile_tables()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO favorites (username, item) VALUES (?, ?)", (username, item))

def get_favorites(username):
    init_profile_tables()
    with sqlite3.connect(DB_NAME) as conn:
        return [row[0] for row in conn.execute("SELECT item FROM favorites WHERE username = ?", (username,))]

def remove_favorite(username, item):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM favorites WHERE username = ? AND item = ?", (username, item))

# Downloads

def log_download(username, filename):
    init_profile_tables()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO downloads (username, filename) VALUES (?, ?)", (username, filename))

def get_downloads(username):
    init_profile_tables()
    with sqlite3.connect(DB_NAME) as conn:
        return [(row[0], row[1]) for row in conn.execute("SELECT filename, timestamp FROM downloads WHERE username = ? ORDER BY timestamp DESC", (username,))]

def remove_download(username, filename):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM downloads WHERE username = ? AND filename = ?", (username, filename))

# Location & Language

def set_user_setting(username, language=None):
    init_profile_tables()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR REPLACE INTO user_settings (username, language) VALUES (?, COALESCE(?, language))", (username, language))

def get_user_setting(username):
    init_profile_tables()
    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute("SELECT language FROM user_settings WHERE username = ?", (username,)).fetchone()
        return row if row else (None, None)

# History

def log_history(username, action):
    init_profile_tables()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO history (username, action) VALUES (?, ?)", (username, action))

def get_history(username, limit=10):
    init_profile_tables()
    with sqlite3.connect(DB_NAME) as conn:
        return [(row[0], row[1]) for row in conn.execute("SELECT action, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC LIMIT ?", (username, limit))]
