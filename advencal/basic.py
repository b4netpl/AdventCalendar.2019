from advencal import app
from flask import session, g, redirect, url_for, request, flash, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from advencal.db import get_db  # TODO remove when moved to SQLAlchemy


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (str(user_id), )
        ).fetchone()


@app.route('/', methods=('GET', 'POST'))
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
def help():

    if session.get('user_id') is None:
        return redirect(url_for('login'))
    admin = session.get('admin')

    return render_template('help.html', admin=admin)


@app.route('/login', methods=('GET', 'POST'))
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
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/changepass', methods=('GET', 'POST'))
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
