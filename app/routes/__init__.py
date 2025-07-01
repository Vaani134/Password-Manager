from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, VaultItem
from .forms import RegisterForm, LoginForm, VaultForm
from .utils import check_password, encrypt_password, generate_key
from . import db
import bcrypt

auth = Blueprint('auth', __name__)

@auth.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password(form.password.data, user.password_hash):
            login_user(user)
            return redirect(url_for('auth.dashboard'))
        flash("Invalid credentials")
    return render_template("login.html", form=form)

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = bcrypt.hashpw(form.password.data.encode(), bcrypt.gensalt())
        user = User(email=form.email.data, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@auth.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = VaultForm()
    # Handle storing passwords
    return render_template("dashboard.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("auth.login"))
#routes
