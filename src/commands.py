from main import db
from flask import Blueprint


db_commands = Blueprint("db-custom", __name__)


def retrieve_suburb():
    """Retrieve suburb from Postcode API from randomly generated
    postcode by Faker"""
    from controllers.controller_helpers import Helpers
    from faker import Faker
    faker = Faker(["en_AU"])

    postcode = faker.postcode()
    return Helpers.location_search(postcode)


def seed_location(locations):
    """Get at least 5 seed locations using retrieve_suburb function"""
    while len(locations) < 5:
        location = retrieve_suburb()
        while not location:
            location = retrieve_suburb()
            if location:
                locations.append(location[0])
    return locations


@db_commands.cli.command("create")
def create_db():
    """Custom flask command to create all database tables"""
    db.create_all()
    print("Tables created")


@db_commands.cli.command("drop")
def drop_db():
    """Custom flask command to drop all database tables"""
    db.drop_all()
    db.engine.execute("DROP TABLE IF EXISTS alembic_version;")
    print("Tables deleted")


@db_commands.cli.command("seed")
def seed_db():
    """Custom flask command to seed database tables"""
    from models.User import Users
    from models.Profile import Profile
    from models.ProfileImage import ProfileImage
    from models.Locations import Location
    from models.Groups import Groups
    from models.Group_members import GroupMembers
    from models.Posts import Posts
    from models.Comments import Comments
    from faker import Faker
    import random

    # initialise function level variables
    faker = Faker()
    users = []
    profile_locations = {}

    for i in range(1, 6):
        """Seed users table with 5 users and password("123456")."""
        user = Users()
        user.username = f"tester{i}"
        user.set_password("123456")
        db.session.add(user)
        users.append(user)
    db.session.commit()

    for i in range(1, 5):
        """Creates 4 profile with tester5 having no profile,
        each profile has 1 profile image stored on AWS S3 bucket,
        each profile has 5 random locations associated with it.
        """
        profile = Profile()
        profile.name = faker.first_name()
        profile.user_id = i
        profile_locations[i] = []
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
            profile_locations[i].append(new_location)
    db.session.commit()

    for profile in Profile.query.all():
        """Seed groups table with 8 groups each with each profile as group admin
        for two groups; group location picked at random from list of locations
        associated with admin profile"""

        entities = ("schools", "cafes")
        group_entity = random.choice(entities)
        locations = profile_locations[profile.id]

        for i in range(1, 3):
            location = random.choice(locations)
            locations.remove(location)

            group = Groups()
            group.name = f"{location.suburb} {group_entity}"
            group.description = f"A group for {group_entity} in {location.suburb}, {location.state}"    # noqa: E501

            gp_location = Location()
            gp_location.postcode = location.postcode
            gp_location.suburb = location.suburb
            gp_location.state = location.state
            group.location.append(gp_location)

            GroupMembers(group=group, profile_id=profile.id, admin=True)
            db.session.add(group, gp_location)
    db.session.commit()

    for profile in Profile.query.all():
        """Add two locations to each profile not currently associated with the profile
        and not associated with locations of any groups the profile
        is an admin of to test group recommendation functionality"""
        profile_postcodes = Location.query.with_entities(
            Location.postcode).filter_by(profile_id=profile.id).all()
        non_group_locations = GroupMembers.query.with_entities(
            Location.postcode, Location.suburb, Location.state).select_from(
                GroupMembers).join(Groups).join(Location).filter(
                    GroupMembers.profile_id != profile.id).all()
        available_locations = []
        for location in non_group_locations:
            if location.postcode not in profile_postcodes:
                available_locations.append(location)
        for i in range(1, 3):
            selected_location = random.choice(available_locations)
            available_locations.remove(selected_location)

            add_location = Location()
            add_location.postcode = selected_location.postcode
            add_location.suburb = selected_location.suburb
            add_location.state = selected_location.state
            add_location.profile_id = profile.id
            profile.locations.append(add_location)
            db.session.add(add_location)
    db.session.commit()

    # seed non admin group members for each group
    profile_ids = (4, 3, 2, 1)
    group_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    for num in profile_ids:
        for i in range(1, 3):
            profile = Profile.query.get(num)
            group_id = group_ids.pop(0)
            new_member = GroupMembers()
            new_member.profile_id = num
            new_member.group_id = group_id
            new_member.admin = False
            profile.groups.append(new_member)
    db.session.commit()

    # seed 1 post each in groups 1 and 3
    ids = [1, 3]
    for num in ids:
        profile = Profile.query.get(num)
        group = Groups.query.get(num)
        new_post = Posts()
        new_post.post = faker.sentence()
        new_post.profile_id = num
        new_post.group_id = num
        profile.posts.append(new_post)
        group.posts.append(new_post)
    db.session.commit()

    # seed comment for post 1
    post = Posts.query.get(1)
    profile = Profile.query.get(4)
    new_comment = Comments()
    new_comment.comment = faker.sentence()
    new_comment.post_id = post.id
    new_comment.profile_id = profile.id
    post.comments.append(new_comment)
    profile.comments.append(new_comment)
    db.session.commit()

    print("Test database seeded")
