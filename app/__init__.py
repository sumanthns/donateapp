from config import PAYMENT_GW_API_KEY, PAYMENT_GW_AUTH_TOKEN
from flask import Flask

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_admin import Admin
from flask_mail import Mail
from instamojo import Instamojo


app = Flask(__name__)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
app.config.from_object('config')
db = SQLAlchemy(app)
mail = Mail(app)
payment_gateway_api = Instamojo(api_key=PAYMENT_GW_API_KEY,
                                auth_token=PAYMENT_GW_AUTH_TOKEN)

from app.admin.views.my_admin import MyAdmin

admin = Admin(app, index_view=MyAdmin(url='/admin', name='Admin Home'))

from app import views, models

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler('tmp/donateapp.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('donateapp startup')