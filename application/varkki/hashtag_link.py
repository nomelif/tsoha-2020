from application import db
import time
import os

class HashtagLink(db.Model):

    # This seems unavoidable. Oof.

    id = db.Column(db.Integer, primary_key=True)
    
    entry_id = db.Column(db.Integer, db.ForeignKey("entry.id", ondelete="CASCADE"), nullable=False)
    hashtag_id = db.Column(db.Integer, db.ForeignKey("hashtag.id", ondelete="CASCADE"), nullable=False)

    def __init__(self, entry_id, hashtag_id):
        self.entry_id = entry_id
        self.hashtag_id = hashtag_id

