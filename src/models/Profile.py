from main import db


class Profile(db.Model):
    __tablename__ = "profile"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)

    def __repr__(self):
        return f"Profile: {self.name}"
