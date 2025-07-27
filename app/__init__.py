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

   
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///instance/password_manager.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key")

    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login_page'  # Fix: set to the correct endpoint
    
    @login_manager.unauthorized_handler
    def unauthorized():
        # Check if the request is for an API endpoint
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Authentication required'}), 401
        # For non-API endpoints, redirect to login
        return redirect(url_for('login_page'))

   
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

    @app.route('/test-import')
    def test_import():
        return render_template('test_import.html')

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
            print(f"[LOGIN] Attempting login for user: {username}")
            key = verify_user(username, password)
            if key:
                user = SimpleUser(username)
                login_user(user)
                session['username'] = username
                print(f"[LOGIN] Successfully logged in user: {username}")
                return redirect(url_for('dashboard'))
            else:
                print(f"[LOGIN] Failed login attempt for user: {username}")
                flash('Invalid username or password', 'error')
        return render_template('login.html')



    @app.route('/logout')
    def logout():
        username = session.get('username', 'Unknown')
        print(f"[LOGOUT] User {username} is logging out")
        logout_user()
        session.clear()
        print(f"[LOGOUT] Session cleared for user {username}")
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
        print(f"Adding favorite: {item} for user: {username}")
        if item:
            from app.services.sqlite.auth_handler import add_favorite
            add_favorite(username, item)
            print(f"Successfully added favorite: {item}")
        else:
            print("No item provided for favorite")
        # Always return JSON response for consistency
        return jsonify({'success': True, 'message': 'Added to favorites'})

    @app.route('/profile/favorite/remove', methods=['POST'])
    @login_required
    def remove_favorite_route():
        username = session.get('username', 'UserName')
        item = request.form.get('item')
        print(f"Removing favorite: {item} for user: {username}")
        if item:
            from app.services.sqlite.auth_handler import remove_favorite
            remove_favorite(username, item)
            print(f"Successfully removed favorite: {item}")
        else:
            print("No item provided for favorite removal")
        # Always return JSON response for consistency
        return jsonify({'success': True, 'message': 'Removed from favorites'})

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
        print(f"[API] Fetching passwords for user: {username}")
        try:
            with sqlite3.connect('instance/password_manager.db') as conn:
                rows = conn.execute("""
                    SELECT id, website, website_username, encrypted_password, notes, folder_id, website_url
                    FROM passwords WHERE username = ? AND trashed = 0
                """, (username,)).fetchall()
            passwords = []
            for row in rows:
                passwords.append({
                    'id': row[0],
                    'website': row[1],
                    'website_username': row[2],
                    'encrypted_password': row[3],
                    'notes': row[4],
                    'folder_id': row[5],
                    'website_url': row[6],
                })
            print(f"[API] Found {len(passwords)} passwords for user {username}")
            print(f"[API] Password details: {[(p['id'], p['website'], p['website_username']) for p in passwords]}")
            return {'passwords': passwords}
        except Exception as e:
            print(f"[API] Error fetching passwords for user {username}: {e}")
            return {'error': str(e)}, 500

    @app.route('/api/passwords', methods=['POST'])
    @login_required
    def add_password():
        username = session['username']
        data = request.json
        print(f"[ADD_PASSWORD] Received data: {data}")
        website = data.get('website_name') or data.get('website')  # Handle both field names
        website_username = data.get('username') or data.get('website_username')  # Handle both field names
        password = data.get('password')
        notes = data.get('notes')
        print(f"[ADD_PASSWORD] Processing for user {username}: website='{website}', username='{website_username}', password_length={len(password) if password else 0}, notes='{notes}'")
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
                    notes TEXT,
                    folder_id INTEGER,
                    trashed INTEGER DEFAULT 0,
                    website_url TEXT
                )
            """)
            # Add folder_id column if it doesn't exist
            try:
                conn.execute("ALTER TABLE passwords ADD COLUMN folder_id INTEGER")
            except:
                pass  # Column already exists
            # Add trashed column if it doesn't exist
            try:
                conn.execute("ALTER TABLE passwords ADD COLUMN trashed INTEGER DEFAULT 0")
            except:
                pass  # Column already exists
            # Add website_url column if it doesn't exist
            try:
                conn.execute("ALTER TABLE passwords ADD COLUMN website_url TEXT")
            except:
                pass  # Column already exists
            conn.execute("""
                INSERT INTO passwords (username, website, website_username, encrypted_password, notes, folder_id, website_url)
                VALUES (?, ?, ?, ?, ?, NULL, ?)
            """, (username, website, website_username, encrypted, notes, website))
            print(f"[ADD_PASSWORD] Successfully saved password for user {username}: website='{website}', username='{website_username}'")
        return {'success': True}

    @app.route('/api/passwords/<int:password_id>', methods=['PUT'])
    @login_required
    def edit_password(password_id):
        username = session['username']
        data = request.json
        website = data.get('website_name') or data.get('website')  # Handle both field names
        website_username = data.get('username') or data.get('website_username')  # Handle both field names
        password = data.get('password')
        notes = data.get('notes')
        key = derive_key(username, b'static_salt')
        encrypted = encrypt_data(key, password)
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("""
                UPDATE passwords SET website=?, website_username=?, encrypted_password=?, notes=?, website_url=?
                WHERE id=? AND username=?
            """, (website, website_username, encrypted, notes, website, password_id, username))
        return {'success': True}

    @app.route('/api/passwords/<int:password_id>', methods=['DELETE'])
    @login_required
    def delete_password(password_id):
        username = session['username']
        with sqlite3.connect('instance/password_manager.db') as conn:
            conn.execute("DELETE FROM passwords WHERE id=? AND username=?", (password_id, username))
        return {'success': True}

    @app.route('/api/passwords/delete_all', methods=['POST'])
    @login_required
    def delete_all_passwords():
        username = session['username']
        print(f"🗑️ Delete all passwords called for user: {username}")
        try:
            with sqlite3.connect('instance/password_manager.db') as conn:
                # First, let's see how many passwords exist
                count = conn.execute("SELECT COUNT(*) FROM passwords WHERE username = ?", (username,)).fetchone()[0]
                print(f"🗑️ Found {count} passwords to delete")
                
                # Delete all passwords
                conn.execute("DELETE FROM passwords WHERE username = ?", (username,))
                
                # Verify deletion
                count_after = conn.execute("SELECT COUNT(*) FROM passwords WHERE username = ?", (username,)).fetchone()[0]
                print(f"🗑️ After deletion: {count_after} passwords remaining")
                
            return jsonify({'success': True, 'deleted_count': count})
        except Exception as e:
            print(f"🗑️ Error deleting all passwords: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/passwords/grouped', methods=['GET'])
    @login_required
    def get_passwords_grouped():
        username = session['username']
        print(f"[GROUPED] Fetching grouped passwords for user: {username}")
        with sqlite3.connect('instance/password_manager.db') as conn:
            # Create folders table if it doesn't exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL
                )
            """)
            
            # Fetch folders
            try:
                folders = conn.execute("SELECT id, name FROM folders WHERE username = ?", (username,)).fetchall()
            except:
                folders = []
                
            # Add website_url column if it doesn't exist
            try:
                conn.execute("ALTER TABLE passwords ADD COLUMN website_url TEXT")
            except:
                pass  # Column already exists
                
            # Fetch passwords with folder_id (excluding trashed)
            rows = conn.execute("""
                SELECT id, website, website_username, encrypted_password, notes, folder_id, website_url
                FROM passwords WHERE username = ? AND trashed = 0
            """, (username,)).fetchall()
        # Group passwords by folder_id
        folder_map = {f[0]: {'id': f[0], 'name': f[1], 'passwords': []} for f in folders}
        folder_map[None] = {'id': None, 'name': '', 'passwords': []}
        for row in rows:
            pw = {
                'id': row[0],
                'website': row[1],
                'website_username': row[2],
                'encrypted_password': row[3],
                'notes': row[4],
                'folder_id': row[5],
                'website_url': row[6] if len(row) > 6 else None,
            }
            folder_map.get(row[5], folder_map[None])['passwords'].append(pw)
        
        result = list(folder_map.values())
        print(f"[GROUPED] Returning {len(result)} folders with {sum(len(f['passwords']) for f in result)} total passwords")
        for folder in result:
            print(f"[GROUPED] Folder '{folder['name']}' has {len(folder['passwords'])} passwords")
        return jsonify({'folders': result})

    @app.route('/api/passwords/<int:password_id>/folder', methods=['PUT'])
    @login_required
    def set_password_folder(password_id):
        username = session['username']
        data = request.json
        folder_id = data.get('folder_id')
        print(f"[API] Moving password {password_id} to folder {folder_id} for user {username}")
        try:
            with sqlite3.connect('instance/password_manager.db') as conn:
                # Check if password exists and belongs to user
                cursor = conn.execute("SELECT id FROM passwords WHERE id = ? AND username = ?", (password_id, username))
                if not cursor.fetchone():
                    print(f"[API] Password {password_id} not found for user {username}")
                    return jsonify({'error': 'Password not found'}), 404
                
                # Update the password's folder
                conn.execute("UPDATE passwords SET folder_id = ? WHERE id = ? AND username = ?", (folder_id, password_id, username))
                print(f"[API] Successfully moved password {password_id} to folder {folder_id}")
            return jsonify({'success': True})
        except Exception as e:
            print(f"[API] Error moving password {password_id} to folder {folder_id}: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/download', methods=['POST'])
    @login_required
    def log_download_route():
        username = session.get('username')
        if not username:
            print("Download attempt: User not logged in")
            return jsonify({'error': 'Not logged in'}), 401
        filename = request.json.get('filename')
        print(f"Download attempt: {filename} for user: {username}")
        if not filename:
            print("Download attempt: No filename provided")
            return jsonify({'error': 'Filename required'}), 400
        from app.services.sqlite.auth_handler import log_download
        log_download(username, filename)
        print(f"Successfully logged download: {filename}")
        return jsonify({'message': 'Download logged successfully'}), 200

    @app.route('/api/folders', methods=['GET'])
    @login_required
    def list_folders():
        username = session.get('username')
        print(f"[API] Fetching folders for user: {username}")
        try:
            with sqlite3.connect('instance/password_manager.db') as conn:
                # Create folders table if it doesn't exist
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS folders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        username TEXT NOT NULL
                    )
                """)
                rows = conn.execute("SELECT id, name FROM folders WHERE username = ?", (username,)).fetchall()
            folders = [{'id': row[0], 'name': row[1]} for row in rows]
            print(f"[API] Found {len(folders)} folders for user {username}")
            return jsonify({'folders': folders})
        except Exception as e:
            print(f"[API] Error fetching folders for user {username}: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/folders', methods=['POST'])
    @login_required
    def create_folder():
        username = session.get('username')
        data = request.json
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Folder name required'}), 400
        with sqlite3.connect('instance/password_manager.db') as conn:
            # Create folders table if it doesn't exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL
                )
            """)
            cursor = conn.execute("INSERT INTO folders (name, username) VALUES (?, ?)", (name, username))
            folder_id = cursor.lastrowid
        return jsonify({'folder': {'id': folder_id, 'name': name}})

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
            conn.execute("UPDATE passwords SET folder_id = NULL WHERE folder_id = ?", (folder_id,))
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

    @app.route('/api/passwords/<int:password_id>/reveal', methods=['GET'])
    @login_required
    def reveal_password(password_id):
        username = session['username']
        with sqlite3.connect('instance/password_manager.db') as conn:
            row = conn.execute("SELECT encrypted_password FROM passwords WHERE id=? AND username=?", (password_id, username)).fetchone()
            if not row:
                return jsonify({'error': 'Password not found'}), 404
            encrypted_password = row[0]
            # For demo, use username as key; in production, use a real master key
            key = derive_key(username, b'static_salt')
            from app.services.encryption import decrypt_data
            try:
                password = decrypt_data(key, encrypted_password)
            except Exception as e:
                return jsonify({'error': 'Failed to decrypt password', 'details': str(e)}), 500
        return jsonify({'password': password})

    @app.route('/api/passwords/analyze', methods=['GET'])
    @login_required
    def analyze_passwords():
        username = session['username']
        with sqlite3.connect('instance/password_manager.db') as conn:
            rows = conn.execute("""
                SELECT id, website, website_username, encrypted_password, notes
                FROM passwords WHERE username = ? AND trashed = 0
            """, (username,)).fetchall()
        
        # For demo, use username as key; in production, use a real master key
        key = derive_key(username, b'static_salt')
        from app.services.encryption import decrypt_data
        
        passwords = []
        for row in rows:
            try:
                decrypted_password = decrypt_data(key, row[3])
                passwords.append({
                    'id': row[0],
                    'website': row[1],
                    'username': row[2],
                    'password': decrypted_password,
                    'notes': row[4]
                })
            except Exception as e:
                # Skip passwords that can't be decrypted
                continue
        
        # Analyze passwords
        weak_count = 0
        reused_count = 0
        total_count = len(passwords)
        seen_passwords = {}
        analysis_results = []
        
        for pw in passwords:
            status = []
            
            # Check password strength
            if len(pw['password']) < 8:
                status.append('Too short')
            if not any(c.isdigit() for c in pw['password']):
                status.append('No number')
            if not any(c.isupper() for c in pw['password']):
                status.append('No uppercase')
            if not any(c.islower() for c in pw['password']):
                status.append('No lowercase')
            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in pw['password']):
                status.append('No symbol')
            
            # Check for reused passwords
            if pw['password'] in seen_passwords:
                status.append('Reused')
                reused_count += 1
            seen_passwords[pw['password']] = True
            
            if status:
                weak_count += 1
            
            analysis_results.append({
                'id': pw['id'],
                'website': pw['website'],
                'username': pw['username'],
                'password': pw['password'],
                'status': status if status else ['Strong']
            })
        
        return jsonify({
            'total': total_count,
            'weak': weak_count,
            'reused': reused_count,
            'results': analysis_results
        })

 
    # with app.app_context():
    #     db.create_all()

    return app
