import os
import random
import string

from advencal import db
from flask import session, redirect, request, url_for, render_template, \
        flash, Markup
from werkzeug.utils import secure_filename
from datetime import datetime, time
from advencal.models import User, Day, DiscoveredDays, Help
from advencal.helpers import commit, admin_required
from advencal.admin import bp
from flask_babel import _
from flask_login import login_required


@bp.route('/edit_quests', methods=('GET', 'POST'))
@login_required
@admin_required
def edit_quests():

    date_today = datetime.today().day

    if request.method == 'POST':

        if 'del_quest' in request.form:
            quest = Day.get_day(request.form['del_quest'])
            quest.quest = None
            quest.quest_answer = None
            commit(db.session)

        elif 'upload_asset' in request.files:
            f = request.files['upload_asset']
            f.save(os.path.join(
                    './advencal/static/quests/',
                    secure_filename(f.filename)
                    ))

        elif 'del_asset' in request.form:
            os.remove(os.path.join(
                    './advencal/static/quests/',
                    secure_filename(request.form['del_asset'])
                    ))

        return redirect(url_for('admin.edit_quests'))

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


@bp.route('/edit_quest', methods=['POST'])
@login_required
@admin_required
def edit_quest():

    if 'edit_quest' in request.form:
        quest_data = Day.get_day(int(request.form['edit_quest']))
        return render_template(
                'edit_quest.html.j2',
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

    return redirect(url_for('admin.edit_quests'))


@bp.route('/tweaks', methods=('GET', 'POST'))
@login_required
@admin_required
def tweaks():

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

        return redirect(url_for('basic.index'))

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


@bp.route('/users', methods=('GET', 'POST'))
@login_required
@admin_required
def users():

    users = User.query.all()

    if request.method == 'POST':

        if 'new_user' in request.form:

            new_user = request.form['new_user']
            if User.exists(new_user):
                flash(Markup(_(
                        'Użytkownik <strong>%(new_user)s</strong>'
                        ' już istnieje',
                        new_user=new_user
                        )), 'warning')
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

        if 'del_user' in request.form:

            user = User.get_user(request.form['del_user'])
            del_username = user.username
            db.session.delete(user)
            commit(db.session)

            flash(Markup(_(
                    'Użytkownik <strong>%(del_username)s</strong>'
                    ' został usunięty', del_username=del_username
                    )), 'success')

            users = User.query.all()

            return render_template('users.html.j2', users=users)

    if request.method == 'GET':
        pass

    return render_template('users.html.j2', users=users)


@bp.route('/edit_help', methods=('GET', 'POST'))
@login_required
@admin_required
def edit_help():

    if request.method == 'POST':

        if 'helpitemtitle' in request.form:

            lastitem = Help.get_max_order(
                    admin=bool(request.form.get('helpitemadmin'))
                    )
            newhelpitem = Help(
                    order=lastitem + 1,
                    title=request.form['helpitemtitle'],
                    body=request.form['helpitembody'],
                    admin=bool(request.form.get('helpitemadmin'))
                    )

            db.session.add(newhelpitem)
            commit(db.session)

        elif 'userhelp_order' in request.form:

            def reorder_helpitems(form_field, admin):
                userhelp_order = request.form[form_field].split(',')
                for i, o in enumerate(userhelp_order, start=1):
                    helpitem = Help.get_helpitem(o)
                    helpitem.order = i
                    helpitem.admin = admin

            reorder_helpitems('userhelp_order', False)
            reorder_helpitems('adminhelp_order', True)
            commit(db.session)

        elif 'del_helpitem' in request.form:

            helpitem = Help.get_helpitem(request.form['helpitem_id'])
            db.session.delete(helpitem)
            commit(db.session)

        elif 'save_helpitem' in request.form:

            helpitem = Help.get_helpitem(request.form['helpitem_id'])
            helpitem.title = request.form['title']
            helpitem.body = request.form['body']
            commit(db.session)

    userhelp = Help.query.filter_by(admin=False).order_by(Help.order).all()
    adminhelp = Help.query.filter_by(admin=True).order_by(Help.order).all()

    return render_template(
            'edit_help.html.j2',
            userhelp=userhelp,
            adminhelp=adminhelp
            )
