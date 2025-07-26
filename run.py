from app import create_app
import os

app = create_app()

if __name__ == "__main__":
   
    debug_env = os.getenv('FLASK_ENV', 'development')
    debug_mode = debug_env == 'development' 

    port = int(os.getenv('PORT', 5000)) 

    app.run(
        debug=debug_mode,
        host="127.0.0.1",
        port=port
    )
