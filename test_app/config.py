import os

class BaseConfig(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = '5bs5zIsG08A3P4hF1bDSVHiNO23z6qqO9qMm5xM/TX1hU3wUDWY6o2l0wWTifqWqsO3S1YV1voyE'

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_ECHO = True

class ProductionConfig(BaseConfig):
    DEBUG = False