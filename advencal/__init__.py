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


    @app.before_request
    # pylint: disable=unused-variable
    def load_logged_in_user():
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (str(user_id), )
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
                    'SELECT * FROM day WHERE id = ?', (request.form['day_id'], )
                ).fetchone()
                if day_data['quest'] is not None:
                    if request.form['answer'].lower() == day_data['quest_answer'].lower():
                        db.execute(
                            'INSERT OR IGNORE INTO discovered_days (day_id, user_id) VALUES (?, ?)', (request.form['day_id'], str(session['user_id']), )
                        )
                else:
                    db.execute(
                        'INSERT OR IGNORE INTO discovered_days (day_id, user_id) VALUES (?, ?)', (request.form['day_id'], str(session['user_id']), )
                    )

                db.commit()
            
            days_discovered = db.execute(
                'select count(distinct day.id) from day inner join discovered_days on day.id=day_id where user_id = ?', (session['user_id'], )
            ).fetchone()

            if int(days_discovered[0]) == 18:
                win = True
            
            date_offset = 0
            if session.get('admin') and session.get('time_shift'):
                date_offset = int(session['time_shift']) - date.today().day

            date_today = date.today().day + date_offset
            
            def dict_factory(cursor, row):
                d = {}
                for idx, col in enumerate(cursor.description):
                    d[col[0]] = row[idx]
                return d
            
            db.row_factory = dict_factory
            days = db.execute(
                'SELECT * FROM day'
            ).fetchall()

            day_data = {}
            for day in days:
                day_data[day['id']] = {
                    'day_no': day['day_no'],
                    'quest': day['quest'],
                    'quest_answer': day['quest_answer']
                }

            db.row_factory = lambda cursor, row: row[0]
            discovered = db.execute(
                'SELECT day_id FROM discovered_days WHERE user_id = ?', (str(session.get('user_id')), )
            ).fetchall()

            return render_template('calendar.html', win=win, date_today=date_today, day_data=day_data, discovered=discovered, app_env=app.env)

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

            elif 'solve_users' in request.form:
                db = get_db()
                db.execute(
                    'INSERT OR IGNORE INTO discovered_days (day_id, user_id) WITH users(user_id) AS (SELECT * FROM (VALUES (' + '),('.join(request.form.getlist('solve_users')) + '))) SELECT id, user_id FROM day, users'
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
                'SELECT id, day_no, quest, quest_answer FROM day ORDER BY day_no'
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
                error = 'Niepoprawny login'
            elif not check_password_hash(user['password'], password):
                error = 'Niepoprawne hasło'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                session['admin'] = user['admin']
                return redirect(url_for('index'))
            
            flash(error, 'warning')

        return render_template('login.html')

    @app.route('/logout')
    # pylint: disable=unused-variable
    def logout():
        session.clear()
        return redirect(url_for('index'))

    @app.route('/changepass', methods=('GET', 'POST'))
    # pylint: disable=unused-variable
    def changepass():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            user_id = session.get('user_id')
            old_pass = request.form['old_pass']
            new_pass = request.form['new_pass']
            new_pass_again = request.form['new_pass_again']

            db = get_db()
            error = False
            user = db.execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()

            if not check_password_hash(user['password'], old_pass):
                flash('Niepoprawne hasło', 'danger')
                error = True

            if new_pass != new_pass_again:
                flash('Nowe hasła nie są jednakowe', 'danger')
                error = True

            if error is False:
                db.execute(
                    'UPDATE user SET password = ? WHERE id = ?', (generate_password_hash(new_pass), user_id)
                )
                db.commit()

                flash('Hasło zmienione poprawnie', 'success')
                return redirect(url_for('index'))
            
            flash('Hasło nie zostało zmienione', 'warning')

        return render_template('changepass.html')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()