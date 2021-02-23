from main import db
from models.User import Users


class Profile(db.Model):
    __tablename__ = "profile"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship(Users)

    def __repr__(self):
        return f"Profile: {self.name}"
