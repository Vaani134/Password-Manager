import os
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

BLOCK_SIZE = 16  # AES block size in bytes

def encrypt_data(key: bytes, plaintext: str) -> str:
    iv = os.urandom(BLOCK_SIZE)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return b64encode(iv + ciphertext).decode('utf-8')

def decrypt_data(key: bytes, b64_ciphertext: str) -> str:
    iv_ciphertext = b64decode(b64_ciphertext)
    iv = iv_ciphertext[:BLOCK_SIZE]
    ciphertext = iv_ciphertext[BLOCK_SIZE:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext.decode('utf-8')


from hashlib import pbkdf2_hmac

def generate_salt() -> bytes:
    """
    Generates a secure 16-byte salt using os.urandom.
    """
    return os.urandom(16)

def derive_key(password: str, salt: bytes, iterations: int = 100_000) -> bytes:
    """
    Derives a 32-byte (256-bit) key from the password and salt using PBKDF2-HMAC-SHA256.
    """
    key = pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode(),
        salt=salt,
        iterations=iterations,
        dklen=32  # 256-bit key
    )
    return key
