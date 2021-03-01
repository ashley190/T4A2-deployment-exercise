from main import ma
from models.Locations import Location


class LocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Location

    postcode = ma.Integer()
    suburb = ma.String()
    state = ma.String()


location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)
