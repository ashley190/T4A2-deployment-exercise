from main import db
from models.Locations import Location
# from models.Group_members import GroupMembers


class Groups(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=False)
    description = db.Column(db.Text, nullable=True, unique=False)
    location = db.relationship(Location, backref="group", lazy="dynamic")
    members = db.relationship("GroupMembers", backref="groups")

    def __repr__(self):
        return f"<Group: {self.name}>"
