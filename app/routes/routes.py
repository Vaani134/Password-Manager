from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, VaultItem
from .forms import RegisterForm, LoginForm, VaultForm
from .utils import check_password, encrypt_password, decrypt_password, generate_key
from . import db
import bcrypt

auth = Blueprint('auth', __name__)

# -------------------------
# Login Route
# -------------------------
@auth.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password(form.password.data, user.password_hash):
            login_user(user)
            return redirect(url_for('auth.dashboard'))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

# -------------------------
# Registration Route
# -------------------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered", "warning")
            return redirect(url_for("auth.register"))

        hashed = bcrypt.hashpw(form.password.data.encode(), bcrypt.gensalt())
        user = User(email=form.email.data, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

# -------------------------
# Dashboard / Vault Route
# -------------------------
@auth.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = VaultForm()
    search = request.args.get('search')

    # Filter items by user
    items = VaultItem.query.filter_by(user_id=current_user.id)

    # Apply search filter
    if search:
        items = items.filter(VaultItem.site.ilike(f'%{search}%'))

    items = items.all()

    if form.validate_on_submit():
        # Generate encryption key
        key = generate_key(current_user.email, form.master_password.data)

        # Encrypt the password
        encrypted_pw = encrypt_password(form.password.data, key)

        # Save to database
        item = VaultItem(
            site=form.site.data,
            username=form.username.data,
            password=encrypted_pw,
            user_id=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash("Password saved successfully", "success")
        return redirect(url_for('auth.dashboard'))

    return render_template("dashboard.html", form=form, items=items)

# -------------------------
# Logout
# -------------------------
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for("auth.login"))
