import os
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))

DB_USER = 'root'
DB_PASSWORD = ''
DB_HOST = 'localhost'
DB_NAME = 'donateapp'
SQLALCHEMY_DATABASE_URI = "mysql://{0}:{1}@{2}/{3}".\
    format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
DATABASE_QUERY_TIMEOUT = 0.5
WTF_CSRF_ENABLED = True
SECRET_KEY = str(uuid.uuid4())
HOSTNAME = "http://donateapp.com"

# email server
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = [os.environ.get('MAIL_ADMIN')]

#payment gateway info
PAYMENT_GW_API_KEY = os.environ.get("PAYMENT_GW_API_KEY")
PAYMENT_GW_AUTH_TOKEN = os.environ.get("PAYMENT_GW_AUTH_TOKEN")
PAYMENT_GW_SALT = os.environ.get("PAYMENT_GW_SALT")

#ADMIN
ADMIN_USERS_PER_PAGE = 5

