#routes
from .auth import auth  # import the blueprint from auth.py

# Export the blueprint so it can be imported as:
# from app.routes import auth
__all__ = ['auth']
