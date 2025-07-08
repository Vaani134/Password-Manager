import os
import json
from app.services.encryption import encrypt_data, decrypt_data  # Adjust this if your project uses a different path

VAULT_FOLDER = "vaults"

class VaultHandler:
    def __init__(self, username, key):
        self.username = username
        self.key = key
        self.filepath = os.path.join(VAULT_FOLDER, f"{self.username}.vault")

        if not os.path.exists(VAULT_FOLDER):
            os.makedirs(VAULT_FOLDER)

    def load_vault(self):
        if not os.path.exists(self.filepath):
            return {}

        with open(self.filepath, "r") as f:
            encrypted_data = f.read()

        try:
            decrypted_json = decrypt_data(self.key, encrypted_data)
            return json.loads(decrypted_json)
        except Exception as e:
            print("❌ Error decrypting vault:", e)
            return {}

    def save_vault(self, data):
        try:
            json_data = json.dumps(data)
            encrypted_data = encrypt_data(self.key, json_data)

            with open(self.filepath, "w") as f:
                f.write(encrypted_data)
        except Exception as e:
            print("❌ Error saving vault:", e)