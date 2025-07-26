import sqlite3

db_path = "instance/password_manager.db"
with sqlite3.connect(db_path) as conn:
    cursor = conn.execute("PRAGMA table_info(user_settings);")
    for row in cursor.fetchall():
        print(row) 