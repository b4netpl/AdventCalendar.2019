from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func
from advencal import db


class DiscoveredDays(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='days')
    day = db.relationship('Day', back_populates='users')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(
            db.String(64),
            index=True,
            unique=True,
            nullable=False
            )
    password = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    days = db.relationship('DiscoveredDays', back_populates='user')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_user(id):
        return User.query.get(int(id))

    def check_username(username):
        if (User.query.filter_by(username=username).scalar()):
            return True
        else:
            return False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day_no = db.Column(db.Integer, nullable=False)
    quest = db.Column(db.Text)
    quest_answer = db.Column(db.Text)
    hour = db.Column(db.Time, nullable=False, default="00:00:00")
    users = db.relationship('DiscoveredDays', back_populates='day')

    def __repr__(self):
        return '<Day {}>'.format(self.day_no)

    def get_day(id):
        return Day.query.get(int(id))


class Help(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<Help {}>'.format(self.title)

    def get_helpitem(id):
        return Help.query.get(int(id))

    def get_max_order(admin):
        return db.session.query(
                func.max(Help.order)
                ).filter_by(admin=admin).scalar()
