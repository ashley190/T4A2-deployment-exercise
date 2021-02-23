from main import ma
from models.User import Users
from marshmallow.validate import Length


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_only = ["password"]

        email = ma.String(required=True, validate=Length(min=6))
        password = ma.String(required=True, validate=Length(min=6))


user_schema = UserSchema()
users_schema = UserSchema(many=True)
