from main import ma
from models.Groups import Groups
from marshmallow.validate import Length


class GroupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        mode = Groups

    id = ma.Integer()
    name = ma.String(required=True, validate=Length(min=1))
    description = ma.String()


group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)


class GroupLocationSchema(ma.Schema):
    id = ma.Integer()
    # admin = ma.Boolean()
    name = ma.String()
    postcode = ma.Integer()
    suburb = ma.String()
    state = ma.String()


group_location_schema = GroupLocationSchema()
groups_location_schema = GroupLocationSchema(many=True)
