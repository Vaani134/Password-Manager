from flask import Flask , render_template
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app