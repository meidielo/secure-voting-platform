import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret'),
        SQLALCHEMY_DATABASE_URI= os.environ.get('DATABASE_URL') 
            or ('sqlite:///' + os.path.join(app.instance_path, 'app.db')),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    # ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)
    login_manager.init_app(app)

    # import blueprints (auth and main routes already in repo)
    from app import auth, routes, dev_routes
    app.register_blueprint(auth.auth)
    app.register_blueprint(routes.main)
    app.register_blueprint(dev_routes.dev)

    # create database tables if they don't exist
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app
