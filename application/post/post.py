from application import db

from .entry import Entry
from .vote import Vote
from .hashtag import insert_tags

import sqlalchemy

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

            # None becomes NULL (if post_id is None, that is) and NULL != x is FALSE for all x.

            elif db.session.execute("SELECT COUNT(*) FROM post WHERE parent_id =:reply AND (id != :post OR :post IS NULL)", {"reply":reply_id, "post":post_id}).fetchone()[0] > 4:
                post_valid = False
                error_message = "Viesti on vastaus jo lukkiutuneeseen viestiin"

            elif db.session.execute("SELECT COUNT(*) FROM post WHERE id = :reply AND parent_id IS NOT NULL", {"reply":reply_id}).fetchone()[0] != 0:
                post_valid = False
                error_message = "Vastausviestiin ei voi vastata"

            # Again, None becomes NULL. If post_id is None, it's not an edit and id = :post is false.
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
        insert_tags(e)
        return {"failure":False}
    else:
        result = {"failure":True, "error_message":error_message}
        result["votes"] = Vote._ensure_votes(account_id)
        result["entries"] = Entry._entries_for_votes(result["votes"])

        db.session.rollback()

        return result


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=True, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=True, index=True)

    account = db.relationship("Account", foreign_keys="Post.account_id")
    parent = db.relationship("Post", foreign_keys="Post.parent_id")

    def __init__(self, account_id, parent_id):
        self.account_id = account_id
        if parent_id != None:
            self.parent_id = parent_id

    def get_displayable_posts(tags):

        result = []

        sql_tmpl = """
WITH accepted_entry AS
    (
        SELECT text, timestamp, id, post_id FROM entry
        WHERE (SELECT COUNT(*) FROM vote WHERE
            upvote = true
            AND entry_id = entry.id) >= 2
    ), current_accepted_entry AS
    (
        SELECT text, timestamp, id, post_id, (SELECT parent_id FROM post WHERE post.id = post_id) as reply_id FROM accepted_entry
        WHERE accepted_entry.timestamp =
            (SELECT MAX(subquery.timestamp) FROM accepted_entry as subquery
                WHERE subquery.post_id = accepted_entry.post_id)
    ), hashtagged_post AS
    (
        SELECT post_id as id, (SELECT parent_id FROM post WHERE post.id = post_id) as parent_id
        FROM current_accepted_entry
        WHERE NOT :has_tags
              OR (SELECT COUNT(*) FROM hashtag_link WHERE
            entry_id = current_accepted_entry.id
            AND hashtag_id IN (SELECT hashtag.id
                              FROM hashtag
                              WHERE hashtag.text IN :tags)) > 0
    ), hashtagged_parent AS
    (
        SELECT DISTINCT COALESCE(parent_id, id, parent_id) as id
        FROM hashtagged_post
    ), timestamped_parent AS
    (
        SELECT id AS parent_id,
               (SELECT timestamp
               FROM current_accepted_entry
               WHERE post_id = hashtagged_parent.id) AS parent_timestamp
        FROM hashtagged_parent
    )

SELECT current_accepted_entry.text, current_accepted_entry.id, (SELECT account_id FROM post WHERE post.id = current_accepted_entry.post_id), timestamped_parent.parent_id, (SELECT current_accepted_entry.post_id = timestamped_parent.parent_id)
FROM timestamped_parent INNER JOIN current_accepted_entry
    ON current_accepted_entry.post_id = timestamped_parent.parent_id
       OR current_accepted_entry.reply_id = timestamped_parent.parent_id
    ORDER BY parent_timestamp DESC,
             parent_id DESC,
             current_accepted_entry.post_id = timestamped_parent.parent_id DESC,
             current_accepted_entry.timestamp DESC
        """
        params = {"tags": tags, "has_tags": len(tags) > 0}
        # SQLalchemy screws PostresSQL up if tags is an empty list
        if tags == []:
            params["tags"] = [""]
        t = sqlalchemy.text(sql_tmpl)
        t = t.bindparams(sqlalchemy.bindparam("tags", expanding=True))
        top_level = db.session.execute(t, params)
        for text, entry_id, account_id, post_id, is_top_level in top_level:
            result.append({"text": text, "entry_id":entry_id, "account_id":account_id, "post_id":post_id, "is_top_level":is_top_level})
        return result
