import os
from typing import Optional
from app.services.encryption import generate_salt, derive_key

USER_DATA_FOLDER = "user_data"

def get_user_folder(username: str) -> str:
    return os.path.join(USER_DATA_FOLDER, username)

def get_salt_path(username: str) -> str:
    return os.path.join(get_user_folder(username), "salt.bin")

def register_user(username: str, master_password: str) -> bool:
    user_folder = get_user_folder(username)

    if os.path.exists(user_folder):
        print("❌ User already exists.")
        return False

    os.makedirs(user_folder)
    salt = generate_salt()
    key = derive_key(master_password, salt)

    with open(get_salt_path(username), "wb") as f:
        f.write(salt)

    print("✅ User registered successfully.")
    return True

def verify_user(username: str, master_password: str) -> Optional[bytes]:
    salt_path = get_salt_path(username)

    if not os.path.exists(salt_path):
        print("❌ User not found.")
        return None

    with open(salt_path, "rb") as f:
        salt = f.read()

    key = derive_key(master_password, salt)
    return key