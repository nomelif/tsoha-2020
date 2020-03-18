from application import app, db
from flask import render_template, request, redirect, url_for
from application.varkki.models import Account, Post, Entry, Vote
from flask_login import login_required, current_user, login_user, logout_user
import bcrypt
import sqlalchemy
import markdown
import bleach
import jinja2

@app.route("/")
def index():
    if current_user.is_authenticated:
        account = Account.query.filter_by(id=current_user.get_id()).first()
        return render_template("index.html", user_name=account.user_name, title="Värkki")
    else:
        return render_template("index-unlogged.html", title="Värkki (kirjautumaton)")

@app.route("/newpost", methods=["POST", "GET"])
@login_required
def newpost():

    account = Account.query.filter_by(id=current_user.get_id()).first()
    if request.method == "GET":
        options = []
        votes, entries = Vote.find_votes_for(account.id)
        for vote, entry in zip(votes, entries):
            #print(entry.text)
            #print(bleach.clean(entry.text))
            #print(markdown.markdown(bleach.clean(entry.text)))
            options.append([vote.id, bleach.clean(entry.text)])
        return render_template("newpost.html", title="Uusi postaus", user_name=account.user_name, options=options)
    else:
        if request.form.get("message") == None or request.form.get("message") == "":
            return render_template("newpost.html", title="Uusi postaus", user_name=account.user_name, error_message="Viesti ei voi olla tyhjä")
        elif len(request.form.get("message")) > 140:
            return render_template("newpost.html", title="Uusi postaus", user_name=account.user_name, error_message=f"Viestisi ylittää maksimipituuden ({len(request.form.get('message'))}/140)", post_content=request.form.get("message"))
        post = Post(account.id, None)
        db.session().add(post)
        db.session().commit()
        entry = Entry(post.id, request.form.get("message"))
        db.session().add(entry)
        db.session().commit()
        return redirect(url_for("index"))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

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
            if request.args.get("next") == None:
                return redirect(url_for("index"))
            else:
                return redirect(request.args.get("next"))
        except sqlalchemy.exc.IntegrityError:
            return render_template("login.html", title="Kirjaudu Värkkiin", error_message="Käyttäjätunnus on jo käytössä.", hide_login=True)
    else:
        account = Account.query.filter_by(user_name=request.form.get("account")).first()
        if account == None or password == None or not bcrypt.checkpw(password.encode("utf-8"), account.password_hash.encode("utf-8")):
            return render_template("login.html", title="Kirjaudu sisään", error_message="Käyttäjätunnus ja salasana eivät täsmää.", hide_signup=True)
        else:
            login_user(account)
            if request.args.get("next") == None:
                return redirect(url_for("index"))
            else:
                return redirect(request.args.get("next"))
