import sqlite3

db_path = "instance/password_manager.db"
with sqlite3.connect(db_path) as conn:
    cursor = conn.execute("PRAGMA table_info(user_settings);")
    columns = [row[1] for row in cursor.fetchall()]
    if "location" not in columns or "language" not in columns:
        print("Recreating user_settings table with location and language columns...")
        # Rename old table
        conn.execute("ALTER TABLE user_settings RENAME TO user_settings_old;")
        # Create new table
        conn.execute("""
            CREATE TABLE user_settings (
                username TEXT PRIMARY KEY,
                location TEXT,
                language TEXT
            );
        """)
        # Copy data (only username if that's all that exists)
        conn.execute("""
            INSERT INTO user_settings (username)
            SELECT username FROM user_settings_old;
        """)
        # Drop old table
        conn.execute("DROP TABLE user_settings_old;")
        print("user_settings table recreated.")
    else:
        print("user_settings table already has the correct columns.") 