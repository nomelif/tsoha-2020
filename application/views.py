from flask import Flask, render_template
from application import app

@app.route("/")
def index():
    return render_template("index.html", title="Värkki")

@app.route("/login")
def login():
    return render_template("login.html", title="Kirjaudu Värkkiin")
