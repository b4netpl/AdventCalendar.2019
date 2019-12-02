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
            
            day_id = str(row * 4 + col + 1)
            
            db = get_db()
            day_data = db.execute(
                'SELECT * FROM day WHERE id = ' + day_id
            ).fetchone()
            is_discovered = db.execute(
                'SELECT * FROM discovered_days WHERE day_id = ' + day_id + ' AND user_id = ' + str(session.get('user_id'))
            ).fetchone()
            # if its discovered change img
            if is_discovered is None:
                img_url = url_for('static', filename=app.env + '/unc_' + str(row) + '_' + str(col) + '.png')
            else:
                img_url = url_for('static', filename=app.env + '/disc_' + str(row) + '_' + str(col) + '.png')
            retval = '<td class="cell" style="background-image: url(' + img_url + ');">'
            # set link based on date, discovered and quest
            custom_popups = {}
            if is_discovered is None:
                if date.today().day < day_data['day_no']:
                    retval += '<a href="#notyetpopup" class="notyet">' + str(day_data['day_no']) + '</a>'
                elif date.today().day >= day_data['day_no']:
                    retval += '<a href="#discoverpopup' + day_id + '" class="undiscovered">' + str(day_data['day_no']) + '</a>'
                    custom_popups[day_id] = {
                        'type': 'discoverpopup' + day_id,
                        'quest': day_data['quest']
                    }
                # TODO late discover!
                #else:
                #    retval += '?'
            
            retval += '</td>'
            for popup in custom_popups:
                retval += (
                    '<div id="' + custom_popups[popup]['type'] + '" class="overlay">' +
                    '<div class="popup"><h2>Tym razem się udało!</h2>' +
                    '<a class="close" href="#">&times;</a>' +
                    '<div class="content"><form method="post"><input type="hidden" id="day_id" name="day_id" value="' + day_id + '"><input type="submit" value="Odkryj"></form></div>' +
                    '</div></div>'
                )
            return retval
        return dict(get_image=get_image)

    @app.route('/', methods=('GET', 'POST'))
    # pylint: disable=unused-variable
    def index():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        else:
            if request.method == 'POST':
                db = get_db()
                # TODO if quest check answer
                db.execute(
                    'INSERT INTO discovered_days (day_id, user_id, answered) VALUES (' + request.form['day_id'] + ', ' + str(session['user_id']) + ', true)'
                )
                db.commit()
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