from application import app, db
from flask import render_template, request
from application.varkki.models import Account

@app.route("/")
def index():
    return render_template("index.html", title="Värkki")

@app.route("/login")
def login():
    return render_template("login.html", title="Kirjaudu Värkkiin")

@app.route("/login", methods=["POST"])
def do_login():
    account_name = request.form.get("account")
    password = request.form.get("password")
    if request.form.get("create account") != None:
        account = Account(account_name, password)
        db.session().add(account)
        db.session().commit()
    print(request.form.get("account"))
    print(request.form.get("password"))
    print(request.form.get("create account"))
    return render_template("login.html", title="Kirjaudu Värkkiin")
