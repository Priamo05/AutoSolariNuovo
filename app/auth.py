from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import db
from .forms import LoginForm, RegisterForm
from .models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("Email già registrata.", "danger")
            return render_template("register.html", form=form)

        user = User(
            full_name=form.full_name.data,
            email=form.email.data.lower(),
            role="user",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registrazione completata.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("Credenziali non valide.", "danger")
    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout eseguito.", "info")
    return redirect(url_for("auth.login"))
