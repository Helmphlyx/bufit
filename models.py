from database import db
from flask_login import UserMixin, current_user
from functools import wraps
from flask import url_for, redirect

ACCESS = {"user": 0, "superuser": 1, "admin": 2}


class User(UserMixin, db.Model):
    """Users table."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    # User Authentication fields
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    # Role access
    access = db.Column(db.Integer, default=0)

    def role_access(self):
        return self.access

    def allowed(self, access_level):
        return self.access >= access_level


def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if not current_user.email:
                return redirect(url_for("users.login"))

            elif not current_user.allowed(access_level):
                return redirect(url_for("main.home"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
