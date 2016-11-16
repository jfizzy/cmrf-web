from . import db
from flask_login import UserMixin
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'USER'
    UCID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    pw_hash = db.Column(db.String(160))
    email = db.Column(db.String(64))
    phone = db.Column(db.Integer)
    date_joined = db.Column(db.DateTime, default=datetime.datetime.now)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.pw_hash = generate_password_hash(password,method='pbkdf2:sha1:1500',salt_length=22)

    def verify_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def __init__(self, ucid, fname, lname, pw, email, phone=None):
        self.UCID = ucid
        self.first_name = fname
        self.last_name = lname
        self.password = pw
        self.email = email
        if phone is not None:
            self.phone = phone

    def __repr__(self):
        return '<User %s %s>' % (self.first_name, self.last_name)

class Admin(UserMixin, db.Model):
    __tablename__ = 'ADMIN'
    ID = db.Column(db.Integer, db.Sequence('admin_seq', start=0, increment=1), primary_key=True)
    UCID = db.Column(db.Integer, db.ForeignKey("USER.UCID"))

    def __init__(self, ucid):
        self.UCID = ucid

    def __repr__(self):
        return '<Admin %r>' % self.ID

class Researcher(UserMixin, db.Model):
    __tablename__ = 'RESEARCHER'
    ID = db.Column(db.Integer, db.Sequence('admin_seq', start=0, increment=1), primary_key=True)
    UCID = db.Column(db.Integer, db.ForeignKey("USER.UCID"))

    def __init__(self, ucid):
        self.UCID = ucid

    def __repr__(self):
        return '<Researcher %r>' % self.ID
