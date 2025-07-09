# 🔐 Password Manager Security Module Integration Guide

**Prepared by:** Saksham 
**For:** Backend Team – Flask Integration

---

## 📁 Module Overview

| Module                | File                         | Purpose                                                      |
| --------------------- | ---------------------------- | ------------------------------------------------------------ |
| AES Encryption        | `app/services/encryption.py` | Encrypt/decrypt vault data securely                          |
| Vault Handler         | `vault_handler.py`           | Save/load full encrypted user vault                          |
| Authentication System | `auth_handler.py`            | Register and verify user credentials using a master password |
| Session Manager       | `session_manager.py`         | Handle login session timeout & auto logout                   |

---

## ✅ Deliverable 1: AES Encryption Module

**File:** `app/services/encryption.py`\
**Functions Provided:**

```python
encrypt_data(key: bytes, plaintext: str) -> str
decrypt_data(key: bytes, b64_ciphertext: str) -> str
generate_salt() -> bytes
derive_key(password: str, salt: bytes) -> bytes
```

### ✅ Use Case:

```python
key = derive_key("MyPassword", salt)
cipher = encrypt_data(key, "my secret")
plain = decrypt_data(key, cipher)
```

---

## ✅ Deliverable 2: Key Derivation (PBKDF2)

**Integrated with:** `app/services/encryption.py`

- `derive_key()` uses PBKDF2-HMAC-SHA256 with salt and iterations.

**Use:** For all encryption operations or password verification.

---

## ✅ Deliverable 3: Vault Encryption Handler

**File:** `vault_handler.py`\
**Class:** `VaultHandler`

### ✅ Methods:

```python
VaultHandler(username: str, key: bytes)
vault.save_vault(data: dict)  # Encrypt & save
vault.load_vault() -> dict    # Decrypt & load
```

### ✅ Usage:

```python
vault = VaultHandler("saksham", key)
vault.save_vault({"gmail.com": {"username": "sam", "password": "pass"}})
vault.load_vault()
```

**Storage Path:**\
Saves encrypted vaults as `/vaults/<username>.vault`

---

## ✅ Deliverable 4: Master Password Auth System

**File:** `auth_handler.py`\
**Functions:**

```python
register_user(username: str, master_password: str) -> bool
verify_user(username: str, master_password: str) -> Optional[bytes]
```

### ✅ Usage:

```python
# Registration
success = register_user("saksham", "MyPassword")

# Login (returns key if valid)
key = verify_user("saksham", "MyPassword")
if key:
    # proceed to load vault
```

**Storage Path:**\
Stores salt at `/user_data/<username>/salt.bin`

---

## ✅ Deliverable 5: Session Management System

**File:** `session_manager.py`\
**Functions:**

```python
start_session(username: str)
is_session_active() -> bool
update_activity()
end_session()
```

### ✅ Usage:

```python
# After login
start_session("saksham")

# On any action
if is_session_active():
    update_activity()
else:
    # redirect to login
```

**Storage:** Uses `session.json` to persist session info.\
**Timeout:** Set to 5 minutes (configurable via `SESSION_TIMEOUT`)

---

## 📌 Suggested Integration Flow (Flask Backend)

```python
from auth_handler import verify_user
from vault_handler import VaultHandler
from session_manager import start_session, is_session_active, update_activity

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    key = verify_user(username, password)
    if key:
        start_session(username)
        # Save key in session/global (securely)
        return redirect("/dashboard")
    else:
        return "Invalid credentials", 401
```

---

## 📉 To-Do for Backend Team

- Call `update_activity()` on every user interaction
- Redirect user to `/login` if `is_session_active()` returns `False`
- Keep derived key secure in memory (not cookies!)
- On logout or timeout, call `end_session()`

---

## 💬 Questions?

Feel free to ping me (Saksham) for:

- Adding support for hashed master password files
- Multi-user vault sync
- UI integration help or backend bugs

---

