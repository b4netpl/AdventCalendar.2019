from advencal import db


discovered_days = db.Table(
        'discovered_days',
        db.Column('id', db.Integer, primary_key=True, autoincrement=True),
        db.Column('day_id', db.Integer, db.ForeignKey('day.id')),
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    days_discovered = db.relationship(
            'Day',
            secondary=discovered_days,
            lazy='subquery',
            backref=db.backref('users', lazy=True)
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day_no = db.Column(db.Integer, nullable=False)
    quest = db.Column(db.Text)
    quest_answer = db.Column(db.Text)
    hour = db.Column(db.Time, nullable=False, default="00:00:00")

    def __repr__(self):
        return '<Day {}>'.format(self.day_no)
