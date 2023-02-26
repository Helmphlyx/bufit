import logging

from flask import Flask
from flask_login import LoginManager
from database import db, init_db
from sqlalchemy_utils import database_exists
from settings import settings
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail

global_user = None


def create_admin():
    admin_user = User(
        email="bufitsite@gmail.com",
        name="admin",
        password=generate_password_hash("Bufitcs633", method="sha256"),
        access=2,
        is_confirmed=True,
    )
    db.session.add(admin_user)
    db.session.commit()


def create_app():
    """Configurations for our Flask web-app."""

    if settings.MYSQL_CREDENTIALS["NAME"]:
        SQLALCHEMY_DATABASE_URI = f"mysql://{settings.MYSQL_CREDENTIALS['USERNAME']}:{settings.MYSQL_CREDENTIALS['PASSWORD']}@host:{settings.MYSQL_CREDENTIALS['PORT']}/{settings.MYSQL_CREDENTIALS['NAME']}"
        SQLALCHEMY_DATABASE_URI_LONG = f"sqlite:///{settings.DATABASE_NAME}"
        logging.warning("BuFit web app configured with MYSQL db.")
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{settings.DATABASE_SHORT_NAME}"
        SQLALCHEMY_DATABASE_URI_LONG = f"sqlite:///{settings.DATABASE_NAME}"
        logging.warning("BuFit web app configured with SQLITE db.")

    app = Flask(__name__)
    app.config[
        "SECRET_KEY"
    ] = "SOME_SECRET_KEY_VALUE"  # TODO: update secret value
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["UPLOAD_FOLDER"] = "static/images/"
    app.url_map.strict_slashes = False

    mail_settings = {
        "MAIL_SERVER": "smtp.gmail.com",
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": "bufitsite@gmail.com",
        "MAIL_PASSWORD": "zsofxopzkulwrqnb",
    }
    app.config.update(mail_settings)

    db.init_app(app)

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    with app.app_context():
        if not database_exists(SQLALCHEMY_DATABASE_URI_LONG):
            db.create_all()
            init_db()
            create_admin()
    return app


app = create_app()
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

application = app


@login_manager.user_loader
def load_user(user_id):
    """Defines function to load users."""
    return User.query.get(int(user_id))


if __name__ == '__main__':
    application.run()
