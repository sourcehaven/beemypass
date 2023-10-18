import datetime
import os

import json5
from loguru import logger

basedir = os.path.abspath(os.path.dirname(__file__))

# See https://auth0.com/blog/brute-forcing-hs256-is-possible-the-importance-of-using-strong-keys-to-sign-jwts/
secret_key = 'sourcehaven'  # TODO: change this to a strong secret key eg.: secrets.token_urlsafe(32)
access_expires_delta = datetime.timedelta(minutes=10)
refresh_expires_delta = datetime.timedelta(days=30)
host = '0.0.0.0'
port = 5757


try:
    import mypass
    with open(mypass.current_app.paths.app / 'mypass.config.json5', 'r') as fp:
        environ: dict = json5.load(fp)
        logger.info('Loaded file :: mypass.config.json5')
except (IOError, AttributeError):
    environ = {
        'FLASK_ENV': 'Production',
        'MYPASS_DB_CONNECTION_URI': 'sqlite+pysqlite:///:memory:',
        'MYPASS_TESTENV': 1
    }
    logger.info(f'Defaulting to basic environment :: {environ}')


def getenv(key, default=None):
    return os.environ.get(key, environ.get(key, default))


class Config:
    DEBUG = False
    TESTING = False
    HOST = host
    PORT = port
    CSRF_ENABLED = True
    SECRET_KEY = secret_key
    JWT_SECRET_KEY = secret_key
    JWT_ACCESS_TOKEN_EXPIRES = access_expires_delta
    JWT_REFRESH_TOKEN_EXPIRES = refresh_expires_delta
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYPASS_DB_CONNECTION_URI', environ.get('MYPASS_DB_CONNECTION_URI'))


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
