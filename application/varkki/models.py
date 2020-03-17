from application import db
import bcrypt
import time

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    text = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    post = db.relationship("Post", foreign_keys="Entry.post_id")

    def __init__(self, post_id, text):
        self.post_id = post_id
        self.text = text
        self.timestamp = int(time.time())

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=True)

    account = db.relationship("Account", foreign_keys="Post.account_id")
    parent = db.relationship("Post", foreign_keys="Post.parent_id")

    def __init__(self, account_id, parent):
        self.account_id = account_id
        if parent != None:
            self.parent = parent

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), nullable=False, unique=True)
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
