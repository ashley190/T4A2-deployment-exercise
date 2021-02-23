from flask import Blueprint, redirect, render_template, flash, request, url_for
from flask_login import login_required, logout_user, current_user, login_user
from forms import RegistrationForm, LoginForm
from models.User import Users
from main import db, login_manager


auth = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on each page load"""
    if user_id:
        return Users.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorised():
    flash("You must be logged in to view this page")
    return redirect(url_for("auth.login"))


@auth.route("/registration", methods=["GET", "POST"])
def register():
    """
    User registration page

    GET requests renders signup page
    POST request validate form and handles front end user registration
    """

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = Users.query.filter_by(
            username=form.username.data).first()
        if not existing_user:
            new_user = Users(
                username=form.username.data
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("profile.profile_page"))
        flash("A user already exists with that username.")
    return render_template(
        "register.html", form=form
    )


@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Login page for registered users

    GET requests renders login page
    POST requests validate and handles front end user login
    """

    # Bypass if user is currently logged in
    if current_user.is_authenticated:
        return redirect(url_for("profile.profile_page"))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for("profile.profile_page"))
        flash("Invalid username and password")
        return redirect(url_for("auth.login"))
    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
