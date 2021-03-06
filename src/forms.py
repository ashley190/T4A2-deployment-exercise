from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField,
                     IntegerField, TextAreaField, RadioField, SelectField)
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
    NumberRange
)


class RegistrationForm(FlaskForm):
    """User Registration Form"""
    username = StringField(
        "Username",
        validators=[
            Length(min=6),
            DataRequired()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            Length(min=6, message="Password must be at least 8 characters"),
            DataRequired()
        ]
    )

    confirm = PasswordField(
        "Confirm Password",
        validators=[
            EqualTo("password", message="Password must match.")
        ]
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    """User Login Form"""
    username = StringField(
        "Username",
        validators=[
            DataRequired()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Log In")


class ProfileForm(FlaskForm):
    """Create profile name"""
    profile_name = StringField(
        "Profile Name",
        validators=[
            Length(min=1, message="Profile name must be at least 1 character"),
            DataRequired()
        ]
    )

    submit = SubmitField("Confirm Profile Name")


class ProfileImageUpload(FlaskForm):
    image = FileField("Profile Image", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])

    submit = SubmitField("Upload Profile Image")


class DeleteButton(FlaskForm):
    submit = SubmitField("Delete")


class SearchLocation(FlaskForm):
    postcode = IntegerField("Postcode", validators=[NumberRange(200, 9999)])
    submit = SubmitField("Search")


class AddButton(FlaskForm):
    submit = SubmitField("Add")


class UpdateButton(FlaskForm):
    submit = SubmitField("Update")


class CreateGroup(FlaskForm):
    """Create Group"""
    group_name = StringField(
        "Group Name",
        validators=[
            Length(min=1, message="Group name must be at least 1 character"),
            DataRequired()
        ]
    )

    group_description = TextAreaField(
        "Description"
    )

    group_location = RadioField("Group location", choices=[])
    submit = SubmitField("Create Group")


class UpdateGroup(FlaskForm):
    """Update Group"""
    group_name = StringField(
        "Group Name",
        validators=[
            Length(min=1, message="Group name must be at least 1 character")
        ]
    )

    group_description = TextAreaField(
        "Description"
    )

    submit = SubmitField("Update Group")


class JoinButton(FlaskForm):
    submit = SubmitField("Join")


class UnjoinButton(FlaskForm):
    submit = SubmitField("Unjoin")


class SearchForm(FlaskForm):
    keyword = StringField(
        "Search keyword",
        validators=[
            Length(min=1, message="Keyword must be at least 1 character")
        ]
    )

    field = SelectField(
        "Search Field",
        choices=[
            (1, "Group details"),
            (2, "Postcode")
        ], coerce=int,
        validators=[DataRequired()]
    )

    submit = SubmitField("Search")


class CreatePost(FlaskForm):
    post = TextAreaField(
        "New Post",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Add Post")
