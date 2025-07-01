from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():
   
    load_dotenv()

    app = Flask(__name__)

   
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///../instance/password_manager.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key")

  
    db.init_app(app)

   
    from app.routes.routes import auth
    app.register_blueprint(auth)

    @app.route('/')
    def index():
        return render_template("index.html")

    return app


