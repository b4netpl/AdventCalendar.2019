from datetime import time
from advencal import app, db
from advencal.models import User, Day


@app.cli.command("init-db-data")
def init_db_data():
    """
    Seed db with test data.
    """

    user = User(username='test', admin=True)
    user.set_password('test')
    db.session.add(user)

    default_hour = time(hour=0, minute=0, second=0)

    db.session.add(Day(id=1, day_no=17, hour=default_hour))
    db.session.add(Day(
            id=2,
            day_no=2,
            quest='Ile to dwa dodać dwa?',
            quest_answer='cztery',
            hour=default_hour
            ))
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

    db.session.commit()
