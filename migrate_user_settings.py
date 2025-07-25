import sqlite3

db_path = "instance/password_manager.db"
with sqlite3.connect(db_path) as conn:
    try:
        conn.execute("ALTER TABLE user_settings ADD COLUMN location TEXT;")
        print("Added 'location' column.")
    except sqlite3.OperationalError:
        print("'location' column already exists.")
    try:
        conn.execute("ALTER TABLE user_settings ADD COLUMN language TEXT;")
        print("Added 'language' column.")
    except sqlite3.OperationalError:
        print("'language' column already exists.")
print("Migration complete.") 