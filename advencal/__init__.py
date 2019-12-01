import os

from flask import Flask, render_template

def create_app():

    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ['SECRET_KEY'],
        DATABASE=os.path.join(app.instance_path, 'advencal.sqlite'),
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import db
    db.init_app(app)

    @app.route('/')
    # pylint: disable=unused-variable
    def index():

        return render_template('calendar.html')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()