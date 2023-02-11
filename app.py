from flask import Flask
from flask_login import LoginManager
from models import User
from database import db, init_db

global_user = None


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "SOME_SECRET_KEY_VALUE"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///database.db"
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
        db.create_all()
        db.session.commit()
        # init_db()

    return app


app = create_app()
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
