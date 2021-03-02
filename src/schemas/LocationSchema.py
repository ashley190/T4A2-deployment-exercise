from main import ma
from models.Locations import Location
from schemas.ProfileSchema import ProfileSchema
from schemas.GroupSchema import GroupSchema


class LocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Location

    id = ma.Integer()
    postcode = ma.Integer()
    suburb = ma.String()
    state = ma.String()
    profile = ma.Nested(ProfileSchema)
    group = ma.Nested(GroupSchema)


location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)
