from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func
from flask_login import UserMixin
from advencal import db, login


class DiscoveredDays(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='days')
    day = db.relationship('Day', back_populates='users')
    tenant = db.relationship('Tenant', back_populates='visits')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    username = db.Column(
            db.String(64),
            index=True,
            unique=True,
            nullable=False
            )
    password = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    days = db.relationship('DiscoveredDays', back_populates='user')
    tenant = db.relationship('Tenant', back_populates='users')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @staticmethod
    def get_user(id):
        return User.query.get(int(id))

    @staticmethod
    def exists(username):
        if (User.query.filter_by(username=username).scalar()):
            return True
        else:
            return False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login.user_loader
def load_user(id):
    return User.get_user(id)


class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    day_no = db.Column(db.Integer, nullable=False)
    quest = db.Column(db.Text)
    quest_answer = db.Column(db.Text)
    hour = db.Column(db.Time, nullable=False, default="00:00:00")
    users = db.relationship('DiscoveredDays', back_populates='day')
    tenant = db.relationship('Tenant', back_populates='days')

    def __repr__(self):
        return '<Day {}>'.format(self.day_no)

    @staticmethod
    def get_day(id):
        return Day.query.get(int(id))


class Help(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    tenant = db.relationship('Tenant', back_populates='helpitems')

    def __repr__(self):
        return '<Help {}>'.format(self.title)

    @staticmethod
    def get_helpitem(id):
        return Help.query.get(int(id))

    @staticmethod
    def get_max_order(admin):
        return db.session.query(
                func.max(Help.order)
                ).filter_by(admin=admin).scalar()


class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    visits = db.relationship('DiscoveredDays', back_populates='tenant')
    users = db.relationship('User', back_populates='tenant')
    days = db.relationship('Day', back_populates='tenant')
    helpitems = db.relationship('Help', back_populates='tenant')

    def __repr__(self):
        return '<Tenant {}>'.format(self.name)

    @staticmethod
    def get_tenant(id):
        return Tenant.query.get(int(id))

    @staticmethod
    def get_tenant_id(name):
        return Tenant.query.filter_by(name=name).scalar()
