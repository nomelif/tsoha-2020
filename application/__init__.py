# Tuodaan Flask käyttöön
from flask import Flask
app = Flask(__name__)

# Pistetään markdownit tulille

from flaskext.markdown import Markdown

Markdown(app)

# Tuodaan SQLAlchemy käyttöön
from flask_sqlalchemy import SQLAlchemy

import os

if os.environ.get("HEROKU"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///varkki.db"
    app.config["SQLALCHEMY_ECHO"] = True

# Luodaan db-olio, jota käytetään tietokannan käsittelyyn
db = SQLAlchemy(app)

# Luetaan kansiosta application tiedoston views sisältö
from application import views

from application.varkki import account
from application.varkki import entry
from application.varkki import post
from application.varkki import vote

from application.varkki.account import Account
from os import urandom
app.config["SECRET_KEY"] = urandom(32)

from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
login_manager.login_message = "Please login to use this functionality."

@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(user_id)

# Luodaan lopulta tarvittavat tietokantataulut
db.create_all()
