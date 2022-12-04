from advencal import db
from flask import session, g, \
        redirect, url_for, request, flash, render_template
from datetime import datetime
from advencal.models import User, Day, DiscoveredDays, Help
from advencal.helpers import commit
from advencal.basic import bp


@bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.get_user(user_id)


@bp.route('/', methods=('GET', 'POST'))
def index():

    if session.get('user_id') is None:
        return redirect(url_for('basic.login'))
    else:
        win = False

        if request.method == 'POST':

            # if quest check answer
            day_data = Day.get_day(request.form['day_id'])
            if day_data.quest is not None:
                if request.form['answer'].lower() == \
                        day_data.quest_answer.lower():

                    visit = DiscoveredDays(
                            day_id=request.form['day_id'],
                            user_id=str(session['user_id'])
                            )
                    db.session.add(visit)
                    commit(db.session)
                # wrong answer
                else:
                    flash(
                            'To nie jest prawidłowa odpowiedź... '
                            'Spróbuj jeszcze raz!',
                            'warning'
                            )
            else:
                visit = DiscoveredDays(
                        day_id=request.form['day_id'],
                        user_id=str(session['user_id'])
                        )
                db.session.add(visit)
                commit(db.session)

        if len(g.user.days) == 24:
            win = True

        date_offset = datetime.now().day
        if session.get('admin') and session.get('time_shift'):
            date_offset = int(session['time_shift'])

        date_today = datetime.now().replace(day=date_offset)

        days = Day.query.all()

        day_data = {}
        for day in days:
            day_data[day.id] = {
                'day_no': day.day_no,
                'quest': day.quest,
                'quest_answer': day.quest_answer,
                'hour': day.hour
            }

        discovered = list(map(lambda day: day.day_id, g.user.days))

        return render_template(
                'calendar.html.j2',
                win=win,
                date_today=date_today,
                day_data=day_data,
                discovered=discovered
                )


@bp.route('/help')
def help():

    if session.get('user_id') is None:
        return redirect(url_for('basic.login'))

    admin = session.get('admin')
    userhelp = Help.query.filter_by(admin=False).order_by(Help.order).all()
    adminhelp = Help.query.filter_by(admin=True).order_by(Help.order).all()

    return render_template(
            'help.html.j2',
            admin=admin,
            userhelp=userhelp,
            adminhelp=adminhelp
            )


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = 'Niepoprawny login'
        elif not user.check_password(password):
            error = 'Niepoprawne hasło'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            session['admin'] = user.admin
            return redirect(url_for('basic.index'))

        flash(error, 'warning')

    return render_template('login.html.j2')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('basic.index'))


@bp.route('/changepass', methods=('GET', 'POST'))
def changepass():

    if session.get('user_id') is None:
        return redirect(url_for('basic.login'))

    if request.method == 'POST':
        user_id = session.get('user_id')
        old_pass = request.form['old_pass']
        new_pass = request.form['new_pass']
        new_pass_again = request.form['new_pass_again']

        error = False
        user = User.get_user(user_id)

        if not user.check_password(old_pass):
            flash('Niepoprawne hasło', 'danger')
            error = True

        if new_pass != new_pass_again:
            flash('Nowe hasła nie są jednakowe', 'danger')
            error = True

        if error is False:
            user.set_password(new_pass)
            commit(db.session)

            flash('Hasło zmienione poprawnie', 'success')
            return redirect(url_for('basic.index'))

        flash('Hasło nie zostało zmienione', 'warning')

    return render_template('changepass.html.j2')
