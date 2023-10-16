from flask import Flask

from service.api import AuthApi, VaultApi, TeapotApi, UserApi


def register_blueprints(app: Flask):
    app.register_blueprint(AuthApi)
    app.register_blueprint(UserApi)
    app.register_blueprint(TeapotApi)
    app.register_blueprint(VaultApi)
