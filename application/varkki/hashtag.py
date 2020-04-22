from application import db

class Hashtag(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140), nullable=False, unique=True)

    def __init__(self, text):
        self.text = text
