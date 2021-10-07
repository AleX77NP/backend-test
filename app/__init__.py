from flask import Flask, Blueprint, session
from .extensions import db,ma, bcrypt, migrate, mail
from .views import main

def create_app(config_file='settings.py'):
    app = Flask(__name__)
    # postaviti kao tajnu ako je aplikacija u production mode-u (ENV i slicno)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/turizam'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = '' # dummy mail, sakriti u prod
    app.config['MAIL_PASSWORD'] = '' # sakriti u prod
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    app.config.from_pyfile(config_file)
    db.init_app(app)
    ma.init_app(app)
    mail.init_app(app)

    bcrypt.init_app(app)

    migrate.init_app(app, db)

    app.register_blueprint(main)

    return app