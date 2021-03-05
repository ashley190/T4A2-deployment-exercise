from controllers.profile_controller import profile
from controllers.auth_controller import auth
from controllers.group_controller import groups
from controllers.post_controller import posts

registerable_controllers = [
    auth,
    profile,
    groups,
    posts
]
