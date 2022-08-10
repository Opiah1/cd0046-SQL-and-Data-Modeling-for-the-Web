import os

from flask_wtf import CsrfProtect

csrf = CsrfProtect()
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SESSION_COOKIE_SECURE = True
# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI ='postgresql://postgres:opiah@localhost:5432/fyurr'
