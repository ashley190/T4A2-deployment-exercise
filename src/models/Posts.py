from main import db
from datetime import datetime
from models.Comments import Comments


class Posts(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    post = db.Column(db.Text, nullable=False)
    profile_id = db.Column(
        db.Integer, db.ForeignKey("profile.id"), nullable=False)
    group_id = db.Column(
        db.Integer, db.ForeignKey(
            "groups.id", ondelete="CASCADE"), nullable=False)
    comments = db.relationship(
        Comments, backref="post", lazy="dynamic",
        cascade="all, delete, delete-orphan", passive_deletes=True)


def __repr__(self):
    return f"Post: {self.id}"
