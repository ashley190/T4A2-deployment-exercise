from main import db
from models.Posts import Posts
from models.Comments import Comments
from models.Groups import Groups
from models.Group_members import GroupMembers
from schemas.PostSchema import post_schema
from controllers.controller_helpers import Helpers
from flask import Blueprint, render_template, url_for, flash, redirect, abort
from flask_login import login_required
from forms import CreatePost, Comment, UpdatePost, DeleteButton
from datetime import datetime

posts = Blueprint("posts", __name__, url_prefix="/web/posts")


@posts.route("/<int:id>/create", methods=["GET", "POST"])
@login_required
def create_group_posts(id):
    """
    Page for creating new posts

    GET requests renders post creation page
    POST requests handles form validation for post creation
    and post creation logic.
    """
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
    """
    Page for adding comments to a post.

    GET requests renders comment creation page with relevant form
    POST requets handles form validation and addition of comment
    to post as specified by id.
    """
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


@posts.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update_post(id):
    """
    Post update page

    GET requests renders page with post update form
    POST requests handles form validation and post update logic.
    """
    user_id, profile = Helpers.retrieve_profile()
    post = Posts.query.filter_by(id=id)
    form = UpdatePost()

    if post.first().profile_id != profile.id:
        return abort(401, description="Not authorised to update")
    if form.validate_on_submit():
        data = {
            "date": str(datetime.now()),
            "post": form.post.data
        }
        fields = post_schema.load(data, partial=True)
        post.update(fields)
        db.session.commit()
        flash("Post updated")
        return redirect(url_for(
            "groups.group_details", id=post.first().group_id))

    return render_template("update_post.html", id=id, form=form)


@posts.route("/<int:id>/remove", methods=["POST"])
@login_required
def remove_post(id):
    """
    Handles post deletion logic. Can only be performed by original poster.
    """
    user_id, profile = Helpers.retrieve_profile()
    form = DeleteButton()
    post = Posts.query.filter_by(id=id).first()
    comments = Comments.query.filter_by(post_id=post.id).all()

    if form.validate_on_submit():
        if post.profile_id != profile.id:
            return abort(401, description="Unauthorised to remove post.")
        for comment in comments:
            db.session.delete(comment)
        db.session.delete(post)
        db.session.commit()
        flash("Post removed")

    return redirect(url_for(
        "groups.group_details", id=post.group_id))
