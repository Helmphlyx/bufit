from flask import Blueprint
from flask import render_template, request, url_for, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from database import db
from flask_login import login_user, logout_user

auth = Blueprint("auth", __name__)


# Login Routes
@auth.route("/")
def login():
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Email is not registered. Please sign up for an account.")
        return redirect(url_for("auth.login"))
    elif not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        return redirect(url_for("auth.login"))

    login_user(user, remember=remember)
    return redirect(url_for("main.home"))


@auth.route("/signup")
def signup():
    return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not email:
        flash("An email address must be provided")
        return redirect(url_for("auth.signup"))
    if not name:
        flash("A username must be provided")
        return redirect(url_for("auth.signup"))
    if not password:
        flash("A password must be provided")
        return redirect(url_for("auth.signup"))
    if user:
        flash("Email address already exists")
        return redirect(url_for("auth.signup"))

    new_user = User(
        email=email,
        name=name,
        password=generate_password_hash(password, method="sha256"),
    )
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))


@auth.route("/logout")
def logout():
    logout_user()
    flash("You have successfully logged yourself out.")
    return redirect(url_for("auth.login"))
