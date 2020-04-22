from application import db
import time
import os

from application.varkki.entry import Entry, delete_entry

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

        # Delete rejected entries

        for entry_id in db.session.execute("SELECT id FROM entry WHERE (SELECT COUNT(*) FROM vote WHERE vote.entry_id = entry.id AND NOT vote.upvote) >= 2"):
            delete_entry(entry_id[0], None, True) # Also deletes hashtags and votes
        


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
