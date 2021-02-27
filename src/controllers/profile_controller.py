from models.Profile import Profile
from models.ProfileImage import ProfileImage
from models.Locations import Location
from main import db
from flask import (current_app, Blueprint, render_template,
                   redirect, url_for, flash, request)
from flask_login import current_user, login_required
import boto3
import os
import requests
import json
from forms import (ProfileForm, ProfileImageUpload,
                   DeleteButton, SearchLocation, AddButton)

profile = Blueprint('profile', __name__, url_prefix="/web/profile")


def retrieve_profile():
    user_id = current_user.get_id()
    profile = Profile.query.filter_by(user_id=user_id).first()
    return user_id, profile


def retrieve_profile_picture(profile_image):
    s3 = boto3.client('s3')
    bucket = os.environ.get("AWS_S3_BUCKET")
    url = s3.generate_presigned_url('get_object', Params={
        "Bucket": bucket,
        "Key": f"profile_images/{profile_image.filename}"}, ExpiresIn=5)
    return url


@profile.route("/", methods=["GET", "POST"])
@login_required
def profile_page():
    user_id, profile = retrieve_profile()
    image = None
    locations = None

    if not profile:
        return redirect(url_for("profile.profile_name"))

    if profile:
        profile_image = ProfileImage.query.filter_by(
            profile_id=profile.id).first()
        if profile_image:
            image = retrieve_profile_picture(profile_image)
        locations = Location.query.filter_by(profile_id=profile.id).all()

    return render_template(
        "profile.html", profile=profile, image=image, locations=locations)


@profile.route("/profilename", methods=["GET", "POST"])
@login_required
def profile_name():
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
    user_id, profile = retrieve_profile()

    form = ProfileImageUpload()
    if form.validate_on_submit():
        image = form.image.data
        filename = f"{profile.id}-profile_image"
        bucket = boto3.resource("s3").Bucket(
            current_app.config["AWS_S3_BUCKET"])
        key = f"profile_images/{filename}"
        bucket.upload_fileobj(image, key)

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
    user_id, profile = retrieve_profile()

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
    form = SearchLocation()
    form2 = AddButton()

    if form.validate_on_submit():
        url = f"http://v0.postcodeapi.com.au/suburbs/{form.postcode.data}.json"
        response = requests.get(url)
        data = json.loads(response.text)
        return render_template(
            "locations.html", form=form, data=data, form2=form2)
    return render_template("locations.html", form=form)


@profile.route("/addlocation", methods=["POST"])
@login_required
def add_location():
    user_id, profile = retrieve_profile()
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
