from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, logout_user
from dotenv import load_dotenv
import os
import sqlite3
from app.services.sqlite.auth_handler import (
    register_user, verify_user,
    get_favorites, get_downloads, get_user_setting, get_history
)
from app.services.encryption import derive_key, encrypt_data


db = SQLAlchemy()
login_manager = LoginManager()

class SimpleUser(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username
    def get_id(self):
        return self.id

def create_app():
    load_dotenv()

    app = Flask(__name__)

   
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///../instance/password_manager.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key")

    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login_page'  # Fix: set to the correct endpoint

   
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return SimpleUser(user_id)

    
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Register vault blueprint
    from app.routes.vault_routes import vault_bp
    app.register_blueprint(vault_bp, url_prefix='/api/vault')

    # Register passwords blueprint
    # from app.routes.passwords import passwords_bp
    # app.register_blueprint(passwords_bp, url_prefix='/api/passwords')

   
    @app.route('/')
    def intro():
        return render_template('intro.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup_page():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')  # Not used in sqlite handler, but could be stored elsewhere
            password = request.form.get('password')
            if not username or not password:
                flash('Please fill in all required fields.', 'error')
                return render_template('signup.html')
            success = register_user(username, password)
            if success:
                flash('You have successfully registered! Please log in.', 'success')
                return redirect(url_for('login_page'))
            else:
                flash('Account already registered. Please log in.', 'error')
                return render_template('signup.html')
        return render_template('signup.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login_page():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            key = verify_user(username, password)
            if key:
                user = SimpleUser(username)
                login_user(user)
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        return render_template('login.html')

    @app.route('/forgot', methods=['GET', 'POST'])
    def forgot_page():
        return render_template('forgot.html')

    @app.route('/logout')
    def logout():
        logout_user()
        session.clear()
        return redirect(url_for('login_page'))

    from flask_login import login_required
    @app.route('/dashboard')
    @login_required
    def dashboard():
        username = session.get('username', 'UserName')
        # Placeholder: fetch name and photo_url from DB
        name = username  # Replace with actual name from DB
        photo_url = None # Replace with actual photo URL from DB
        return render_template('dashboard.html', name=name, photo_url=photo_url)

    @app.route('/profile')
    @login_required
    def profile():
        username = session.get('username', 'UserName')
        favorites = get_favorites(username)
        downloads = get_downloads(username)
        location, language = get_user_setting(username)
        history = get_history(username)
        return render_template(
            'profile.html',
            username=username,
            favorites=favorites,
            downloads=downloads,
            location=location,
            language=language,
            history=history
        )

    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        username = session.get('username', 'UserName')
        # Placeholder: fetch current name and photo_url from DB
        name = username  # Replace with actual name from DB
        photo_url = None # Replace with actual photo URL from DB
        if request.method == 'POST':
            # Handle photo upload
            photo = request.files.get('photo')
            if photo and photo.filename:
                # Save photo and update photo_url (implement actual storage logic)
                photo_url = '/static/images/' + photo.filename
                photo.save('app/static/images/' + photo.filename)
            # Handle name change
            new_name = request.form.get('name')
            if new_name:
                name = new_name
                # Update name in DB (implement actual DB update)
            # Handle password change
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            if new_password:
                if new_password == confirm_password:
                    # Verify current password and update to new password (implement logic)
                    pass
                else:
                    flash('New passwords do not match', 'error')
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
        return render_template('profile_edit.html', name=name, photo_url=photo_url)

    @app.route('/profile/favorite/add', methods=['POST'])
    @login_required
    def add_favorite_route():
        username = session.get('username', 'UserName')
        item = request.form.get('item')
        if item:
            from app.services.sqlite.auth_handler import add_favorite
            add_favorite(username, item)
        return redirect(url_for('profile'))

    @app.route('/profile/favorite/remove', methods=['POST'])
    @login_required
    def remove_favorite_route():
        username = session.get('username', 'UserName')
        item = request.form.get('item')
        if item:
            from app.services.sqlite.auth_handler import remove_favorite
            remove_favorite(username, item)
        return redirect(url_for('profile'))

    @app.route('/profile/location', methods=['POST'])
    @login_required
    def set_location_route():
        username = session.get('username', 'UserName')
        location = request.form.get('location')
        if location:
            from app.services.sqlite.auth_handler import set_user_setting
            set_user_setting(username, location=location)
        return redirect(url_for('profile'))

    @app.route('/profile/language', methods=['POST'])
    @login_required
    def set_language_route():
        username = session.get('username', 'UserName')
        language = request.form.get('language')
        if language:
            from app.services.sqlite.auth_handler import set_user_setting
            set_user_setting(username, language=language)
        return redirect(url_for('profile'))

    @app.route('/profile/download/remove', methods=['POST'])
    @login_required
    def remove_download_route():
        username = session.get('username')
        filename = request.form.get('filename')
        if filename:
            from app.services.sqlite.auth_handler import remove_download
            remove_download(username, filename)
        return redirect(url_for('profile'))

    @app.route('/api/passwords', methods=['GET'])
    @login_required
    def get_passwords():
        username = session['username']
        with sqlite3.connect('instance/password_manager.db') as conn:
            rows = conn.execute("""
                SELECT id, website, website_username, encrypted_password, notes
                FROM passwords WHERE username = ?
            """, (username,)).fetchall()
        passwords = []
        for row in rows:
            passwords.append({
                'id': row[0],
                'website': row[1],
                'website_username': row[2],
                'encrypted_password': row[3],
                'notes': row[4],
            })
        return {'passwords': passwords}

    @app.route('/api/passwords', methods=['POST'])
    @login_required
    def add_password():
        username = session['username']
        data = request.json
        website = data.get('website')
        website_username = data.get('website_username')
        password = data.get('password')
        notes = data.get('notes')
        # For demo, use username as key; in production, use a real master key
        key = derive_key(username, b'static_salt')
        encrypted = encrypt_data(key, password)
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    website TEXT,
                    website_username TEXT,
                    encrypted_password TEXT,
                    notes TEXT
                )
            """)
            conn.execute("""
                INSERT INTO passwords (username, website, website_username, encrypted_password, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (username, website, website_username, encrypted, notes))
        return {'success': True}

    @app.route('/api/passwords/<int:password_id>', methods=['PUT'])
    @login_required
    def edit_password(password_id):
        username = session['username']
        data = request.json
        website = data.get('website')
        website_username = data.get('website_username')
        password = data.get('password')
        notes = data.get('notes')
        key = derive_key(username, b'static_salt')
        encrypted = encrypt_data(key, password)
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("""
                UPDATE passwords SET website=?, website_username=?, encrypted_password=?, notes=?
                WHERE id=? AND username=?
            """, (website, website_username, encrypted, notes, password_id, username))
        return {'success': True}

    @app.route('/api/passwords/<int:password_id>', methods=['DELETE'])
    @login_required
    def delete_password(password_id):
        username = session['username']
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("DELETE FROM passwords WHERE id=? AND username=?", (password_id, username))
        return {'success': True}

    @app.route('/api/passwords/grouped', methods=['GET'])
    @login_required
    def get_passwords_grouped():
        username = session['username']
        with sqlite3.connect('instance/password_manager.db') as conn:
            # Fetch folders
            folders = conn.execute("SELECT id, name FROM folders WHERE username = ?", (username,)).fetchall()
            # Fetch passwords with folder_id
            rows = conn.execute("""
                SELECT id, website, website_username, encrypted_password, notes, folder_id
                FROM passwords WHERE username = ?
            """, (username,)).fetchall()
        # Group passwords by folder_id
        folder_map = {f[0]: {'id': f[0], 'name': f[1], 'passwords': []} for f in folders}
        folder_map[None] = {'id': None, 'name': 'Uncategorized', 'passwords': []}
        for row in rows:
            pw = {
                'id': row[0],
                'website': row[1],
                'website_username': row[2],
                'encrypted_password': row[3],
                'notes': row[4],
                'folder_id': row[5],
            }
            folder_map.get(row[5], folder_map[None])['passwords'].append(pw)
        return jsonify({'folders': list(folder_map.values())})

    @app.route('/api/passwords/<int:password_id>/folder', methods=['PUT'])
    @login_required
    def set_password_folder(password_id):
        username = session['username']
        data = request.json
        folder_id = data.get('folder_id')
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("UPDATE passwords SET folder_id = ? WHERE id = ? AND username = ?", (folder_id, password_id, username))
        return jsonify({'success': True})

    @app.route('/api/download', methods=['POST'])
    @login_required
    def log_download_route():
        username = session.get('username')
        if not username:
            return jsonify({'error': 'Not logged in'}), 401
        filename = request.json.get('filename')
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        from app.services.sqlite.auth_handler import log_download
        log_download(username, filename)
        return jsonify({'message': 'Download logged successfully'}), 200

    @app.route('/api/folders', methods=['GET'])
    @login_required
    def list_folders():
        username = session.get('username')
        with sqlite3.connect('instance/password_manager.db') as conn:
            rows = conn.execute("SELECT id, name FROM folders WHERE username = ?", (username,)).fetchall()
        folders = [{'id': row[0], 'name': row[1]} for row in rows]
        return jsonify({'folders': folders})

    @app.route('/api/folders', methods=['POST'])
    @login_required
    def create_folder():
        username = session.get('username')
        data = request.json
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Folder name required'}), 400
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("INSERT INTO folders (name, username) VALUES (?, ?)", (name, username))
        return jsonify({'success': True})

    @app.route('/api/folders/<int:folder_id>', methods=['PUT'])
    @login_required
    def rename_folder(folder_id):
        username = session.get('username')
        data = request.json
        new_name = data.get('name')
        if not new_name:
            return jsonify({'error': 'New folder name required'}), 400
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("UPDATE folders SET name = ? WHERE id = ? AND username = ?", (new_name, folder_id, username))
        return jsonify({'success': True})

    @app.route('/api/folders/<int:folder_id>', methods=['DELETE'])
    @login_required
    def delete_folder(folder_id):
        username = session.get('username')
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("DELETE FROM folders WHERE id = ? AND username = ?", (folder_id, username))
            conn.execute("UPDATE User_passwords SET folder_id = NULL WHERE folder_id = ?", (folder_id,))
        return jsonify({'success': True})

    @app.route('/api/passwords/<int:password_id>/trash', methods=['PUT'])
    @login_required
    def move_password_to_trash(password_id):
        username = session['username']
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("UPDATE passwords SET trashed = 1 WHERE id = ? AND username = ?", (password_id, username))
        return jsonify({'success': True})

    @app.route('/api/passwords/trashed', methods=['GET'])
    @login_required
    def list_trashed_passwords():
        username = session['username']
        with sqlite3.connect('instance/password_manager.db') as conn:
            rows = conn.execute("SELECT id, website, website_username, encrypted_password, notes FROM passwords WHERE username = ? AND trashed = 1", (username,)).fetchall()
        passwords = [
            {'id': row[0], 'website': row[1], 'website_username': row[2], 'encrypted_password': row[3], 'notes': row[4]}
            for row in rows
        ]
        return jsonify({'passwords': passwords})

    @app.route('/api/passwords/<int:password_id>/restore', methods=['PUT'])
    @login_required
    def restore_password(password_id):
        username = session['username']
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("UPDATE passwords SET trashed = 0 WHERE id = ? AND username = ?", (password_id, username))
        return jsonify({'success': True})

    @app.route('/api/passwords/<int:password_id>/delete', methods=['DELETE'])
    @login_required
    def permanently_delete_password(password_id):
        username = session['username']
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("DELETE FROM passwords WHERE id = ? AND username = ?", (password_id, username))
        return jsonify({'success': True})

 
    # with app.app_context():
    #     db.create_all()

    return app
