import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# See https://auth0.com/blog/brute-forcing-hs256-is-possible-the-importance-of-using-strong-keys-to-sign-jwts/
secret_key = 'sourcehaven'  # TODO: change this to a strong secret key eg.: secrets.token_urlsafe(32)
access_expires_delta = datetime.timedelta(minutes=10)
refresh_expires_delta = datetime.timedelta(days=30)
host = '0.0.0.0'
port = 5757


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
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYPASS_DB_CONNECTION_URI')


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
