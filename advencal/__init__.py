import os

from flask import Flask, render_template, redirect, url_for, session

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

    @app.context_processor
    # pylint: disable=unused-variable
    def image_processor():
        def get_image(row, col):
            try:
                int(row)
                int(col)
            except Exception as e:
                raise(e)
            img_url = url_for('static', filename='unc_' + str(row) + '_' + str(col) + '.png')
            retval = '<td style="width: 200px; height: 200px; text-align: center; vertical-align: middle; background-image: url(' + img_url + ');"><a href=# style="font-family: Arial, Helvetica, sans-serif; font-size: 100px; text-decoration: none; color: black; color: rgba(0, 0, 0, 0.3);">24</a></td>'
            return retval
        return dict(get_image=get_image)

    @app.route('/')
    # pylint: disable=unused-variable
    def index():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        else:
            return render_template('calendar.html')

    @app.route('/login')
    # pylint: disable=unused-variable
    def login():

        return render_template('calendar.html')

    @app.route('/logout')
    # pylint: disable=unused-variable
    def logout():
        session.clear()
        return redirect(url_for('index'))
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run()