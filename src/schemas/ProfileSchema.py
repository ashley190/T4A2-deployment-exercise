from main import ma
from models.Profile import Profile
from marshmallow.validate import Length


class ProfileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Profile

    name = ma.String(required=True, validate=Length(min=1))


profile_schema = ProfileSchema()
