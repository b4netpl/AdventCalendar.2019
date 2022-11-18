# import os, sys
# print(repr(request.form), file=sys.stderr)
# - do testowania, wysyła zawartość do terminala

import os
import string
import random

from flask import Flask, Markup, g
from flask import render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from advencal.db import get_db
from datetime import datetime
from operator import itemgetter


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
                        'SELECT * FROM day WHERE id = ?',
                        (request.form['day_id'], )
                        ).fetchone()
                if day_data['quest'] is not None:
                    if request.form['answer'].lower() == day_data['quest_answer'].lower():
                        db.execute(
                            'INSERT OR IGNORE INTO discovered_days (day_id, user_id) VALUES (?, ?)', (request.form['day_id'], str(session['user_id']), )
                        )
                    # wrong answer
                    else:
                        flash('To nie jest prawidłowa odpowiedź... Spróbuj jeszcze raz!', 'warning')
                else:
                    db.execute(
                        'INSERT OR IGNORE INTO discovered_days (day_id, user_id) VALUES (?, ?)', (request.form['day_id'], str(session['user_id']), )
                    )

                db.commit()

            days_discovered = db.execute(
                'select count(distinct day.id) from day inner join discovered_days on day.id=day_id where user_id = ?', (session['user_id'], )
            ).fetchone()

            if int(days_discovered[0]) == 24:
                win = True

            date_offset = datetime.now().day
            if session.get('admin') and session.get('time_shift'):
                date_offset = int(session['time_shift'])

            date_today = datetime.now().replace(day=date_offset)

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
                    'quest_answer': day['quest_answer'],
                    'hour': day['hour']
                }

            db.row_factory = lambda cursor, row: row[0]
            discovered = db.execute(
                    'SELECT day_id FROM discovered_days WHERE user_id = ?',
                    (str(session.get('user_id')), )
                    ).fetchall()

            return render_template(
                    'calendar.html',
                    win=win,
                    date_today=date_today,
                    day_data=day_data,
                    discovered=discovered
                    )

    @app.route('/help')
    # pylint: disable=unused-variable
    def help():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        admin = session.get('admin')

        return render_template('help.html', admin=admin)

    @app.route('/tweaks', methods=('GET', 'POST'))
    # pylint: disable=unused-variable
    def tweaks():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        if not session.get('admin'):
            return redirect(url_for('index'))

        date_today = datetime.today().day

        if request.method == 'POST':

            if 'del_discos' in request.form:
                conditions = [
                        'user_id in ('
                        + ','.join(request.form.getlist('del_users'))
                        + ')'
                        ]
                if request.form['del_discos'] == 'del_taf':
                    conditions.append(
                            'day_id not in (select id from day where day_no < '
                            + str(date_today)
                            + ')'
                            )
                if request.form.get('del_except_quests'):
                    conditions.append(
                            'day_id not in (select id from day where quest is not null)'
                            )
                db = get_db()
                # TODO count rows to delete
                db.execute(
                        'DELETE FROM discovered_days WHERE '
                        + ' AND '.join(conditions)
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

            return redirect(url_for('index'))

        if request.method == 'GET':
            db = get_db()
            users = db.execute(
                'SELECT id, username FROM user'
            ).fetchall()
            days = db.execute(
                'SELECT id, day_no, quest, quest_answer, hour FROM day ORDER BY day_no'
            ).fetchall()
            discos = db.execute(
                'SELECT day_id, user_id FROM discovered_days'
            ).fetchall()

            return render_template(
                    'tweaks.html',
                    users=users,
                    date_today=date_today,
                    days=days,
                    discos=discos
                    )

    @app.route('/questsed', methods=('GET', 'POST'))
    # pylint: disable=unused-variable
    def questsed():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        if not session.get('admin'):
            return redirect(url_for('index'))

        date_today = datetime.today().day

        if request.method == 'POST':

            if 'quest_del' in request.form:
                db = get_db()
                db.execute(
                    'UPDATE day SET quest=NULL, quest_answer=NULL WHERE id = ?', (request.form['quest_del'], )
                )
                db.commit()
                return redirect(url_for('questsed'))

            elif 'upload_graffile' in request.files:
                f = request.files['upload_graffile']
                f.save(os.path.join(
                        './advencal/static/quests/',
                        secure_filename(f.filename)
                        ))
                return redirect(url_for('questsed'))

            return redirect(url_for('index'))

        if request.method == 'GET':
            db = get_db()
            users = db.execute(
                'SELECT id, username FROM user'
            ).fetchall()
            days = db.execute(
                'SELECT id, day_no, quest, quest_answer, hour FROM day ORDER BY day_no'
            ).fetchall()
            graffiles = os.listdir('./advencal/static/quests/')
            return render_template(
                    'quests.html',
                    users=users,
                    date_today=date_today,
                    days=days,
                    graffiles=graffiles
                    )

    @app.route('/users', methods=('GET', 'POST'))
    # pylint: disable=unused-variable
    def users():

        if session.get('user_id') is None:
            return redirect(url_for('login'))
        if not session.get('admin'):
            return redirect(url_for('index'))

        db = get_db()
        users = db.execute(
            'SELECT id, username, admin FROM user'
        ).fetchall()

        usersmap = {}
        for user in users:
            usersmap[user['id']] = user['username']

        if request.method == 'POST':

            if 'new_user' in request.form:

                new_user = request.form['new_user']
                if new_user in map(itemgetter('username'), users):
                    flash(Markup(
                            'Użytkownik <strong>'
                            + new_user
                            + '</strong> już istnieje'
                            ), 'warning')
                    return render_template('users.html', users=users)

                if request.form['pass_source'] == 'pass_input':
                    new_pass = request.form['new_pass']
                else:
                    new_pass = ''.join(random.sample(
                            string.ascii_letters
                            + string.digits,
                            20
                            ))

                db.execute(
                    'INSERT INTO user (username, password) VALUES (?, ?)',
                    (new_user, generate_password_hash(new_pass), )
                    )
                db.commit()
                credentials = {
                    "login": new_user,
                    "pass": new_pass
                }

                users = db.execute(
                    'SELECT id, username, admin FROM user'
                ).fetchall()

                return render_template(
                        'users.html',
                        users=users,
                        credentials=credentials
                        )

            if 'change_pass_source' in request.form:
                if request.form['change_pass_source'] == 'change_pass_input':
                    new_pass = request.form['change_pass']
                else:
                    new_pass = ''.join(random.sample(
                            string.ascii_letters
                            + string.digits,
                            20
                            ))

                db.execute(
                    'UPDATE user SET password = ? WHERE id = ?',
                    (
                        generate_password_hash(new_pass),
                        request.form['user_id']
                    )
                )
                db.commit()

                credentials = {
                    "login": usersmap[int(request.form['user_id'])],
                    "pass": new_pass
                }
                return render_template(
                        'users.html',
                        users=users,
                        credentials=credentials
                        )

            if 'user_del' in request.form:
                db.execute(
                    'DELETE FROM user WHERE id = ?',
                    (request.form['user_del'], )
                )
                db.commit()
                flash(Markup(
                        'Użytkownik <strong>'
                        + usersmap[int(request.form['user_del'])]
                        + '</strong> został usunięty'
                        ), 'success')
                users = db.execute(
                    'SELECT id, username, admin FROM user'
                ).fetchall()
                return render_template('users.html', users=users)

        if request.method == 'GET':
            pass

        return render_template('users.html', users=users)

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
                'SELECT * FROM day WHERE id = ?', (day_id, )
            ).fetchone()
            return render_template(
                    'questedit.html',
                    quest=str(quest_data['quest'] or ''),
                    quest_answer=str(quest_data['quest_answer'] or ''),
                    hour=quest_data['hour'],
                    day_id=day_id
                    )

        if 'day_id' in request.form:

            db.execute(
                'UPDATE day SET quest = ?, quest_answer = ?, hour = ? WHERE id = ?', (request.form['quest'] or None, request.form['quest_answer'] or None, request.form['hour'], request.form['day_id'], )
            )
            db.commit()

        return redirect(url_for('questsed'))

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
                    'UPDATE user SET password = ? WHERE id = ?',
                    (generate_password_hash(new_pass), user_id, )
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
