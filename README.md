# Password Manager

A secure, modern password manager built with Flask, supporting encrypted password storage, user authentication, and vault import/export features.

## Features
- User registration and login (with hashed passwords)
- Store, edit, delete, and organize passwords in folders
- Encrypted password storage using AES (cryptography library)
- Import/export vault functionality
- User profile management
- Trash and restore deleted passwords
- Download logs and favorites
- Delete all passwords functionality with confirmation modal
- RESTful API endpoints for integration

## Requirements
See `requirements.txt` for all dependencies. Install with:

```bash
pip install -r requirements.txt
```

## Setup & Running
1. Clone the repository and navigate to the project directory.
2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python run.py
   ```
   The app will start on http://127.0.0.1:5000 by default.

## Project Structure
- `app/` - Main application package
  - `models.py` - SQLAlchemy models (User, Folder, User_passwords)
  - `routes/` - Flask blueprints for authentication, vault, and password management
  - `services/` - Encryption, hybrid vault, and database logic
  - `static/` - CSS, JS, and images
  - `templates/` - HTML templates
- `instance/password_manager.db` - SQLite database
- `run.py` - Application entry point

## API Endpoints
### Auth
- `POST /api/auth/signup` - Register a new user
- `POST /api/auth/signin` - User login

### Vault
- `POST /api/vault/export` - Export all user passwords to encrypted vault
- `POST /api/vault/import` - Import vault data
- `POST /api/vault/sync` - Sync vault data back to database

### Passwords
- `GET /api/passwords` - List all passwords
- `POST /api/passwords` - Add a new password
- `PUT /api/passwords/<password_id>` - Edit a password
- `DELETE /api/passwords/<password_id>` - Delete a password
- `POST /api/passwords/delete_all` - Delete all passwords for the current user
- `GET /api/passwords/grouped` - List passwords grouped by folder
- `PUT /api/passwords/<password_id>/folder` - Move password to folder
- `PUT /api/passwords/<password_id>/trash` - Move password to trash
- `GET /api/passwords/trashed` - List trashed passwords
- `PUT /api/passwords/<password_id>/restore` - Restore trashed password
- `DELETE /api/passwords/<password_id>/delete` - Permanently delete password

### Folders
- `GET /api/folders` - List folders
- `POST /api/folders` - Create folder
- `PUT /api/folders/<folder_id>` - Rename folder
- `DELETE /api/folders/<folder_id>` - Delete folder

## Database
- Uses SQLite by default (see `instance/password_manager.db`).
- Models: User, Folder, User_passwords.

## Security
- Passwords are encrypted using AES (cryptography library) with a key derived from the user's master password and a unique salt.
- User authentication uses Flask-Login and bcrypt for password hashing.

## License
MIT License
