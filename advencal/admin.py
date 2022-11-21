import os
import random
import string

from advencal import app
from flask import session, redirect, request, url_for, render_template, flash, Markup
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from datetime import datetime
from operator import itemgetter
#from advencal.db import get_db  # TODO remove when moved to SQLAlchemy


@app.route('/tweaks', methods=('GET', 'POST'))
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
