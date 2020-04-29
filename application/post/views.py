from application import app, db
from flask import render_template, request, redirect, url_for
from application.account import Account
from application.post import submit_post, Vote, delete_entry
from flask_login import login_required, current_user
import bleach

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

@app.route("/delete/<int:entry_id>")
@login_required
def delete(entry_id):
    delete_entry(entry_id, current_user.get_id())
    db.session.commit()
    return redirect(url_for("index"))
