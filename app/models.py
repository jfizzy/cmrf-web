from . import db
from . import login_manager
from flask_login import UserMixin
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    
    __tablename__ = 'USER'
    
    UCID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    pw_hash = db.Column(db.String(160))
    email = db.Column(db.String(64))
    email_conf = db.Column(db.Boolean)
    phone = db.Column(db.Integer)
    date_joined = db.Column(db.DateTime, default=datetime.datetime.now)

    @property
    def id(self):
        return self.UCID

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

class Admin(db.Model):

    __tablename__ = 'ADMIN'

    ID = db.Column(db.Integer, db.Sequence('admin_seq', start=0, increment=1), primary_key=True)
    UCID = db.Column(db.Integer, db.ForeignKey("USER.UCID"))

    def __init__(self, ucid):
        self.UCID = ucid

    def __repr__(self):
        return '<Admin %r>' % self.ID

class Researcher(db.Model):

    __tablename__ = 'RESEARCHER'

    ID = db.Column(db.Integer, db.Sequence('admin_seq', start=0, increment=1), primary_key=True)
    UCID = db.Column(db.Integer, db.ForeignKey("USER.UCID"))

    def __init__(self, ucid):
        self.UCID = ucid

    def __repr__(self):
        return '<Researcher %r>' % self.ID

class FundingAccount(db.Model):
    
    __tablename__ = 'FUNDING_ACCOUNT'

    ID = db.Column(db.Integer, db.Sequence('funding_account_seq', start=0, increment=1),
                   primary_key=True, nullable=False)
    acc_no = db.Column(db.String(64), index=True, nullable=False)
    acc_name = db.Column(db.String(64), nullable=False)
    acc_type = db.Column(db.String(64))
    RSC_ID = db.Column(db.Integer, db.ForeignKey("RESEARCHER.ID"))

    def __init__(self, acc_no, acc_name, acc_type, rsc_id):
        self.acc_no = acc_no
        self.acc_name = acc_name
        self.acc_type = acc_type
        self.rsc_id = rsc_id

    def __repr__(self):
        return '<Funding Account - Name: [%s], Account Number: [%s]>' % (self.acc_name, self.acc_no)

class Report(db.Model):
    
    __tablename__ = "REPORT"

    ID = db.Column(db.Integer, db.Sequence('report_sequence', start=0, increment=1), primary_key=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    balance = db.Column(db.Numeric(6,2))
    desc = db.Column(db.Text, nullable=True)
    file_loc = db.Column(db.String(64), nullable=True)
    
    def __init__(self, balance, woid, desc=None, file_loc=None):
        self.balance = balance
        if desc is not None:
            self.desc = desc
        if file_loc is not None:
            self.file_loc = file_loc
        self.WKO_ID = woid

    def __repr__(self):
        return '<Report - ID: [%s], Work Order ID: [%s], Date: [%s], File Location: [%s]>'% (
            self.ID, self.WKO_ID, self.date, self.file_loc)
        
        
    
class WorkOrder(db.Model):

    __tablename__ = "WORK_ORDER"

    ID = db.Column(db.Integer, db.Sequence('work_order_seq', start=0, increment=1),
                   primary_key=True, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    no_samples = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.Text, nullable=True)
    ri_qehf = db.Column(db.Boolean)
    ri_qeb = db.Column(db.Boolean)
    ri_tsq = db.Column(db.Boolean)
    ri_unk = db.Column(db.Boolean)
    tm_pep = db.Column(db.Boolean)
    tm_fa = db.Column(db.Boolean)
    tm_aa = db.Column(db.Boolean)
    tm_unk = db.Column(db.Boolean)
    RPT_ID = db.Column(db.Integer, db.ForeignKey("REPORT.ID"), nullable=True)
    RSC_ID = db.Column(db.Integer, db.ForeignKey("RESEARCHER.ID"), nullable=False)
    ADM_ID = db.Column(db.Integer, db.ForeignKey("ADMIN.ID"), nullable=True)
    
    def __init__(self, title, no_samples, ri_qehf, ri_qeb, ri_tsq, ri_unk, tm_pep, tm_fa,
                 tm_aa, tm_unk, RSC_ID, status='Pending', desc=None):
        self.title = title
        self.no_samples = no_samples
        self.status = status
        if desc is not None:
            self.desc = desc
        self.ri_qehf = ri_qehf
        self.ri_qeb = ri_qeb
        self.ri_tsq = ri_tsq
        self.ri_unk = ri_unk
        self.tm_pep = tm_pep
        self.tm_fa = tm_fa
        self.tm_aa = tm_aa
        self.tm_unk = tm_unk
        self.RPT_ID = None
        self.RSC_ID = RSC_ID
        self.ADM_ID = None

    def __repr__(self):
        return '<Work Order - ID: [%s], Title: [%s], Status: [%s]>' % (
            self.ID, self.title, self.status)

class LogEntry(db.Model):

    __tablename__ = "LOG_ENTRY"

    ID = db.Column(db.Integer, db.Sequence('log_entry_seq', start=0, increment=1),
                   primary_key=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    desc = db.Column(db.String(128))
    UCID = db.Column(db.Integer, db.ForeignKey("USER.UCID"), nullable=False)

    def __init__(self, ucid, desc=None):
        self.UCID = ucid
        if desc is not None:
            self.desc = desc

    def __repr__(self):
        return '<Log Entry - Entry ID: [%s], UCID: [%s], Timestamp: [%s], Description: [%s]>' % (
            self.ID, self.UCID, self.timestamp, self.desc)
