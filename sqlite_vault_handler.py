import sqlite3
import json
from app.services.encryption import encrypt_data, decrypt_data

DB_NAME = "password_manager.db"

def init_vault_table():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vaults (
                username TEXT PRIMARY KEY,
                encrypted_data TEXT NOT NULL
            )
        """)

class VaultHandler:
    def __init__(self, username: str, key: bytes):
        self.username = username
        self.key = key
        init_vault_table()

    def save_vault(self, data: dict):
        json_data = json.dumps(data)
        encrypted = encrypt_data(self.key, json_data)

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                INSERT INTO vaults (username, encrypted_data)
                VALUES (?, ?)
                ON CONFLICT(username) DO UPDATE SET encrypted_data=excluded.encrypted_data
            """, (self.username, encrypted))

    def load_vault(self) -> dict:
        with sqlite3.connect(DB_NAME) as conn:
            result = conn.execute("SELECT encrypted_data FROM vaults WHERE username = ?", (self.username,)).fetchone()

        if result:
            decrypted = decrypt_data(self.key, result[0])
            return json.loads(decrypted)
        else:
            return {}