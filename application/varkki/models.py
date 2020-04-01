from application import db
import bcrypt
import time
import os

def submit_post(votes_cast, account_id, message, post_id, reply_id = None):

    message_valid = True
    votes_current = True
    post_valid = True
    error_message = None

    # Check validity of message

    if message == None or message == "":
        message_valid = False
        error_message = "Viestin ei tule olla tyhjä"
    elif len(message) > 140:
        message_valid = False
        error_message = f"Viesti on liian pitkä ({len(message)} / 140 merkkiä)"


    # Check if new votes have appeared to fill the user's quota. If so, reload the page and force them to vote on them.

    if message_valid and len(Vote._potential_votes(account_id)) != 0:
        votes_current = True
        error_message = "Lisää äänestettävää on ilmestynyt"

    # Check if the new post is an edit. If so, is the post_id valid and belonging to the right user?

    if post_id != None:
        try:
            post_id = int(post_id)
        except:
            post_valid = False
            error_message = "Muokattava viesti epäkelpo"
        else:
            if db.session.execute("SELECT COUNT(*) FROM post WHERE id = :post AND account_id = :poster", {"post":post_id, "poster":account_id}).fetchone()[0] != 1:
                post_valid = False
                error_message = "Muokattava viesti ei kuulu sinulle"
    
    # Check if the new post is a reply. If so, are there a maximum of four (minus this) posts in reply to the parent and is the parent valid (actual post id, not itself a reply)?
    # Check that a user doesn't try to turn a post into a reply by editing it

    if reply_id != None:
        try:
            reply_id = int(reply_id)
        except:
            post_valid = False
            error_message = "Viesti on vastaus epäkelpoon viestiin"
        else:
            if db.session.execute("SELECT COUNT(*) FROM post WHERE id = :reply", {"reply":reply_id}).fetchone()[0] != 1:
                post_valid = False
                error_message = "Viesti on vastaus epäkelpoon viestiin"

            # None becomes NULL (if post_id is None, that is) and NULL != x for all x.

            elif db.session.execute("SELECT COUNT(*) FROM post WHERE parent_id =:reply AND id != :post", {"reply":reply_id, "post":post_id}).fetchone()[0] > 4:
                post_valid = False
                error_message = "Viesti on vastaus jo lukkiutuneeseen viestiin"

            elif db.session.execute("SELECT COUNT(*) FROM post WHERE id = :reply AND parent_id IS NOT NULL", {"reply":reply_id}).fetchone()[0] != 0:
                post_valid = False
                error_message = "Vastausviestiin ei voi vastata"

            # Again, None becomes NULL so if the message is not a reply, the condition is false
            # This check is to avoid someone editing a post into being a reply. (Has stupid consequences like potentially forming arbitrary trees of replies)

            elif db.session.execute("SELECT COUNT(*) FROM post WHERE id = :post AND parent_id IS NULL", {"post":post_id}).fetchone()[0] != 0:
                post_valid = False
                error_message = "Viestistä ei voi tehdä vastausviestiä"


    if not (message_valid and votes_current and post_valid):
        result = {"failure":True, "error_message":error_message}
        result["votes"] = Vote._ensure_votes(account_id)
        result["entries"] = Entry._entries_for_votes(result["votes"])
        db.session.commit()
        return result

    # If we are here, it means that we can proceed to try to vote and post

    vote_result = Vote._do_vote(account_id, votes_cast)

    if vote_result == None:

        if post_id == None:
            p = Post(account_id, reply_id)
            db.session.add(p)
            db.session.commit()
            post_id = p.id
        e = Entry(post_id, message)
        db.session.add(e)

        db.session.commit()
        return {"failure":False}
    else:
        result = {"failure":True, "error_message":error_message}
        result["votes"] = Vote._ensure_votes(account_id)
        result["entries"] = Entry._entries_for_votes(result["votes"])

        db.session.rollback()

        return result

