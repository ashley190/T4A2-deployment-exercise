from main import db
from flask import Blueprint


db_commands = Blueprint("db-custom", __name__)


def retrieve_suburb():
    import requests
    import json
    from faker import Faker
    faker = Faker(["en_AU"])

    postcode = faker.postcode()
    url = f"http://v0.postcodeapi.com.au/suburbs/{postcode}.json"
    response = requests.get(url)
    data = json.loads(response.text)
    return data


def seed_location(locations):
    while len(locations) < 3:
        location = retrieve_suburb()
        while not location:
            location = retrieve_suburb()
            if location:
                locations.append(location[0])
    return locations


@db_commands.cli.command("create")
def create_db():
    db.create_all()
    print("Tables created")


@db_commands.cli.command("drop")
def drop_db():
    db.drop_all()
    db.engine.execute("DROP TABLE IF EXISTS alembic_version;")
    print("Tables deleted")


@db_commands.cli.command("seed")
def seed_db():
    from models.User import Users
    from models.Profile import Profile
    from models.ProfileImage import ProfileImage
    from models.Locations import Location
    from faker import Faker

    faker = Faker()
    users = []

    for i in range(1, 6):
        user = Users()
        user.username = f"tester{i}"
        user.set_password("123456")
        db.session.add(user)
        users.append(user)

    for i in range(1, 5):
        profile = Profile()
        profile.name = faker.first_name()
        profile.user_id = i
        db.session.add(profile)

        image = ProfileImage()
        image.filename = f"{i}-profile_image"
        profile.profile_image = image

        locations = []
        seed_location(locations)

        for location in locations:
            new_location = Location()
            new_location.postcode = location["postcode"]
            new_location.suburb = location["name"]
            new_location.state = location["state"]["abbreviation"]
            new_location.profile_id = profile.id
            profile.locations.append(new_location)

    db.session.commit()

    print("Test database seeded")
