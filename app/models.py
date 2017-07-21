from . import db
from . import login_manager
from flask_login import UserMixin, AnonymousUserMixin
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

class Permission:
    MAKE_R = 0x01
    VIEW_R = 0x02
    ADD_ARTICLE = 0x04
    ALL_R = 0x08
    EDITING = 0x16
    USER_ACC = 0x32
    ADMINISTER = 0x80

class Role(db.Model):

    __tablename__ = 'ROLE'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User' : (Permission.MAKE_R |
                      Permission.VIEW_R, True),
            'Assistant' : (Permission.VIEW_R |
                           Permission.ADD_ARTICLE |
                           Permission.ALL_R, False),
            'LabAdmin' : (Permission.VIEW_R |
                          Permission.ADD_ARTICLE |
                          Permission.ALL_R |
                          Permission.EDITING |
                          Permission.USER_ACC, False),
            'Administrator': (0xff, False) #all permissions
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role=Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role [%s] - Permissions: [%s]>' % (self.name, bin(self.permissions))

class User(UserMixin, db.Model):

    __tablename__ = 'USER'

    UCID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    pw_hash = db.Column(db.String(160))
    email = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('ROLE.id'))
    email_conf = db.Column(db.Boolean, default=False)
    lab = db.Column(db.String(64), index=True)
    phone = db.Column(db.String(64))
    date_joined = db.Column(db.DateTime, default=datetime.datetime.now)

    @property
    def id(self):
        return self.UCID

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.pw_hash = generate_password_hash(password,method='pbkdf2:sha256:1500',salt_length=22)

    def verify_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role_id is None:
            if self.email == current_app.config['CMRF_ADMIN'] and self.email is not None:
                self.role_id = Role.query.filter_by(permissions=0xff).first().id
            if self.role_id is None:
                self.role_id = Role.query.filter_by(default=True).first().id

    def __repr__(self):
        return '<User %s %s>' % (self.first_name, self.last_name)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.email_conf = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration=604800):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.UCID}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_r_privileged(self):
        return self.can(Permission.ALL_R)

	def is_n_privileged(self):
		return self.can(Permission.ADD_ARTICLE)
		
    def is_u_privileged(self):
        return self.can(Permission.USER_ACC)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Report(db.Model):

    __tablename__ = "REPORT"

    ID = db.Column(db.Integer, primary_key=True, nullable=False)
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

    ID = db.Column(db.Integer, primary_key=True, nullable=False)
    submit_date = db.Column(db.DateTime, default=datetime.datetime.now)
    title = db.Column(db.String(64), nullable=False)
    no_samples = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(64), nullable=False)
    desc = db.Column(db.Text, nullable=True)
    ri_qehf = db.Column(db.Boolean, default=False)
    ri_qeb = db.Column(db.Boolean, default=False)
    ri_tsq = db.Column(db.Boolean, default=False)
    ri_unk = db.Column(db.Boolean, default=False)
    tm_ccm = db.Column(db.Boolean, default=False)
    tm_pep = db.Column(db.Boolean, default=False)
    tm_fa = db.Column(db.Boolean, default=False)
    tm_aa = db.Column(db.Boolean, default=False)
    tm_oth = db.Column(db.Boolean, default=False)
    tm_oth_txt = db.Column(db.String(20), default=None)
    assistance = db.Column(db.Boolean, default=False)
    RPT_ID = db.Column(db.Integer, db.ForeignKey("REPORT.ID"), nullable=True)
    RSC_ID = db.Column(db.Integer, db.ForeignKey("USER.UCID"), nullable=False)
    ADM_ID = db.Column(db.Integer, db.ForeignKey("USER.UCID"), nullable=True)

    def __init__(self, title, no_samples,
                 RSC_ID, tm, ri, assistance, status='Pending Approval',other_tm=None, desc=None):
        self.title = title
        self.no_samples = no_samples
        self.status = status
        if desc is not None:
            self.desc = desc
        if 0 in ri:
            self.ri_qehf = True
        if 1 in ri:
            self.ri_qeb = True
        if 2 in ri:
            self.ri_tsq = True
        if 3 in ri:
            self.ri_unk = True

        if 0 in tm:
            self.tm_ccm = True
        if 1 in tm:
            self.tm_pep = True
        if 2 in tm:
            self.tm_fa = True
        if 3 in tm:
            self.tm_aa = True
        if 4 in tm:
            self.tm_oth = True
            self.tm_oth_txt = other_tm

        if assistance == 0:
            self.assistance = True
        else:
            self.assistance = False

        self.RSC_ID = RSC_ID
        self.RPT_ID = None
        self.ADM_ID = None

    def __repr__(self):
        return '<Work Order - ID: [%s], Title: [%s], Status: [%s]>' % (
            self.ID, self.title, self.status)

    def get_required_instruments(self):
        return [self.ri_qehf, self.ri_qeb, self.ri_tsq, self.ri_unk]

    def get_target_metabolites(self):
        return [self.tm_pep, self.tm_fa, self.tm_aa, self.tm_unk]

    def has_report(self):
        return self.RPT_ID is not None

    def get_report(self):
        return self.RPT_ID

    def is_approved(self):
        return (status is 'Approved' and self.ADM_ID is not None)

