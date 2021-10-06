from flask import Flask, Blueprint, session
from .extensions import db
from .views import main

def create_app(config_file='settings.py'):
    app = Flask(__name__)
    # postaviti kao tajnu ako je aplikacija u production mode-u (ENV i slicno)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/turizam'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config.from_pyfile(config_file)
    db.init_app(app)

    app.register_blueprint(main)

    return app