from main import db
from models.Posts import Posts
from models.Comments import Comments
from models.Groups import Groups
from models.Group_members import GroupMembers
from controllers.controller_helpers import Helpers
from flask import Blueprint, render_template, url_for, flash, redirect, abort
from flask_login import login_required
from forms import CreatePost, Comment

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


@posts.route("/<int:id>/comment", methods=["GET", "POST"])
@login_required
def post_comment(id):
    user_id, profile = Helpers.retrieve_profile()
    post = Posts.query.get(id)
    member = GroupMembers.query.filter_by(
        profile_id=profile.id, group_id=post.group_id).first()
    form = Comment()

    if not member:
        return abort(401, description="Unauthorised to comment.")
    if form.validate_on_submit():
        new_comment = Comments()
        new_comment.comment = form.comment.data
        new_comment.post_id = post.id
        new_comment.profile_id = profile.id
        post.comments.append(new_comment)
        profile.comments.append(new_comment)
        db.session.commit()
        flash("Comment added!")
        return redirect(url_for("groups.group_details", id=post.group_id))

    return render_template("comment.html", form=form, id=post.id)


@posts.route("/<int:id>/update", methods=["GET, POST"])
@login_required
def update_post(id):
    user_id, profile = Helpers.retrieve_profile()
    post = Posts.query.get(id)

    if post.profile_id != profile.id:
        return abort(401, description="Not authorised to update")
