from main import db


class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    postcode = db.Column(db.Integer, nullable=False)
    suburb = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    profile_id = db.Column(
        db.Integer, db.ForeignKey("profile.id"), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=True)

    def __repr__(self):
        return f"Location: {self.id}"