class Vote(db.Model):

    # This seems unavoidable. Oof.

    id = db.Column(db.Integer, primary_key=True)
    
    entry_id = db.Column(db.Integer, db.ForeignKey("entry.id", ondelete="CASCADE"), nullable=False)
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

    # Tries to apply upvotes

    def _do_vote(account_id, upvotes):

        # Check if all the votes actually are for open votes the user has access to

        for vote in upvotes:
            if db.session().execute("SELECT COUNT(*) FROM vote WHERE vote.id = :vote AND vote.account_id = :voter", {"voter":account_id, "vote":vote}).first()[0] == 0:
                return "Kelvottomia ääniä"

        # Apply the upvotes

        for vote in upvotes:

            # Apply upvote

            db.session.execute("UPDATE vote SET upvote = TRUE WHERE vote.id = :vote", {"voter":account_id, "vote":vote})

        
        # Make NULLs into downvotes

        db.session.execute("UPDATE vote SET upvote = FALSE WHERE vote.account_id = :voter AND vote.upvote IS NULL", {"voter":account_id})

        # Anonymise closed votes (upvotes)

        db.session.execute("UPDATE vote SET account_id = NULL WHERE (SELECT COUNT(*) FROM vote as k WHERE k.upvote = TRUE AND k.entry_id = vote.entry_id GROUP BY k.entry_id) >= 2") 

        # Delete rejected entries (and via cascading, the relevant votes)

        db.session.execute("DELETE FROM entry WHERE (SELECT COUNT(*) FROM vote WHERE vote.entry_id = entry.id AND NOT vote.upvote) >= 2")

        # Delete votes that cascading didn't delete (looking at you, SQLite)

        if not os.environ.get("HEROKU"):
            db.session.execute("DELETE FROM vote WHERE (SELECT COUNT(*) FROM entry WHERE entry.id = entry_id) = 0")

        


    # Doesn't guarantee the maximal set of available votes, guaranteed to be read-only
    # Guaranteed not to return more than three if used in an otherwise valid transaction

    def lookup_votes_for(account_id):

        return Vote.query.filter_by(account_id=account_id, upvote=None).all()

    def ensure_votes(account_id):
        votes = Vote._ensure_votes(account_id)
        entries = Entry._entries_for_votes(votes)
        db.session.commit()
        return votes, entries

    # Returns votes that _ensure_votes would insert into the table for a user
    # Guaranteed not to write, returns transient ORM objects

    def _potential_votes(account_id):

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
      post.id = entry.post_id
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

  -- Don't generate votes on entries which have been resolved

  AND (
    SELECT
      COUNT(*)
    FROM
      vote
    WHERE
      vote.entry_id = entry.id
      AND vote.account_id IS NULL
  ) = 0

  LIMIT
    :needed

  """, {"poster":account_id, "needed":3-len(Vote.lookup_votes_for(account_id))})

        votes = []

        for row in generated:
            votes.append(Vote(row[0], account_id, None))

        return votes

    # Guarantees maximal set of available votes, if they have not yet been allocated, will update database (subsequent commit is needed)

    def _ensure_votes(account_id):

        votes = Vote.query.filter_by(account_id=account_id, upvote=None).all()

        for vote in Vote._potential_votes(account_id):
            votes.append(vote)
            db.session().add(votes[-1])

        return votes


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
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

    def delete_entry(entry_id, account_id):
        if db.session.execute("SELECT COUNT(*) FROM entry WHERE (SELECT post.account_id FROM post WHERE post.id = entry.post_id) = :deleter AND id = :entry", {"deleter":account_id, "entry":entry_id}).fetchone()[0] == 1:
            db.session.execute("DELETE FROM entry WHERE id = :entry", {"entry": entry_id})

            if not os.environ.get("HEROKU"):
                db.session.execute("DELETE FROM vote WHERE entry_id = :entry", {"entry": entry_id})

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=True)

    account = db.relationship("Account", foreign_keys="Post.account_id")
    parent = db.relationship("Post", foreign_keys="Post.parent_id")

    def __init__(self, account_id, parent_id):
        self.account_id = account_id
        if parent_id != None:
            self.parent_id = parent_id

    def get_displayable_posts():

        result = []

        top_level = db.session.execute("""
SELECT text, entry.id, post.account_id, post.id
FROM   post
       INNER JOIN entry
               ON post.id = entry.post_id
       INNER JOIN (SELECT post_id,
                          Max(timestamp) AS max_timestamp
                   FROM   entry
                   WHERE  (SELECT Count(*)
                           FROM   vote
                           WHERE  vote.entry_id = entry.id
                                  AND vote.upvote = true) >= 2
                   GROUP  BY post_id) AS pid_map
               ON post.id = pid_map.post_id
                  AND entry.timestamp = pid_map.max_timestamp
WHERE  post.parent_id IS NULL
ORDER  BY entry.timestamp DESC  
        """).fetchall()
        for text, entry_id, account_id, post_id in top_level:
            result.append({"text": text, "entry_id":entry_id, "account_id":account_id, "replies":[], "post_id":post_id})
            replies = db.session.execute("""
SELECT text, entry.id, post.account_id, post.id
FROM   post
       INNER JOIN entry
               ON post.id = entry.post_id
       INNER JOIN (SELECT post_id,
                          Max(timestamp) AS max_timestamp
                   FROM   entry
                   WHERE  (SELECT Count(*)
                           FROM   vote
                           WHERE  vote.entry_id = entry.id
                                  AND vote.upvote = true) >= 2
                   GROUP  BY post_id) AS pid_map
               ON post.id = pid_map.post_id
                  AND entry.timestamp = pid_map.max_timestamp
WHERE  post.parent_id = :parent
ORDER  BY entry.timestamp DESC  
        """, {"parent": post_id}).fetchall()
            for reply_text, reply_entry_id, reply_account_id, reply_post_id in replies:
                result[-1]["replies"].append({"text":reply_text, "entry_id":reply_entry_id, "account_id":reply_account_id, "post_id":reply_post_id})
        return result


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
    
    def update_account(account, new_user_name, new_password):

        # Check that there isn't already someone else with the given user name (ignore self if no name change happened)

        if db.session.execute("SELECT COUNT(*) FROM account WHERE user_name = :name AND NOT id = :id", {"name":new_user_name, "id":account}).first()[0] != 0:
            return "Käyttäjänimi on jo varattu"

        db.session.execute("UPDATE account SET user_name = :name WHERE id = :id", {"name":new_user_name, "id":account})
        if new_password != None:
            db.session.execute("UPDATE account SET password_hash = :hash WHERE id = :id", {"hash":bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"), "id":account})
        db.session.commit()

    def delete_user(account):

        # Hand-delete all the votes on posts by the user (PostgreSQL cascading should take care of this)

        if not os.environ.get("HEROKU"):
            db.session.execute("DELETE FROM vote WHERE vote.entry_id IN (SELECT entry.id FROM entry JOIN post on entry.post_id = post.id WHERE post.account_id = :account)", {"account": account})

        # Delete all entries

        db.session.execute("DELETE FROM entry WHERE :account IN (SELECT account_id FROM post WHERE post.id = entry.post_id)", {"account": account})        

        # Anonymise all posts

        db.session.execute("UPDATE post SET account_id = NULL WHERE account_id = :account", {"account": account})

        # Delete all votes

        db.session.execute("DELETE FROM vote WHERE vote.account_id = :account", {"account": account})

        # Physically delete the account

        db.session.execute("DELETE FROM account WHERE id = :account", {"account":account})

        # If this didn't blow up, good riddance

        db.session.commit()
