from models.Profile import Profile
from main import db
from schemas.ProfileSchema import profile_schema
from flask import Blueprint, request, jsonify
profile = Blueprint('profile', __name__, url_prefix="/profile")


@profile.route("/", methods=["GET"])
def profile_page():
    profile = Profile.query.get(1)
    return jsonify(profile_schema.dump(profile))


@profile.route("/", methods=["POST"])
def create_profile():
    profile = profile_schema.load(request.json)

    new_profile = Profile()
    new_profile.name = profile["name"]

    db.session.add(new_profile)
    db.session.commit()

    return jsonify(profile_schema.dump(new_profile))
