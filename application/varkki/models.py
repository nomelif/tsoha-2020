from application import db
import bcrypt

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
