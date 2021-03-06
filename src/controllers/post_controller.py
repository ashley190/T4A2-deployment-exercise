from main import db
from models.Posts import Posts
# from models.Comments import Comments
from models.Groups import Groups
from models.Group_members import GroupMembers
from controllers.controller_helpers import Helpers
from flask import Blueprint, render_template, url_for, flash, redirect, abort
from flask_login import login_required
from forms import CreatePost

posts = Blueprint("posts", __name__, url_prefix="/web/posts")


@posts.route("/<int:id>/create", methods=["GET", "POST"])
@login_required
def create_group_posts(id):
    user_id, profile = Helpers.retrieve_profile()
    group = Groups.query.get(id)
    member = GroupMembers.query.filter_by(
        profile_id=profile.id, group_id=id).first()
    form = CreatePost()

    if not member:
        return abort(401, description="Unauthorised to create post")
    if form.validate_on_submit():
        new_post = Posts()
        new_post.post = form.post.data
        new_post.profile_id = profile.id
        new_post.group_id = id
        profile.posts.append(new_post)
        group.posts.append(new_post)
        db.session.commit()
        flash(f"Post added to group {group.name}")
        return redirect(url_for("groups.group_details", id=id))

    return render_template("new_post.html", id=id, form=form)
