from application import db
import bcrypt
import time
import os
from datetime import datetime

from .hashtag import delete_orphans

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False, index=True)
    text = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    post = db.relationship("Post", foreign_keys="Entry.post_id")
    child_votes = db.relationship("Vote", passive_deletes=True, backref="Entry")

    def __init__(self, post_id, text):
        self.post_id = post_id
        self.text = text
        self.timestamp = int(time.time())

    def _entries_for_votes(votes):
        entries = []
        for vote in votes:
            entries.append(Entry.query.filter_by(id=vote.entry_id).first())

        return entries

def delete_entry(entry_id, account_id, skip_account_check=False):
    if skip_account_check or db.session.execute("SELECT COUNT(*) FROM entry WHERE (SELECT post.account_id FROM post WHERE post.id = entry.post_id) = :deleter AND id = :entry", {"deleter":account_id, "entry":entry_id}).fetchone()[0] == 1:

        db.session.execute("DELETE FROM hashtag_link WHERE entry_id = :entry", {"entry": entry_id})
        delete_orphans()
        db.session.execute("DELETE FROM entry WHERE id = :entry", {"entry": entry_id})

        if not os.environ.get("HEROKU"):
            db.session.execute("DELETE FROM vote WHERE entry_id = :entry", {"entry": entry_id})
