
from models.Profile import Profile
from models.ProfileImage import ProfileImage
from models.Locations import Location
from models.Test import Test
from main import db
from flask import (current_app, Blueprint, render_template,
                   redirect, url_for, flash, request)
from flask_login import current_user, login_required
from controllers.controller_helpers import Helpers
import boto3
from forms import (ProfileForm, ProfileImageUpload,
                   DeleteButton, SearchLocation, AddButton)

profile = Blueprint('profile', __name__, url_prefix="/web/profile")

@profile.route("/test", methods=["GET"])
@login_required
def test():
    tests = Test.get.all()
    return f"{tests}"


@profile.route("/", methods=["GET"])
@login_required
def profile_page():
    """
    User profile page

    Renders profile page
    """
    user_id, profile = Helpers.retrieve_profile()
    image = None
    locations = None

    if not profile:
        return redirect(url_for("profile.profile_name"))

    if profile:
        profile_image = ProfileImage.query.filter_by(
            profile_id=profile.id).first()
        if profile_image:
            image = Helpers.retrieve_profile_picture(profile_image)
        locations = Location.query.filter_by(profile_id=profile.id).all()

    return render_template(
        "profile.html", profile=profile, image=image, locations=locations)


@profile.route("/profilename", methods=["GET", "POST"])
@login_required
def profile_name():
    """
    Profile name page - for new users.

    GET requests renders profile name page with ProfileForm
    POST requests validate form and handles confirmation of new
    user's profile name.
    """
    user_id = current_user.get_id()
    form = ProfileForm()
    if form.validate_on_submit():
        new_profile = Profile(
            name=form.profile_name.data,
            user_id=user_id
        )
        db.session.add(new_profile)
        db.session.commit()
        flash("Profile name confirmed!")
        return redirect(url_for("profile.profile_page"))
    return render_template("profile_name.html", form=form)


@profile.route("/uploadimage", methods=["GET", "POST"])
@login_required
def profile_image():
    """
    Profile image upload page

    GET requests renders profile image upload page
    with options to upload and remove profile image.
    POST requests validates profile image upload form and handles
    profile picture upload to designated AWS S3 bucket
    """
    user_id, profile = Helpers.retrieve_profile()

    form = ProfileImageUpload()
    if form.validate_on_submit():
        image = form.image.data
        filename = f"{profile.id}-profile_image"
        bucket = boto3.resource("s3").Bucket(
            current_app.config["AWS_S3_BUCKET"])
        key = f"profile_images/{filename}"
        bucket.upload_fileobj(image, key)

        # creates database link to image filename if it doesn't already exist.
        if not profile.profile_image:
            new_image = ProfileImage()
            new_image.filename = filename
            profile.profile_image = new_image
            db.session.commit()
            flash("Image upload successful")
        return redirect(url_for("profile.profile_page"))
    delete = DeleteButton()
    return render_template("image_upload.html", form=form, delete=delete)


@profile.route("/deleteimage", methods=["POST"])
@login_required
def remove_image():
    """
    Handles removal of profile image from S3 bucket
    """
    user_id, profile = Helpers.retrieve_profile()

    delete = DeleteButton()
    if delete.validate_on_submit():
        if profile.profile_image:
            bucket = boto3.resource("s3").Bucket(
                current_app.config["AWS_S3_BUCKET"])
            filename = profile.profile_image.filename
            bucket.Object(f"profile_images/{filename}").delete()
            db.session.delete(profile.profile_image)
            db.session.commit()
            flash("Image removed")
        flash("Image not found")
    return redirect(url_for("profile.profile_page"))


@profile.route("/locationsearch", methods=["GET", "POST"])
@login_required
def profile_locations():
    """
    Location search page

    GET requests render search page starting with a postcode search option,
    followed by search results after postcode search completed.
    POST requests handles location search by postcode using an external
    API (postcodeAPI).
    """
    form = SearchLocation()
    form2 = AddButton()

    if form.validate_on_submit():
        data = Helpers.location_search(form.postcode.data)
        if not data:
            flash("No locations found. Try another postcode.")
        return render_template(
            "locations.html", form=form, data=data, form2=form2)
    return render_template("locations.html", form=form)


@profile.route("/addlocation", methods=["POST"])
@login_required
def add_location():
    """
    Handles logic for associating a selected location(returned from
    location search) to a user profile.
    """
    user_id, profile = Helpers.retrieve_profile()
    form = AddButton()

    if form.validate_on_submit():
        postcode = request.args["postcode"]
        suburb = request.args["suburb"]
        state = request.args["state"]

        profile_location = Location.query.filter_by(
            suburb=suburb, profile_id=profile.id).first()
        if not profile_location:
            new_location = Location()
            new_location.postcode = postcode
            new_location.suburb = suburb
            new_location.state = state
            new_location.profile_id = profile.id
            profile.locations.append(new_location)
            db.session.commit()
            flash("Suburb added!")
        elif profile_location:
            flash("Suburb already associated with your profile")
    return redirect(url_for("profile.profile_page"))
