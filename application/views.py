from application import app
from flask import render_template, request, redirect, url_for
from application.account import Account
from application.varkki.post import Post, submit_post
from application.varkki.vote import Vote
from flask_login import login_required, current_user
import bleach

@app.route("/")
def index():
    if current_user.is_authenticated:
        account = Account.query.filter_by(id=current_user.get_id()).first()
        tags = []
        query = request.args.get("tag")
        if query != None:
            for tag in query.split():
                if not tag.startswith("#"):
                    tags.append("#" + tag)
                else:
                    tags.append(tag)
        return render_template("index.html", user_name=account.user_name, account_id=account.id, posts=Post.get_displayable_posts(tags), title="Värkki", index=True)
    else:
        return render_template("index-unlogged.html", title="Värkki (kirjautumaton)")

@app.route("/newpost", methods=["POST", "GET"])
@login_required # <- First SQL interaction, only reads
def newpost():

    account = Account.query.filter_by(id=current_user.get_id()).first() # <- Read only SQL

    display_page = False
    error_message = None
    post_content = ""

    # Figure out the available votes (for display if the page gets displayed or for reference if a vote is cast)

    options = []
    votes, entries = None, None
    edit = False

    if request.method == "GET": # Just return the blank page
        if request.args.get("post_id") != None:
            edit = True
        votes, entries = Vote.ensure_votes(account.id) # <- contains commit
        display_page=True
    else:
        result = submit_post(tuple([key[5:] for key in request.form.keys() if key.startswith("vote-") and request.form.get(key) == "on"]), account.id, request.form.get("message"), request.args.get("post_id"), request.args.get("parent_id")) # <- contains commit or rollback
        if result["failure"]:
            votes = result["votes"]
            entries = result["entries"]
            post_content = request.form.get("message")
            error_message = result["error_message"]
            display_page=True

    if display_page:
        for vote, entry in zip(votes, entries):
            options.append([vote.id, bleach.clean(entry.text)])
        return render_template("newpost.html", title="Uusi postaus", user_name=account.user_name, options=options, error_message=error_message, post_content=post_content, edit=edit)
    else: # Redirect to index
        return redirect(url_for("index"))
