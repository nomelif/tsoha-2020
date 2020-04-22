from application import db

from application.varkki.hashtag_link import HashtagLink

class Hashtag(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140), nullable=False, unique=True)

    def __init__(self, text):
        self.text = text

def extract_tags(text):
    result = []
    for word in text.split(): # Split on all whitespace (seemingly zero-width joiners in emoji sequences are not impacted)
        
        # Some limits on what constitutes a valid hashtag

        if word.startswith("#") and len(word) > 1: # No explicit limit on hashtag length, will always be shorter than a message

            # Save the hashtags in a lower case form

            result.append(word.lower())

    return set(result)

def insert_tags(entry):
    tag_objects = []
    for tag in extract_tags(entry.text):

        # Ensure that a relevant hashtag exists

        if Hashtag.query.filter_by(text=tag).count() == 0:
            tag_objects.append(Hashtag(tag))
            db.session().add(tag_objects[-1])
        else:
            tag_objects.append(Hashtag.query.filter_by(text=tag).first())
    db.session.commit()
    for tag in tag_objects:
        db.session().add(HashtagLink(entry.id, tag.id))
    db.session.commit()

def delete_orphans():
    db.session.execute("DELETE FROM hashtag WHERE (SELECT COUNT(*) FROM hashtag_link WHERE hashtag_id = hashtag.id) = 0")
