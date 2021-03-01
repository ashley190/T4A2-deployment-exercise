from main import db


class GroupMembers(db.Model):
    __tablename__ = "group_members"
    group_id = db.Column(
        db.Integer, db.ForeignKey("groups.id"), primary_key=True)
    profile_id = db.Column(
        db.Integer, db.ForeignKey("profile.id"), primary_key=True)
    admin = db.Column(db.Boolean)
    group = db.relationship("Groups", backref=db.backref(
        "profiles", lazy="dynamic"))
    profile = db.relationship(
        "Profile", backref=db.backref("group", lazy="dynamic"))
