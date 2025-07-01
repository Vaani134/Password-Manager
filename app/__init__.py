from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from app.routes.auth import auth_bp
from dotenv import load_dotenv
import os

#initoalizing db
db=SQLAlchemy()

def create_app():
    #load env vars
    load_dotenv()

    app = Flask(__name__)
    
    #configd
    app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
                
    #intialize db with app
    db.init_app(app)

    app.register_blueprint(auth_bp)
    
    #route for frontend connection
    @app.route('/')
    def index():
        return render_template('index.html')
    
    #create database tables
    with app.app_context():
        db.create_all()
    
    return app