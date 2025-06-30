from app import create_app
import os

app= create_app()

if __name__=="__main__":
    debug_mode =os.getenv('FLASK_ENV')
    port= int(os.getenv('PORT'))

    app.run(
        debug=debug_mode,
        host="127.0.0.1",
        port=port
    )