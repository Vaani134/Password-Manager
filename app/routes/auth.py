from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, VaultItem
from .forms import RegisterForm, LoginForm, VaultForm
from .utils import check_password, encrypt_password, decrypt_password, generate_key
from . import db
import bcrypt
from datetime import timedelta

auth = Blueprint('auth', __name__)

# -------------------------
# SESSION TIMEOUT LOGIC
# -------------------------
@auth.before_app_request
def make_session_permanent():
    session.permanent = True
    session.modified = True  # ⏰ Resets timeout on user activity
    auth.current_app.permanent_session_lifetime = timedelta(minutes=10)


# -------------------------
# LOGIN ROUTE
# -------------------------
@auth.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password(form.password.data, user.password_hash):
            login_user(user)
            session.permanent = True
            return redirect(url_for('auth.dashboard'))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)


# -------------------------
# REGISTER ROUTE
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
# DASHBOARD (CREATE / READ)
# -------------------------
@auth.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = VaultForm()
    search = request.args.get('search', '').strip()

    # Filter items by current user
    items = VaultItem.query.filter_by(user_id=current_user.id)
    if search:
        items = items.filter(VaultItem.site.ilike(f'%{search}%'))

    items = items.all()

    if form.validate_on_submit():
        key = generate_key(current_user.email, form.master_password.data)
        encrypted_pw = encrypt_password(form.password.data, key)

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
# EDIT VAULT ENTRY
# -------------------------
@auth.route("/vault/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_vault_item(id):
    item = VaultItem.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash("Unauthorized action: You can't modify this entry.", "danger")
        return redirect(url_for("auth.dashboard"))

    form = VaultForm(obj=item)

    if form.validate_on_submit():
        key = generate_key(current_user.email, form.master_password.data)
        item.site = form.site.data
        item.username = form.username.data
        item.password = encrypt_password(form.password.data, key)

        db.session.commit()
        flash("Vault item updated successfully", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("edit_vault.html", form=form, item=item)


# -------------------------
# DELETE VAULT ENTRY
# -------------------------
@auth.route("/vault/<int:id>/delete", methods=["POST"])
@login_required
def delete_vault_item(id):
    item = VaultItem.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash("Unauthorized action: You can't delete this entry.", "danger")
        return redirect(url_for("auth.dashboard"))

    db.session.delete(item)
    db.session.commit()
    flash("Item deleted successfully", "info")
    return redirect(url_for("auth.dashboard"))


# -------------------------
# LOGOUT
# -------------------------
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully or session expired.", "info")
    return redirect(url_for("auth.login"))
