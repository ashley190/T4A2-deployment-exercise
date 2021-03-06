from main import db
from models.Locations import Location
from models.Posts import Posts


class Groups(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=False)
    description = db.Column(db.Text, nullable=True, unique=False)
    location = db.relationship(
        Location, backref="group", lazy="dynamic",
        cascade="all, delete, delete-orphan", passive_deletes=True)
    members = db.relationship(
        "GroupMembers", backref="groups",
        cascade="all, delete, delete-orphan", passive_deletes=True)
    posts = db.relationship(
        Posts, backref="group", lazy="dynamic",
        cascade="all, delete, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"Group: {self.id}"
