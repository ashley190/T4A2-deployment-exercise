from models.Profile import Profile
from models.Groups import Groups
from models.Locations import Location
from models.Group_members import GroupMembers
from schemas.GroupSchema import groups_location_schema
from controllers.profile_controller import retrieve_profile
from main import db
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from forms import CreateGroup, SearchLocation
import requests
import json

groups = Blueprint("groups", __name__, url_prefix="/web/groups")


@groups.route("/", methods=["GET"])
@login_required
def groups_page():
    user_id, profile = retrieve_profile()

    # groups = Profile.query.with_entities(
    #     Profile.id, GroupMembers.admin, Groups.name, Location.postcode, Location.suburb, Location.state).select_from(Profile).outerjoin(GroupMembers).join(Groups).join(Location).filter_by(id=profile.id)
    # # return f"{groups}"
    groups = Profile.query.with_entities(Profile.id, GroupMembers.admin, Groups.id, Groups.name, Location.postcode, Location.suburb, Location.state).select_from(Profile).filter_by(id=profile.id).outerjoin(GroupMembers).join(Groups).join(Location)
    # return f"{groups}"
    return jsonify(groups_location_schema.dump(groups))

# select p.id as profile_id, gm.admin as admin, g.name as group_name, l.postcode as postcode, l.suburb as suburb, l.state as state
# from profile p
# left outer join group_members gm on p.id=gm.profile_id
# inner join groups g on gm.group_id=g.id
# inner join locations l on g.id=l.group_id
# where p.id = 2;    
    # return render_template("groups.html", groups=groups)


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

