from application import db

class Hashtag(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(20), nullable=False)

    def __init__(self, text):
        seld.text = text
