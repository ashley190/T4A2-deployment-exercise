from models.Profile import Profile
from main import db
from schemas.ProfileSchema import profile_schema
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from forms import ProfileForm
profile = Blueprint('profile', __name__, url_prefix="/profile")


@profile.route("/", methods=["GET", "POST"])
@login_required
def profile_page():
    user_id = current_user.get_id()
    profile = Profile.query.filter_by(user_id=user_id).first()
    
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


# @profile.route("/", methods=["POST"])
# def create_profile():
#     profile = profile_schema.load(request.json)

#     new_profile = Profile()
#     new_profile.name = profile["name"]

#     db.session.add(new_profile)
#     db.session.commit()

#     return jsonify(profile_schema.dump(new_profile))
