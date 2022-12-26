from advencal import db
from flask import redirect, url_for, request, flash, render_template, session
from datetime import datetime
from advencal.models import User, Day, DiscoveredDays, Help
from advencal.helpers import commit
from advencal.basic import bp
from flask_babel import _
from flask_login import login_user, logout_user, current_user, login_required


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():

    win = False

    if request.method == 'POST':

        # if quest check answer
        day_data = Day.get_day(request.form['day_id'])
        if day_data.quest is not None:
            if request.form['answer'].lower() == \
                    day_data.quest_answer.lower():

                visit = DiscoveredDays(
                        day_id=request.form['day_id'],
                        user_id=str(current_user.id)
                        )
                db.session.add(visit)
                commit(db.session)
            # wrong answer
            else:
                flash(_(
                        'To nie jest prawidłowa odpowiedź... '
                        'Spróbuj jeszcze raz!'
                        ), 'warning')
        else:
            visit = DiscoveredDays(
                    day_id=request.form['day_id'],
                    user_id=str(current_user.id)
                    )
            db.session.add(visit)
            commit(db.session)

    if len(current_user.days) == 24:
        win = True

    date_offset = datetime.now().day
    if current_user.admin and session.get('time_shift'):
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

    discovered = list(map(lambda day: day.day_id, current_user.days))

    return render_template(
            'calendar.html.j2',
            win=win,
            date_today=date_today,
            day_data=day_data,
            discovered=discovered
            )


@bp.route('/help')
@login_required
def help():

    userhelp = Help.query.filter_by(admin=False).order_by(Help.order).all()
    adminhelp = Help.query.filter_by(admin=True).order_by(Help.order).all()

    return render_template(
            'help.html.j2',
            userhelp=userhelp,
            adminhelp=adminhelp
            )


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('basic.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.query.filter_by(username=username).scalar()

        if user is None:
            error = _('Niepoprawny login')
        elif not user.check_password(password):
            error = _('Niepoprawne hasło')

        if error is None:
            login_user(user, remember=request.form.get('remember_me'))
            return redirect(url_for('basic.index'))

        flash(error, 'warning')

    return render_template('login.html.j2')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('basic.index'))


@bp.route('/change_pass', methods=('GET', 'POST'))
@login_required
def change_pass():

    if request.method == 'POST':
        old_pass = request.form['old_pass']
        new_pass = request.form['new_pass']
        new_pass_again = request.form['new_pass_again']

        error = False

        if not current_user.check_password(old_pass):
            flash(_('Niepoprawne hasło'), 'danger')
            error = True

        if new_pass != new_pass_again:
            flash(_('Nowe hasła nie są jednakowe'), 'danger')
            error = True

        if error is False:
            current_user.set_password(new_pass)
            commit(db.session)

            flash(_('Hasło zmienione poprawnie'), 'success')
            return redirect(url_for('basic.logout'))

        flash(_('Hasło nie zostało zmienione'), 'warning')

    return render_template('change_pass.html.j2')
