from models.Profile import Profile
from models.Groups import Groups
from models.Locations import Location
from models.Group_members import GroupMembers
from controllers.profile_controller import retrieve_profile
from main import db
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from forms import CreateGroup, SearchLocation
import requests
import json

groups = Blueprint("groups", __name__, url_prefix="/web/groups")


@groups.route("/", methods=["GET"])
@login_required
def groups_page():
    user_id, profile = retrieve_profile()
    # My Groups logic
    groups = Groups.query.with_entities(
        Profile.id, GroupMembers.admin, Groups.id,
        Groups.name, Location.postcode, Location.suburb,
        Location.state).select_from(Profile).filter_by(
            id=profile.id).outerjoin(GroupMembers).join(Groups).join(Location)

    # Group recommendations logic
    member = []
    non_member = []
    locations = []
    recommendations = []
    # Get user's groups
    for group in groups:
        member.append(Groups.query.get(group.id))
    # Get groups that user is not a member of
    for group in Groups.query.all():
        if group not in member:
            non_member.append(group)
    # Get postcodes associated to user's profile
    for location in Location.query.filter_by(profile_id=profile.id):
        locations.append(location.postcode)

    # Find non-member group postcodes that matches postcodes associated
    # with user's profile
    for group in non_member:
        query = Groups.query.with_entities(
            Groups.name, Location.postcode, Location.suburb,
            Location.state).filter_by(id=group.id).filter(
                Location.postcode.in_(locations)).join(
                    Location).first()
        recommendations.append(query)
    return render_template(
        "groups.html", groups=groups, recommendations=recommendations)


@groups.route("/create", methods=["GET", "POST"])
@login_required
def create_group():
    user_id, profile = retrieve_profile()

    form = SearchLocation()
    form2 = CreateGroup()
    form2.group_location.choices = None
    data = None

    if form.validate_on_submit():
        url = f"http://v0.postcodeapi.com.au/suburbs/{form.postcode.data}.json"
        response = requests.get(url)
        data = json.loads(response.text)
        group_locations = [
            (index, (location["name"], location["state"]["abbreviation"]))
            for index, location in enumerate(data)]
        form2.group_location.choices = group_locations
        return render_template(
            "create_group.html", form=form, form2=form2, data=data)
    if form2.is_submitted():
        form2.group_location.choices = request.args["locations"]
        data = request.args.to_dict(flat=False)
    if form2.validate_on_submit():
        location = data["data"][int(form2.group_location.data)]
        location = location.replace("'", '"')
        location = json.loads(location)

        new_group = Groups()
        new_group.name = form2.group_name.data
        new_group.description = form2.group_description.data
        new_location = Location()
        new_location.postcode = location["postcode"]
        new_location.suburb = location["name"]
        new_location.state = location["state"]["abbreviation"]

        new_group.location.append(new_location)
        GroupMembers(group=new_group, profile=profile, admin=True)
        db.session.add(new_group, new_location)
        db.session.commit()
        flash("Group created!")
        return redirect(url_for("groups.groups_page"))
    return render_template(
        "create_group.html", form=form, form2=form2, data=data)