from main import db


class Test(db.Model):
    __tablename__ = "test"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    test = db.Boolean()

    def __repr__(self):
        return f"Test: {self.id}"
