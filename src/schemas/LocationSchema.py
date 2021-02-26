from main import ma
from models.Locations import Location


class LocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Location


location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)
