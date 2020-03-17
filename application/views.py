from application import app, db
from flask import render_template, request, redirect, url_for
from application.varkki.models import Account
from flask_login import login_required, current_user, login_user, logout_user
import bcrypt
import sqlalchemy

@app.route("/")
def index():
    if current_user.is_authenticated:
        account = Account.query.filter_by(id=current_user.get_id()).first()
        return render_template("index.html", user_name=account.user_name, title="Värkki")
    else:
        return render_template("index-unlogged.html", title="Värkki (kirjautumaton)")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/login", methods=["POST", "GET"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("login.html", title="Kirjaudu Värkkiin")

    account_name = request.form.get("account")
    password = request.form.get("password")
    if request.form.get("create account") != None:
        if account_name == None or password == None:
            return render_template("login.html", title="Kirjaudu Värkkiin", error_message="Käyttäjätunnuksen ja salasanan on saatava arvo.", hide_login=True)
        if len(password) < 8:
            return render_template("login.html", title="Kirjaudu Värkkiin", error_message="Salasanan kuuluu olla vähintään kahdeksan merkin pituinen.", hide_login=True)
        if len(account_name) == 0:
            return render_template("login.html", title="Kirjaudu Värkkiin", error_message="Käyttäjätunnus ei saa olla tyhjä.", hide_login = True)
        if len(account_name) > 20:
            return render_template("login.html", title="Kirjaudu Värkkiin", error_message="Käyttäjätunnukselle on 20 merkin pituusraja.", hide_login=True)
        try:
            account = Account(account_name, password)
            db.session().add(account)
            db.session().commit()
            login_user(account)
            return redirect(url_for("index"))
        except sqlalchemy.exc.IntegrityError:
            return render_template("login.html", title="Kirjaudu Värkkiin", error_message="Käyttäjätunnus on jo käytössä.", hide_login=True)
    else:
        account = Account.query.filter_by(user_name=request.form.get("account")).first()
        if account == None or password == None or not bcrypt.checkpw(password.encode("utf-8"), account.password_hash.encode("utf-8")):
            return render_template("login.html", title="Kirjaudu sisään", error_message="Käyttäjätunnus ja salasana eivät täsmää.", hide_signup=True)
        else:
            login_user(account)
            return redirect(url_for("index"))
