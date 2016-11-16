import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Km!Z6376=wq&X17qcPrJdMrk#xA?Z!ff2=g+a&_$'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    MAIL_SERVER = 'mail.lewisresearchgroup.org'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'no-reply@lewisresearchgroup.org'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    CMRF_MAIL_SUBJECT_PREFIX = '[Calgary Metabolomic Research Facility]'
    CMRF_MAIL_SENDER = 'CMRF Admin <no-reply@lewisresearchgroup.org>'
    CMRF_ADMIN = os.environ.get('CMRF_ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
