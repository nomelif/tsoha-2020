from application import app, db
from flask import render_template, request, redirect, url_for, make_response
from . import models
from flask_login import login_required, current_user, login_user, logout_user
import bcrypt
import sqlalchemy

def validateUserName(user_name):
    ok = True
    error_message = ""
    if user_name == None or len(user_name) == 0:
        ok = False
        error_message = "Käyttäjänimi ei saa olla tyhjä"
    elif user_name.strip() != user_name: # Slightly stronger than the JS validation, affects tabs and newlines
        ok = False
        error_message = "Käyttäjänimi ei voi alkaa tai loppua välillä."
    elif len(user_name) > 20:
        ok = False
        error_message = "Käyttäjätunnukselle on 20 merkin pituusraja."
    return (ok, error_message)

def validatePassword(password, acceptNone = False):
    if acceptNone and password == None:
        return (True, "")
    if password == None or len(password) < 8:
        return (False, "Salasanalla pituudella on kahdeksan merkin alaraja")
    return (True, "")

@app.route("/downloadData")
@login_required
def downloadData():
    data = models.data_dump(current_user.get_id())
    response = make_response(render_template("datadump.html", data=data), 200)
    response.mimetype = "text/plain"
    return response

@app.route("/deleteUser")
@login_required
def deleteUser():
    account_id = current_user.get_id()
    logout_user()
    models.Account.delete_user(account_id)
    return redirect(url_for("index"))

@app.route("/updateUser", methods=["POST", "GET"])
@login_required
def updateUser():
    if request.method == "GET":
        return render_template("edit.html", title="Muokkaa käyttäjää", account=models.Account.query.filter_by(id=current_user.get_id()).first().user_name)
    else:
        new_user_name = request.form.get("account")
        new_password = request.form.get("password")
        ok = True
        error_message = ""

        # Parse Noney values as None = no change to password

        if new_password == "":
            new_password = None

        if not validatePassword(new_password, True)[0]:
            ok = False
            error_message = validatePassword(new_password, True)[1]
        elif not validateUserName(new_user_name)[0]:
            ok = False
            error_message = validateUserName(new_user_name)[1]

        if ok:
            result = models.Account.update_account(current_user.get_id(), new_user_name, new_password)
            if result:
                return render_template("edit.html", title="Muokkaa käyttäjää", error_message=result)
            else:
                return redirect(url_for("index"))
        else:
            return render_template("edit.html", title="Muokkaa käyttäjää", error_message=error_message)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/newaccount", methods=["POST", "GET"])
def newaccount():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("newaccount.html", title="Luo tunnus")

    account_name = request.form.get("account")
    password = request.form.get("password")

    ok = True
    error_message = ""
    if not validateUserName(account_name)[0]:
        ok = False
        error_message = validateUserName(account_name)[1]
    elif not validatePassword(password)[0]:
        ok = False
        error_message = validatePassword(password)[1]
    if ok:
        try:
            account = models.Account(account_name, password)
            db.session().add(account)
            db.session().commit()
            login_user(account)
            return redirect(url_for("index"))
        except sqlalchemy.exc.IntegrityError:
            ok = False
            error_message = "Käyttäjätunnus on jo käytössä"
    if not ok:
        return render_template("newaccount.html", title="Kirjaudu Värkkiin", error_message=error_message)

@app.route("/login", methods=["POST", "GET"])
def login():

    if current_user.is_authenticated:
        if request.args.get("next") == None:
            return redirect(url_for("index"))
        else:
            return redirect(request.args.get("next"))

    if request.method == "GET":
        return render_template("login.html", title="Kirjaudu Värkkiin")

    account_name = request.form.get("account")
    password = request.form.get("password")
    account = models.Account.query.filter_by(user_name=request.form.get("account")).first()
    if account == None or password == None or not bcrypt.checkpw(password.encode("utf-8"), account.password_hash.encode("utf-8")):
        return render_template("login.html", title="Kirjaudu sisään", error_message="Käyttäjätunnus ja salasana eivät täsmää.")
    else:
        login_user(account)
        if request.args.get("next") == None:
            return redirect(url_for("index"))
        else:
            return redirect(request.args.get("next"))
