import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ['pl', 'en']


class TestConfig(Config):
    SECRET_KEY = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
