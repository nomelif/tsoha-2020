from application import db
import bcrypt
import time

class Vote(db.Model):

    # This seems unavoidable. Oof.

    id = db.Column(db.Integer, primary_key=True)
    
    entry_id = db.Column(db.Integer, db.ForeignKey("entry.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=True)
    upvote = db.Column(db.Boolean, nullable=True)

    __table_args__ = (
        db.CheckConstraint("account_id IS NOT NULL OR upvote IS NOT NULL"),
    )

    def __init__(self, entry_id, account_id, upvote):
        if entry_id != None:
            self.entry_id = entry_id
        if account_id != None:
            self.account_id = account_id
        if upvote != None:
            self.upvote = upvote

    # Class method

    def find_votes_for(account_id):

        # Find votes that have already been allocated to the given user and with null upvote
        # There should never be more than three

        votes = Vote.query.filter_by(account_id=account_id, upvote=None).all()

        # Fish unreviewed entries

        generated = db.session().execute("""
SELECT
  id
FROM
  entry
WHERE

  -- Don't generate votes on self posts

  (
    SELECT
      post.account_id
    FROM
      post
    WHERE
      post.id = entry.id
  ) != :poster

  -- Don't generate votes if one has been allocated

  AND (
    SELECT 
      COUNT(*)
    FROM 
      vote
    where 
      vote.entry_id = entry.id
      AND vote.account_id = :poster
  ) = 0

  -- Don't generate votes on entries which have been "sold out"

  AND (
    SELECT 
      COUNT(*)
    FROM 
      vote
    where 
      vote.entry_id = entry.id
  ) < 3
  LIMIT
    :needed

  """, {"poster":account_id, "needed":3-len(votes)})

        new_votes = []

        for row in generated:
            new_votes.append(Vote(row[0], account_id, None))
            db.session().add(new_votes[-1])
        db.session().commit()

        votes.extend(new_votes)

        # By now we have as many votes as are available, find the texts of the associated entries

        entries = []
        for vote in votes:
            entries.append(Entry.query.filter_by(id=vote.entry_id).first())

        return votes, entries


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
