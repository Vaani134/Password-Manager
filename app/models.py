#database scgema
from .services.encryption import generate_salt ,derive_key , encrypt_data ,decrypt_data
import base64
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db

class User(db.Model):
    """user model for auth."""
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(40),unique=True,nullable=False)
    password_hash=db.Column(db.String(50),nullable=False)
    Salted_masterkey=db.Column(db.String(50),nullable=False)
    create_time=db.Column(db.DateTime,default=datetime.utcnow)
    last_login=db.Column(db.DateTime)
    name = db.Column(db.String(50), nullable=True)
    photo_url = db.Column(db.String(200), nullable=True)
    #get all passwords fr the user
    passwords = db.relationship('User_passwords', backref='owner', lazy=True)

    def generate_master_key(self):
        """Generate and store salt for master password encryption"""
        salt_bytes=generate_salt()  #generate random salt
        self.Salted_masterkey=base64.b64encode(salt_bytes).decode('utf-8')



    
class Folder(db.Model):
    __tablename__ = 'folders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)
    # Optionally, add created_at, updated_at fields

# Update User_passwords to support folder association
class User_passwords(db.Model):
    """user stored passwords model"""
    __tablename__='User_passwords'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    folder_id=db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    encrypted_password = db.Column(db.Text, nullable=False)
    website_name=db.Column(db.String(100),nullable=False )
    website_url=db.Column(db.String(500),nullable=False )
    username=db.Column(db.String(100),nullable=False )
    notes=db.Column(db.String(500),nullable=False )
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trashed = db.Column(db.Boolean, default=False)
    
    def encrypt_password(self,plain_password,master_password,user_salt):
        """Encrypt password using master passwrd and user salt"""
        # Convert salt from string to bytes
        salt_bytes=base64.b64decode(user_salt)
        # Derive encryption key from master passwd
        key=derive_key(master_password,salt_bytes)
        self.encrypted_password=encrypt_data(key,plain_password)

    def decrypt_password(self,master_password,user_salt):
        """"Decrupt password using m_pass & user salr"""
        salt_bytes=base64.b64decode(user_salt)        
        key=derive_key(master_password,salt_bytes)

        return decrypt_data(key, self.encrypted_password)

