from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os


db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()

    app = Flask(__name__)

   
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///../instance/password_manager.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key")

    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  

   
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Register vault blueprint
    from app.routes.vault_routes import vault_bp
    app.register_blueprint(vault_bp, url_prefix='/api/vault')

    # Register passwords blueprint
    # from app.routes.passwords import passwords_bp
    # app.register_blueprint(passwords_bp, url_prefix='/api/passwords')

   
    @app.route('/')
    def index():
        return render_template('index.html')

 
    with app.app_context():
        db.create_all()

    return app
