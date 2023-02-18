from flask import Flask
from flask_login import LoginManager
from models import User
from database import db, init_db
from sqlalchemy_utils import database_exists
from settings import settings

global_user = None


def create_app():
    """Configurations for our Flask web-app."""
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{settings.DATABASE_SHORT_NAME}"
    SQLALCHEMY_DATABASE_URI_LONG = f"sqlite:///{settings.DATABASE_NAME}"

    app = Flask(__name__)
    app.config[
        "SECRET_KEY"
    ] = "SOME_SECRET_KEY_VALUE"  # TODO: update secret value
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["UPLOAD_FOLDER"] = "static/images/"
    app.url_map.strict_slashes = False

    db.init_app(app)

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from models import User

    with app.app_context():
        if not database_exists(SQLALCHEMY_DATABASE_URI_LONG):
            db.create_all()
            init_db()
    return app


app = create_app()
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    """Defines function to load users."""
    return User.query.get(int(user_id))