class NewsItem(db.Model):
	
    __tablename__ = "NEWS_ITEM"
	
    ID = db.Column(db.Integer, primary_key=True, nullable=False)
    UCID = db.Column(db.Integer, db.ForeignKey("USER.UCID"), nullable=False)
    title = db.Column(db.String(64), nullable=False)
    submit_date = db.Column(db.DateTime, default=datetime.datetime.now)
    desc = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)
	
    def __init__(self, ucid, title, desc=None, url=None):
	self.UCID = ucid
	self.title = title
	if desc is not None:
	    self.desc = desc
	if url is not None:
	    self.url = url

    def __repr__(self):
	return '<News Item - ID: [%s], UCID: [%s], Title: [%s]>' % (self.ID, self.UCID, self.title)
		
		
class Publication(db.Model):
	
    __tablename__ = "PUBLICATION"

    ID = db.Column(db.Integer, primary_key=True, nullable=False)
    UCID = db.Column(db.Integer, db.ForeignKey("USER.UCID"), nullable=False)
    title = db.Column(db.Text, nullable=False)
    submit_date = db.Column(db.DateTime, default=datetime.datetime.now)
    desc = db.Column(db.Text, nullable=False)
    pdf_name = db.Column(db.Text, nullable=False)
    pdf_url = db.Column(db.Text, nullable=False)

    def __init__(self, ucid, title, desc, pdf_name, pdf_url):
	self.UCID = ucid
	self.title = title
	self.desc = desc
	self.pdf_name = pdf_name
        self.pdf_url = pdf_url
		
    def __repr__(self):
	return '<Publication - ID: [%s], UCID: [%s], Title: [%s]>' % (self.ID, self.UCID, self.title)
	
class Person(db.Model):
	
	__tablename__ = "PERSON"
	
	ID = db.Column(db.Integer, primary_key=True, nullable=False)
	UCID = db.Column(db.Integer, db.ForeignKey("USER.UCID"), nullable=False)
	submit_date = db.Column(db.DateTime, default=datetime.datetime.now)
	name = db.Column(db.String(64), nullable=False)
	title = db.Column(db.String(64), nullable=False)
	email = db.Column(db.String(64), nullable=True, default=None)
	photo_name = db.Column(db.Text, nullable=True, default=None)
	photo_url = db.Column(db.Text, nullable=True, default=None)
	
	def __init__(self, ucid, name, title, email=None, photo_name=None, photo_url=None):
		self.UCID = ucid
		self.name=name
		self.title=title
		self.email=email
		self.photo_name=photo_name
		self.photo_url=photo_url
		
	def __repr__(self):
		return '<Person - ID: [%s], UCID: [%s], Name: [%s]>' % (self.ID, self.UCID, self.name)
