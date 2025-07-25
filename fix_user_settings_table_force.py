import sqlite3

db_path = "instance/password_manager.db"
with sqlite3.connect(db_path) as conn:
    # Try to preserve usernames if table exists
    try:
        usernames = [row[0] for row in conn.execute("SELECT username FROM user_settings").fetchall()]
    except sqlite3.OperationalError:
        usernames = []
    # Drop the table if it exists
    try:
        conn.execute("DROP TABLE IF EXISTS user_settings;")
        print("Dropped old user_settings table.")
    except Exception as e:
        print(f"Error dropping table: {e}")
    # Create new table
    conn.execute("""
        CREATE TABLE user_settings (
            username TEXT PRIMARY KEY,
            location TEXT,
            language TEXT
        );
    """)
    print("Created new user_settings table.")
    # Restore usernames
    for username in usernames:
        conn.execute("INSERT INTO user_settings (username) VALUES (?)", (username,))
    print("Restored usernames.")
    print("user_settings table is now fixed.") 