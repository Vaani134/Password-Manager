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
    
    