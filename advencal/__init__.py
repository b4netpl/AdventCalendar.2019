import os

from flask import Flask, render_template, redirect, url_for, session, request, flash, g

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

    # This is necessary for get_image() function to be available in
    # jinja template.
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
            
            date_offset = 0
            if session.get('admin') and session.get('time_shift'):
                date_offset = int(session['time_shift']) - date.today().day

            day_id = str(row * 4 + col + 1)
            date_today = date.today().day + date_offset
            
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
                if date_today < day_data['day_no']:
                    retval += '<a href="#notyetpopup" class="notyet">' + str(day_data['day_no']) + '</a>'
                elif date_today >= day_data['day_no']:
                    retval += '<a href="#discoverpopup' + day_id + '" class="undiscovered">' + str(day_data['day_no']) + '</a>'
                    custom_popups[day_id] = {
                        'type': 'discoverpopup' + day_id,
                        'quest': day_data['quest']
                    }
            
            retval += '</td>'
            for popup in custom_popups:
                retval += '<div id="' + custom_popups[popup]['type'] + '" class="overlay">'
                if custom_popups[popup]['quest'] is None:
                    retval += '<div class="popup"><h2>Tym razem się udało!</h2>'
                else:
                    retval += '<div class="popup"><h2>Ojej! Zadanie!</h2>'

                retval += (
                    '<a class="close" href="#">&times;</a>' +
                    '<div class="content">'
                )

                if custom_popups[popup]['quest'] is not None:
                    retval += custom_popups[popup]['quest'] + '<br><br>'
                
                retval += (
                    '<form method="post">' +
                    '<input type="hidden" id="day_id" name="day_id" value="' + day_id + '">'
                )

                if custom_popups[popup]['quest'] is not None:
                    retval += (
                        '<label for="answer">Odpowiedź</label>' +
                        '<input name="answer" id="answer" required>' +
                        '<input type="submit" value="Mlerp!">'
                    )
                else:
                    retval += '<input type="submit" value="Odkryj">'
                
                retval += (
                    '</form></div>' +
                    '</div></div>'
                )
            return retval
        return dict(get_image=get_image)

    @app.before_request
    # pylint: disable=unused-variable
    def load_logged_in_user():
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ' + str(user_id)
            ).fetchone()

    @app.route('/', methods=('GET', 'POST'))
    # pylint: disable=unused-variable
    def index():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        else:
            win = False
            db = get_db()
            if request.method == 'POST':
                
                # if quest check answer
                day_data = db.execute(
                    'SELECT * FROM day WHERE id = ' + request.form['day_id']
                ).fetchone()
                if day_data['quest'] is not None:
                    if request.form['answer'].lower() == day_data['quest_answer'].lower():
                        db.execute(
                            'INSERT OR IGNORE INTO discovered_days (day_id, user_id) VALUES (' + request.form['day_id'] + ', ' + str(session['user_id']) + ')'
                        )
                else:
                    db.execute(
                        'INSERT OR IGNORE INTO discovered_days (day_id, user_id) VALUES (' + request.form['day_id'] + ', ' + str(session['user_id']) + ')'
                    )

                db.commit()
            
            days_discovered = db.execute(
                'select count(distinct day.id) from day inner join discovered_days on day.id=day_id where user_id = ?', (session['user_id'], )
            ).fetchone()

            if int(days_discovered[0]) == 24:
                win = True
            
            return render_template('calendar.html', win=win)

    @app.route('/tweaks', methods=('GET', 'POST'))
    # pylint: disable=unused-variable
    def tweaks():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        if not session.get('admin'):
            return redirect(url_for('index'))

        date_today = date.today().day

        if request.method == 'POST':
            
            if 'del_discos' in request.form:
                conditions = ['user_id in (' + ','.join(request.form.getlist('del_users')) + ')']
                if request.form['del_discos'] == 'del_taf':
                    conditions.append('day_id not in (select id from day where day_no < ' + str(date_today) + ')')
                if request.form.get('del_except_quests'):
                    conditions.append('day_id not in (select id from day where quest is not null)')
                db = get_db()
                # TODO count rows to delete
                db.execute(
                    'DELETE FROM discovered_days WHERE ' + ' AND '.join(conditions)
                )
                db.commit()

            elif 'time_shift' in request.form:
                if date_today != int(request.form['time_shift']):
                    session['time_shift'] = request.form['time_shift']
                else:
                    session.pop('time_shift', None)
            
            elif 'quest_del' in request.form:
                db = get_db()
                db.execute(
                    'UPDATE day SET quest=NULL, quest_answer=NULL WHERE id = ?', (request.form['quest_del'], )
                )
                db.commit()
                return redirect(url_for('tweaks'))

            return redirect(url_for('index'))

        if request.method == 'GET':
            db = get_db()
            users = db.execute(
                'SELECT id, username FROM user'
            ).fetchall()
            days = db.execute(
                'SELECT id, day_no, quest FROM day ORDER BY day_no'
            ).fetchall()
            discos = db.execute(
                'SELECT day_id, user_id FROM discovered_days'
            ).fetchall()
            
            return render_template('tweaks.html', users=users, date_today=date_today, days=days, discos=discos)

    @app.route('/questedit', methods=['POST'])
    # pylint: disable=unused-variable
    def questedit():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        if not session.get('admin'):
            return redirect(url_for('index'))

        db = get_db()

        if 'quest_edit' in request.form:
            day_id = request.form['quest_edit']
            quest_data = db.execute(
                'SELECT * FROM day WHERE id = ?', (day_id,)
            ).fetchone()
            return render_template('questedit.html', quest=quest_data['quest'], quest_answer=quest_data['quest_answer'], day_id=day_id)

        if 'day_id' in request.form and request.form['quest'] != "None":
            db.execute(
                'UPDATE day SET quest = ?, quest_answer = ? WHERE id = ?', (request.form['quest'], request.form['quest_answer'], request.form['day_id'])
            )
            db.commit()
        
        return redirect(url_for('tweaks'))


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
                session['admin'] = user['admin']
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