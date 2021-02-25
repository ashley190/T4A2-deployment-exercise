from models.Profile import Profile
from models.ProfileImage import ProfileImage
from main import db
from schemas.ProfileSchema import profile_schema
from schemas.ProfileImageSchema import profile_image_schema
from flask import current_app, Blueprint, request, jsonify, render_template, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from pathlib import Path
import boto3
from forms import ProfileForm

profile = Blueprint('profile', __name__, url_prefix="/web/profile")


def retrieve_profile():
    user_id = current_user.get_id()
    profile = Profile.query.filter_by(user_id=user_id).first()
    return user_id, profile


@profile.route("/", methods=["GET", "POST"])
@login_required
def profile_page():
    user_id, profile = retrieve_profile()
    
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
    return render_template(
        "profile.html", profile=profile, form=form)


@profile.route("/image", methods=["POST"])
# @login_required
def profile_image():
    user_id = "1"
    profile = Profile.query.filter_by(user_id=user_id).first()

    # user_id, profile = retrieve_profile()
    # profile = Profile.query.filter_by(user_id=user_id).first()

    if "image" not in request.files:
        return abort(400, description="No image")
    
    image = request.files["image"]

    if Path(image.filename).suffix not in [".jpg", ".png", ".gif"]:
        return abort(400, description="Invalid file type")
    
    filename=f"{profile.id}.profile_image{Path(image.filename).suffix}"
    bucket = boto3.resource("s3").Bucket(current_app.config["AWS_S3_BUCKET"])
    key = f"profile_images/{filename}"
    bucket.upload_fileobj(image, key)

    if not profile.profile_image:
        new_image = ProfileImage()
        new_image.filename = filename
        profile.profile_image = new_image
        db.session.commit()

    return ("", 200)