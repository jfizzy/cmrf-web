from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads
from config import config

bootstrap = Bootstrap()

mail = Mail()

moment = Moment()

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'basic' #Basic allows persistent sessions. Strong stops this.
login_manager.login_view = 'auth.login'
login_manager.refresh_view = 'auth.reauthenticate'
login_manager.needs_refresh_message = (
	u'As a security feature, we require that you reauthenticate to access this page.'
)
login_manager.needs_refresh_message_category = 'info'

documents = UploadSet('documents', set(['pdf']))
photos = UploadSet('photos', set(['png', 'jpg', 'jpe', 'jpeg', 'gif']))

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    configure_uploads(app, documents)
    configure_uploads(app, photos)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .cmrf import cmrf as cmrf_blueprint
    app.register_blueprint(cmrf_blueprint, url_prefix='/cmrf')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
