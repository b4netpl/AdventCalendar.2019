import click
import json
import os

from flask.cli import AppGroup
from datetime import time
from advencal import db
from advencal.models import User, Day, DiscoveredDays, Help
from advencal.helpers import commit


def register(app):

    init_data = AppGroup('init-data', short_help="Load data into db.")

    @init_data.command("create-user")
    @click.option('--username', prompt=True)
    @click.password_option()
    def create_user(username, password):
        """
        Create user with admin rights.
        """

        user = User(username=username, admin=True)
        user.set_password(password)
        db.session.add(user)

        commit(db.session)

    @init_data.command("create-calendar")
    @click.confirmation_option(
            prompt='Are you sure you want to ERASE the calendar?'
            )
    def create_calendar():
        """
        Initialize empty calendar.

        This will erase all quests and answers from
        the calendar!!!

        All discovered days/answers will be erased
        as well!!!
        """

        Day.query.delete()
        DiscoveredDays.query.delete()

        commit(db.session)
        db.session.close()

        default_hour = time(hour=0, minute=0, second=0)

        db.session.add(Day(id=1, day_no=17, hour=default_hour))
        db.session.add(Day(id=2, day_no=2, hour=default_hour))
        db.session.add(Day(id=3, day_no=15, hour=default_hour))
        db.session.add(Day(id=4, day_no=8, hour=default_hour))
        db.session.add(Day(id=5, day_no=24, hour=default_hour))
        db.session.add(Day(id=6, day_no=9, hour=default_hour))
        db.session.add(Day(id=7, day_no=19, hour=default_hour))
        db.session.add(Day(id=8, day_no=6, hour=default_hour))
        db.session.add(Day(id=9, day_no=11, hour=default_hour))
        db.session.add(Day(id=10, day_no=22, hour=default_hour))
        db.session.add(Day(id=11, day_no=4, hour=default_hour))
        db.session.add(Day(id=12, day_no=14, hour=default_hour))
        db.session.add(Day(id=13, day_no=18, hour=default_hour))
        db.session.add(Day(id=14, day_no=5, hour=default_hour))
        db.session.add(Day(id=15, day_no=21, hour=default_hour))
        db.session.add(Day(id=16, day_no=7, hour=default_hour))
        db.session.add(Day(id=17, day_no=20, hour=default_hour))
        db.session.add(Day(id=18, day_no=13, hour=default_hour))
        db.session.add(Day(id=19, day_no=10, hour=default_hour))
        db.session.add(Day(id=20, day_no=1, hour=default_hour))
        db.session.add(Day(id=21, day_no=23, hour=default_hour))
        db.session.add(Day(id=22, day_no=16, hour=default_hour))
        db.session.add(Day(id=23, day_no=3, hour=default_hour))
        db.session.add(Day(id=24, day_no=12, hour=default_hour))

        commit(db.session)

    @init_data.command("load-help")
    @click.argument(
            'language',
            type=click.Choice(['pl', 'en'], case_sensitive=False)
            )
    @click.confirmation_option(
            prompt='Are you sure you want to replace contents of Help section?'
            )
    def load_help(language):
        """
        Load Help contents in <language> from file.

        This will erase current contents of Help section.
        """

        try:
            with open(os.path.join(
                        './advencal/help/',
                        'help.' + language + '.json'
                        ), 'r', encoding='utf8') as f:
                help_items = json.load(f)
        except OSError:
            click.echo('Error opening file. Data not changed.')
        else:
            Help.query.delete()
            commit(db.session)
            db.session.close()

            for item in help_items:
                db.session.add(Help(
                        order=item['order'],
                        title=item['title'],
                        body=item['body'],
                        admin=item['admin']
                        ))

            commit(db.session)

    @init_data.command("save-help")
    @click.argument(
            'language',
            type=click.Choice(['pl', 'en'], case_sensitive=False)
            )
    @click.confirmation_option(
            prompt='Are you sure you want to replace Help data file?'
            )
    def save_help(language):
        """
        Save Help contents in <language> to file.

        This will erase current contents of Help file.
        """

        help_contents = Help.query.all()
        commit(db.session)

        help_json = []

        for item in help_contents:
            help_json.append(
                {
                    'order': item.order,
                    'title': item.title,
                    'body': item.body,
                    'admin': item.admin
                }
            )

        try:
            with open(os.path.join(
                        './advencal/help/',
                        'help.' + language + '.json'
                        ), 'w', encoding='utf8') as f:
                json.dump(help_json, f, indent=4, ensure_ascii=False)
                f.write('\n')  # to stop complains about no newline at the EOF
        except OSError:
            click.echo('Error writing to file. Data not written.')

    app.cli.add_command(init_data)
