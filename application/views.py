from application import app, db
from flask import render_template, request, redirect, url_for
from application.varkki.models import Account
from flask_login import login_required, current_user, login_user, logout_user
import bcrypt

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
        account = Account(account_name, password)
        db.session().add(account)
        db.session().commit()
        login_user(account)
        return redirect(url_for("index"))
    else:
        account = Account.query.filter_by(user_name=request.form.get("account")).first()
        if account == None or password == None:
            return render_template("login.html", title="Kirjaudu sisään")
        elif bcrypt.checkpw(password.encode("utf-8"), account.password_hash):
            login_user(account)
            return redirect(url_for("index"))
        else:
            return render_template("login.html", title="Kirjaudu Värkkiin")
