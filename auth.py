import datetime

from flask import Blueprint, abort
from flask import render_template, request, url_for, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, requires_access_level, ACCESS
from database import db
from flask_login import login_user, logout_user, login_required

auth = Blueprint("auth", __name__)


# Login Routes
@auth.route("/")
def login():
    """Landing / Login page."""
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    """Handle user login."""
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Email is not registered. Please sign up for an account.")
        return redirect(url_for("auth.login"))
    elif not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        return redirect(url_for("auth.login"))
    elif user.is_confirmed is False:
        flash("User account is not confirmed. Please check your email.")
        return redirect(url_for("auth.login"))
    login_user(user, remember=True)
    return redirect(url_for("main.home"))


@auth.route("/signup")
def signup():
    """User signup page."""
    return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
    """Handle user signup."""
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    password_check = request.form.get("password_check")

    email_user = User.query.filter_by(email=email).first()
    name_user = User.query.filter_by(name=name).first()

    if not email:
        flash("An email address must be provided")
        return redirect(url_for("auth.signup"))
    if not name:
        flash("A username must be provided")
        return redirect(url_for("auth.signup"))
    if not password:
        flash("A password must be provided")
        return redirect(url_for("auth.signup"))
    if password != password_check:
        flash("Passwords do not match! Please try again")
        return redirect(url_for("auth.signup"))
    if email_user:
        flash("Email address already exists! Please login.")
        return redirect(url_for("auth.signup"))
    if name_user:
        flash("Username already taken!")
        return redirect(url_for("auth.signup"))

    new_user = User(
        email=email,
        name=name,
        password=generate_password_hash(password, method="sha256"),
    )

    # Now we'll send the email confirmation link
    from utils import ts, send_email

    subject = "Confirm your email"
    token = ts.dumps(email, salt="email-confirm-key")

    confirm_url = url_for("auth.confirm_email", token=token, _external=True)

    html = render_template(
        "email_confirmation.html", confirm_url=confirm_url, name=name
    )

    send_email([new_user.email], subject, html)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))


@auth.route("/logout")
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have successfully logged yourself out.")
    return redirect(url_for("auth.login"))


@auth.route("/confirm/<token>")
def confirm_email(token):
    from utils import ts

    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except Exception as e:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()
    user.is_confirmed = True
    user.confirmed_on = datetime.datetime.now()

    db.session.add(user)
    db.session.commit()

    return redirect(url_for("auth.login"))


@auth.route("/forgot_password")
def forgot_password():
    """Forgeot password page."""
    return render_template("forgot_password.html")


@auth.route("/forgot_password", methods=["POST"])
def forgot_password_post():
    """Handles forgotten password request."""
    email = request.form.get("email")

    if not email:
        flash("An email address must be provided")
        return redirect(url_for("auth.forgot_password"))

    # Now we'll send the email confirmation link
    from utils import ts, send_email

    subject = "Reset Password"
    token = ts.dumps(email, salt="email-confirm-key")

    confirm_url = url_for("auth.reset_password", token=token, _external=True)

    html = render_template(
        "password_reset.html",
        confirm_url=confirm_url,
    )

    send_email([email], subject, html)

    return redirect(url_for("auth.login"))


@auth.route("/reset_password/<token>", methods=["POST", "GET"])
def reset_password(token):
    from utils import ts

    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except Exception as e:
        abort(404)

    if request.method == "POST":
        password = request.form.get("password")
        password_check = request.form.get("password_check")

        if not password:
            flash("A new password must be provided")
            token = ts.dumps(email, salt="email-confirm-key")
            return redirect(url_for("auth.reset_password", token=token))
        if not password_check:
            flash("A password check must be provided")
            token = ts.dumps(email, salt="email-confirm-key")
            return redirect(url_for("auth.reset_password", token=token))
        if password != password_check:
            flash("Passwords do not match! Please try again")
            token = ts.dumps(email, salt="email-confirm-key")
            return redirect(url_for("auth.reset_password", token=token))

        user = User.query.filter_by(email=email).first_or_404()
        user.password = generate_password_hash(password)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    return render_template("reset_password.html", token=token)


@auth.route("/create_user")
@login_required
@requires_access_level(ACCESS["admin"])
def create_user():
    """Create user page."""
    return render_template("create_user.html")


@auth.route("/create_user", methods=["POST"])
@login_required
@requires_access_level(ACCESS["admin"])
def create_user_post():
    """Handle creating user page."""
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    coach_toggle = request.form.get("coach_toggle")

    email_user = User.query.filter_by(email=email).first()
    name_user = User.query.filter_by(name=name).first()

    if not email:
        flash("An email address must be provided")
        return redirect(url_for("auth.create_user"))
    if not name:
        flash("A username must be provided")
        return redirect(url_for("auth.create_user"))
    if not password:
        flash("A password must be provided")
        return redirect(url_for("auth.create_user"))
    if email_user:
        flash("Email address already exists")
        return redirect(url_for("auth.create_user"))
    if name_user:
        flash("Username already taken")
        return redirect(url_for("auth.create_user"))

    new_user = User(
        email=email,
        name=name,
        password=generate_password_hash(password, method="sha256"),
        access=1 if coach_toggle else 0,
    )

    # Now we'll send the email confirmation link
    from utils import ts, send_email

    subject = "Confirm your email"
    token = ts.dumps(email, salt="email-confirm-key")

    confirm_url = url_for("auth.confirm_email", token=token, _external=True)

    html = render_template(
        "email_confirmation_from_admin.html",
        confirm_url=confirm_url,
        name=name,
        password=password,
    )

    send_email([new_user.email], subject, html)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("main.home"))
