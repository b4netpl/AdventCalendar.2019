import os
import random
import string

from advencal import app, db
from flask import session, redirect, request, url_for, render_template, flash
from flask import Markup
from werkzeug.utils import secure_filename
from datetime import datetime, time
from advencal.models import User, Day, DiscoveredDays, Help
from advencal.helpers import commit


@app.route('/questsed', methods=('GET', 'POST'))
def questsed():

    if session.get('user_id') is None:
        return redirect(url_for('login'))
    if not session.get('admin'):
        return redirect(url_for('index'))

    date_today = datetime.today().day

    if request.method == 'POST':

        if 'quest_del' in request.form:
            quest = Day.get_day(request.form['quest_del'])
            quest.quest = None
            quest.quest_answer = None
            commit(db.session)
            return redirect(url_for('questsed'))

        elif 'upload_asset' in request.files:
            f = request.files['upload_asset']
            f.save(os.path.join(
                    './advencal/static/quests/',
                    secure_filename(f.filename)
                    ))
            return redirect(url_for('questsed'))

        elif 'asset_del' in request.form:
            os.remove(os.path.join(
                    './advencal/static/quests/',
                    secure_filename(request.form['asset_del'])
                    ))
            return redirect(url_for('questsed'))

        return redirect(url_for('index'))

    if request.method == 'GET':
        users = User.query.all()
        days = Day.query.order_by(Day.day_no).all()
        assets = os.listdir('./advencal/static/quests/')
        return render_template(
                'quests.html.j2',
                users=users,
                date_today=date_today,
                days=days,
                assets=assets
                )


@app.route('/questedit', methods=['POST'])
def questedit():

    if session.get('user_id') is None:
        return redirect(url_for('login'))
    if not session.get('admin'):
        return redirect(url_for('index'))

    if 'quest_edit' in request.form:
        quest_data = Day.get_day(int(request.form['quest_edit']))
        return render_template(
                'questedit.html.j2',
                quest=str(quest_data.quest or ''),
                quest_answer=str(quest_data.quest_answer or ''),
                hour=quest_data.hour,
                day_id=quest_data.id
                )

    if 'day_id' in request.form:

        day = Day.get_day(request.form['day_id'])
        day.quest = request.form['quest'] or None
        day.quest_answer = request.form['quest_answer'] or None
        day.hour = time.fromisoformat(request.form['hour'])
        commit(db.session)

    return redirect(url_for('questsed'))


@app.route('/tweaks', methods=('GET', 'POST'))
def tweaks():

    if session.get('user_id') is None:
        return redirect(url_for('login'))
    if not session.get('admin'):
        return redirect(url_for('index'))

    date_today = datetime.today().day

    if request.method == 'POST':

        if 'del_discos' in request.form:
            visits_to_delete = DiscoveredDays.query.filter(
                    DiscoveredDays.user_id.in_(
                            request.form.getlist('del_users')
                            )
                    )
            if request.form['del_discos'] == 'del_taf':
                today_and_future = Day.query.filter(
                        Day.day_no < date_today
                        ).with_entities(Day.id)
                visits_to_delete = visits_to_delete.filter(
                        DiscoveredDays.day_id.not_in(today_and_future)
                        )
            if request.form.get('del_except_quests'):
                quest_days = Day.query.filter(
                        Day.quest != ''
                        ).with_entities(Day.id)
                visits_to_delete = visits_to_delete.filter(
                        DiscoveredDays.day_id.not_in(quest_days)
                        )
            for visit in visits_to_delete.all():
                db.session.delete(visit)
            commit(db.session)

        elif 'solve_users' in request.form:
            visits_to_add = []
            for user_id in request.form.getlist('solve_users'):
                visits = DiscoveredDays.query.filter_by(
                        user_id=user_id
                        ).with_entities(DiscoveredDays.day_id)
                unvisited = Day.query.filter(Day.id.not_in(visits)).all()
                for visit in unvisited:
                    visit_to_append = DiscoveredDays(
                            user_id=user_id, day_id=visit.id
                            )
                    visits_to_add.append(visit_to_append)
            db.session.add_all(visits_to_add)
            commit(db.session)

        elif 'time_shift' in request.form:
            if date_today != int(request.form['time_shift']):
                session['time_shift'] = request.form['time_shift']
            else:
                session.pop('time_shift', None)

        return redirect(url_for('index'))

    if request.method == 'GET':
        users = User.query.all()
        days = Day.query.order_by(Day.day_no).all()
        discos = DiscoveredDays.query.all()

        return render_template(
                'tweaks.html.j2',
                users=users,
                date_today=date_today,
                days=days,
                discos=discos
                )


@app.route('/users', methods=('GET', 'POST'))
def users():

    if session.get('user_id') is None:
        return redirect(url_for('login'))
    if not session.get('admin'):
        return redirect(url_for('index'))

    users = User.query.all()

    if request.method == 'POST':

        if 'new_user' in request.form:

            new_user = request.form['new_user']
            if User.check_username(new_user):
                flash(Markup(
                        'Użytkownik <strong>'
                        + new_user
                        + '</strong> już istnieje'
                        ), 'warning')
                return render_template('users.html.j2', users=users)

            if request.form['pass_source'] == 'pass_input':
                new_pass = request.form['new_pass']
            else:
                new_pass = ''.join(random.sample(
                        string.ascii_letters
                        + string.digits,
                        20
                        ))

            user = User(username=new_user, admin=False)
            user.set_password(new_pass)
            db.session.add(user)
            commit(db.session)
            credentials = {
                "login": new_user,
                "pass": new_pass
            }

            users = User.query.all()

            return render_template(
                    'users.html.j2',
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

            user = User.get_user(request.form['user_id'])
            user.set_password(new_pass)
            commit(db.session)

            credentials = {
                "login": user.username,
                "pass": new_pass
            }
            return render_template(
                    'users.html.j2',
                    users=users,
                    credentials=credentials
                    )

        if 'user_del' in request.form:

            user = User.get_user(request.form['user_del'])
            username_del = user.username
            db.session.delete(user)
            commit(db.session)

            flash(Markup(
                    'Użytkownik <strong>'
                    + username_del
                    + '</strong> został usunięty'
                    ), 'success')

            users = User.query.all()

            return render_template('users.html.j2', users=users)

    if request.method == 'GET':
        pass

    return render_template('users.html.j2', users=users)


@app.route('/edithelp', methods=('GET', 'POST'))
def edithelp():

    if session.get('user_id') is None:
        return redirect(url_for('login'))
    if not session.get('admin'):
        return redirect(url_for('index'))

    if request.method == 'POST':

        if 'helpitemtitle' in request.form:

            if request.form.get('helpitemadmin'):
                helpitemadmin = True
            else:
                helpitemadmin = False

        lastitem = Help.get_max_order(admin=helpitemadmin)
        newhelpitem = Help(
                order=lastitem + 1,
                title=request.form['helpitemtitle'],
                body=request.form['helpitembody'],
                admin=helpitemadmin
                )

        db.session.add(newhelpitem)
        commit(db.session)

    admin = session.get('admin')
    userhelp = Help.query.filter_by(admin=False).order_by(Help.order).all()
    adminhelp = Help.query.filter_by(admin=True).order_by(Help.order).all()

    return render_template(
            'edithelp.html.j2',
            admin=admin,
            userhelp=userhelp,
            adminhelp=adminhelp
            )
