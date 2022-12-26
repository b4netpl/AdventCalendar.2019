from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension


db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
login = LoginManager()
login.login_view = 'basic.login'
login.login_message = None
toolbar = DebugToolbarExtension()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    babel.init_app(app)

    login.init_app(app)

    toolbar.init_app(app)

    from advencal.basic import bp as basic_bp
    app.register_blueprint(basic_bp)

    from advencal.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from advencal import models  # noqa: F401,E402
