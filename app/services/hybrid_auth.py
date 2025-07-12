"""Hybrid authentication service combining SQLAlchemy and SQLite vault auth."""

from flask import session
from werkzeug.security import check_password_hash
from ..models import User
from .sqlite.auth_handler import verify_user as sqlite_verify_user
from .encryption import derive_key
import base64

def verify_master_password_hybrid(user_id:int ,master_password :str):
    """Verify master password using SQLAlchemy User model."""
    user=User.query.get(user_id)
    if not user:
        return None,None
    # Verify using existing SQLAlchemy hash check
    if check_password_hash(user.password_hash,master_password):
         # Get salt and derive key for vault operations
        salt_bytes=base64.b64decode(user.Salted_masterkey)
        key=derive_key(master_password,salt_bytes)
        return key , user 
    return None, None
def get_current_user():
    """Get current user from session."""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])