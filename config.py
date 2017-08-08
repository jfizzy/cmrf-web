import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    CMRF_MAIL_SUBJECT_PREFIX = '[CMRF]'
    CMRF_MAIL_SENDER = 'CMRF Admin <cmrfnoreply@gmail.com>'
    CMRF_ADMIN = os.environ.get('CMRF_ADMIN')
	
    CMRF_SLOW_DB_QUERY_TIME = 0.5
    
    UPLOADS_DEFAULT_DEST = './app/uploads'
    UPLOADS_DEFAULT_URL = 'http://localhost:5000/app/uploads/'

    UPLOADED_DOCUMENTS_DEST = './app/uploads/documents'
    UPLOADED_DOCUMENTS_URL = 'http://localhost:5000/app/uploads/documents/'
    
    UPLOADED_PHOTOS_DEST = './app/uploads/photos'
    UPLOADED_PHOTOS_URL = 'http://localhost:5000/app/uploads/photos/'

    ALLOWED_EXT_PHOTOS = set(['png', 'jpg', 'jpeg', 'gif'])
    ALLOWED_EXT_DOCUMENTS = set(['pdf'])

    RECAPTCHA_USE_SSL = True
    RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
    RECAPTCHA_TYPE = 'image'
    RECAPTCHA_SIZE = 'compact'
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') 

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the admins
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler=SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.CMRF_MAIL_SENDER,
            toaddrs=[cls.CMRF_ADMIN],
            subject=cls.CMRF_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

class HerokuConfig(ProductionConfig):
	SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))
	
	@classmethod
	def init_app(cls, app):
		ProductionConfig.init_app(app)
		
		# handle proxy server headers
		from werkzeug.contrib.fixers import ProxyFix
		app.wsgi_app = ProxyFix(app.wsgi_app)
		
		# log to stderr
		import logging
		from logging import StreamHandler
		file_handler = StreamHandler()
		file_handler.setLevel(logging.WARNING)
		app.logger.addHandler(file_handler)
	
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
	'heroku': HerokuConfig,
	
    'default': HerokuConfig
}
