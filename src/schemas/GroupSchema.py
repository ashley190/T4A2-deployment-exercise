from main import ma
from models.Groups import Groups
from marshmallow.validate import Length


class GroupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        mode = Groups

    name = ma.String(required=True, validate=Length(min=1))


group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)
