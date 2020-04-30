from application import db
import bcrypt
import os
from datetime import datetime

from application.post import Entry, delete_entry, Post, Vote

def data_dump(account_id):
    data = {}
    data["account"] = Account.query.filter_by(id=account_id).first()
    
    data["posts"] = []
    for post in Post.query.filter_by(account_id=account_id).all():
        post_data = {"id": post.id, "parent_id":post.parent_id, "entries":[]}
        for entry in Entry.query.filter_by(post_id=post.id).all():

            post_data["entries"].append({"id":entry.id, "text":entry.text, "time":datetime.fromtimestamp(entry.timestamp).strftime("%H:%M:%S %d.%m.%Y"), "upvotes":Vote.query.filter_by(entry_id=entry.id, upvote=True).count(), "downvotes":Vote.query.filter_by(entry_id=entry.id, upvote=False).count()})
        data["posts"].append(post_data)

    data["upvotes"] = []
    data["downvotes"] = []
    data["nullvotes"] = []

    for vote in Vote.query.filter_by(account_id=account_id).all():
        vote_data = {"id":vote.id, "text":Entry.query.filter_by(id=vote.entry_id).first().text, "entry_id": vote.entry_id}
        if vote.upvote == True:
            data["upvotes"].append(vote_data)
        elif vote.upvote == False:
            data["downvotes"].append(vote_data)
        else:
            data["nullvotes"].append(vote_data)
    return data

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(60), nullable=False)

    def __init__(self, user_name, password):
        self.user_name = user_name

        # True for whatever was the current version on 17.3.2020:
        # It is known from bcrypt source that hashpw returns a string containing chars:
        # A-z0-9 and the litteral characters . / and $
        # IE. b64 with $ added and + replaced by . for some reason.
        # These are all ASCII characters and that guarantees that interpreting them as utf-8
        # will not split any bytes into two. We can store the result as a utf-8 varchar(60).

        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True
    
    def update_account(account, new_user_name, new_password):

        # Check that there isn't already someone else with the given user name (ignore self if no name change happened)

        if db.session.execute("SELECT COUNT(*) FROM account WHERE user_name = :name AND NOT id = :id", {"name":new_user_name, "id":account}).first()[0] != 0:
            return "Käyttäjänimi on jo varattu"

        db.session.execute("UPDATE account SET user_name = :name WHERE id = :id", {"name":new_user_name, "id":account})
        if new_password != None:
            db.session.execute("UPDATE account SET password_hash = :hash WHERE id = :id", {"hash":bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"), "id":account})
        db.session.commit()

    def delete_user(account):

        # Delete all entries

        for entry_id in db.session.execute("SELECT id FROM entry WHERE (SELECT account_id FROM post WHERE post.id = entry.post_id) = :account", {"account": account}):
            delete_entry(entry_id[0], account)

        # Anonymise all posts

        db.session.execute("UPDATE post SET account_id = NULL WHERE account_id = :account", {"account": account})

        # Delete all votes

        db.session.execute("DELETE FROM vote WHERE vote.account_id = :account", {"account": account})

        # Physically delete the account

        db.session.execute("DELETE FROM account WHERE id = :account", {"account":account})

        # If this didn't blow up, good riddance

        db.session.commit()
