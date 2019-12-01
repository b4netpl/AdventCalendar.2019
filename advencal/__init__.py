import os

from flask import Flask, render_template, redirect, url_for, session, request, flash

from werkzeug.security import check_password_hash, generate_password_hash

from advencal.db import get_db

from datetime import date

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
            
            # Reaching to db for every cell is sub-optimal, to say the least,
            # but I'm in a hurry. :( This call should be moved to index() def 
            # and the result put into global var.
            db = get_db()
            day_data = db.execute(
                'SELECT * FROM day WHERE id = ' + str(row * 4 + col + 1)
            ).fetchone()
            img_url = url_for('static', filename='unc_' + str(row) + '_' + str(col) + '.png')
            retval = '<td style="width: 200px; height: 200px; text-align: center; vertical-align: middle; background-image: url(' + img_url + ');"><a href=# style="font-size: 100px; text-decoration: none; color: black; color: rgba(0, 0, 0, 0.3);">' + str(day_data['day_no']) + '</a></td>'
            return retval
        return dict(get_image=get_image)

    @app.route('/')
    # pylint: disable=unused-variable
    def index():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        else:
            return render_template('calendar.html')

    @app.route('/login', methods=('GET', 'POST'))
    # pylint: disable=unused-variable
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db = get_db()
            error = None
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))
            
            flash(error)

        return render_template('login.html')

    @app.route('/logout')
    # pylint: disable=unused-variable
    def logout():
        session.clear()
        return redirect(url_for('index'))
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run()