from models.Groups import Groups
from models.Locations import Location
from models.Group_members import GroupMembers
from controllers.profile_controller import retrieve_profile
from main import db
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required
from forms import CreateGroup
import random

groups = Blueprint("groups", __name__, url_prefix="/web/groups")


@groups.route("/")
@login_required
def groups_page():
    return render_template("groups.html")


@groups.route("/create", methods=["GET", "POST"])
@login_required
def create_group():
    user_id, profile = retrieve_profile()
    default_location = Location.query.filter_by(profile_id=profile.id).all()

    form = CreateGroup()
    if form.validate_on_submit():
        new_group = Groups()
        new_group.name = form.group_name.data
        new_group.description = form.group_description.data
        new_group.location.append(random.choice(default_location))
        GroupMembers(group=new_group, profile=profile, admin=True)
        db.session.add(new_group)
        db.session.commit()
        flash("This ran!")
        return redirect(url_for("groups.groups_page"))
    return render_template("create_group.html", form=form)
