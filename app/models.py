#database scgema
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
    #get all passwords fr the user
    passwords = db.relationship('User_passwords', backref='owner', lazy=True)
    
class User_passwords(db.Model):
    """user stored passwords model"""
    __tablename__='User_passwords'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    encrypted_password = db.Column(db.Text, nullable=False)
    website_name=db.Column(db.String(100),nullable=False )
    website_url=db.Column(db.String(500),nullable=False )
    username=db.Column(db.String(100),nullable=False )
    notes=db.Column(db.String(500),nullable=False )
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

