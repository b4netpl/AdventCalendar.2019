import os

from flask import Flask

def create_app():

    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ['SECRET_KEY']
    )

    @app.route('/')
    # pylint: disable=unused-variable
    def index():

        return 'meh'

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()