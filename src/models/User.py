from main import db
from models.Profile import Profile      # noqa: F401
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Users(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), unique=False, nullable=False)
    profile = db.relationship("Profile", uselist=False, backref="user")

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method="sha256"
        )

    def check_password(self, password):
        """Check password hash."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"User: {self.username}"
