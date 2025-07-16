"""
from flask import Blueprint, request, jsonify, render_template

# Define the Blueprint as 'auth'
auth = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth.route('/signup', methods=['POST'])
def signup():
    return jsonify({'message': 'signup endpoint working'}), 200

@auth.route('/signin', methods=['POST'])
def signin():
    return jsonify({'message': 'signin endpoint working'}), 200
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db
from flask import request, redirect, url_for, flash
from app.models import SavedPassword  # ⬅️ assuming this model exists
from app import db
from flask_login import current_user

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.")
            return redirect(url_for('auth.signup'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please log in.")
        return redirect(url_for('auth.signin'))

    return render_template('signup.html')

@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('auth.dashboard'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('auth.signin'))

    return render_template('login.html')

@auth.route('/dashboard')
#@login_required
def dashboard():
    return render_template('dashboard.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.signin'))



@auth.route('/add-password', methods=['POST'])
@login_required
def add_password():
    website = request.form['website']
    username = request.form['username']
    password = request.form['password']

    new_entry = SavedPassword(
        user_id=current_user.id,
        website=website,
        username=username,
        password=password
    )
    db.session.add(new_entry)
    db.session.commit()
    flash('Password added successfully!')
    return redirect(url_for('auth.dashboard'))
