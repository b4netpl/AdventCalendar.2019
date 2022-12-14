from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from advencal.basic import bp as basic_bp
    app.register_blueprint(basic_bp)

    from advencal.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    return app


from advencal import models  # noqa: F401,E402
