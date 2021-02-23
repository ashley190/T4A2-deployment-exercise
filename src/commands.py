from main import db
from flask import Blueprint


db_commands = Blueprint("db-custom", __name__)


@db_commands.cli.command("create")
def create_db():
    db.create_all()
    print("Tables created")


@db_commands.cli.command("drop")
def drop_db():
    db.drop_all()
    print("Tables dropped")


@db_commands.cli.command("seed")
def seed_db():
    from models.User import Users
    from models.Profile import Profile
    from faker import Faker
    import random

    faker = Faker()
    users = []

    for i in range(1, 6):
        user = Users()
        user.username = f"tester{i}"
        user.set_password("123456")
        db.session.add(user)
        users.append(user)

    db.session.commit()
    print("User table seeded")

    for i in range(10):
        profile = Profile()
        profile.name = faker.first_name()
        profile.user_id = random.choice(users).id
        db.session.add(profile)

    db.session.commit()
    print("Profile table seeded")
