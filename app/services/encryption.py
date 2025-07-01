from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

def generate_salt():
    """generating salt for password """
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
