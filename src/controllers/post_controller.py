from  main import db
from models.Posts import Posts
from models.Comments import Comments
from flask import Blueprint
from flask_login import login_required

posts = Blueprint("posts", __name__, url_prefix="/web/posts")

@posts.route("/", methods=["GET"])
@login_required
def group_posts():
    pass