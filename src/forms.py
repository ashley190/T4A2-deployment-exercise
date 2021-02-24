from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length
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