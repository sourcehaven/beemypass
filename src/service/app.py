import os

from flask import Flask
from flask_jwt_extended import JWTManager

from service.db import db, migrate
from service.models.seri import ModelPlusJSONProvider
from service.mw import register_error_handlers, register_blueprints, check_if_token_in_blacklist
from service import config


def create_app():
    app = Flask(__name__)
    app.config.from_object(getattr(config, f'{config.getenv("FLASK_ENV", "")}Config'))
    app.json = ModelPlusJSONProvider(app)

    register_blueprints(app)
    register_error_handlers(app)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    jwt = JWTManager(app)
    jwt.token_in_blocklist_loader(check_if_token_in_blacklist)
    if config.getenv('MYPASS_TESTENV'):
        from ._dummy import init_db
        with app.app_context():
            init_db(db)

    return app
