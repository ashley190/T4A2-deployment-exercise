from main import ma
from models.Group_members import GroupMembers
from schemas.GroupSchema import GroupSchema
from schemas.ProfileSchema import ProfileSchema


class GroupMemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GroupMembers

    group_id = ma.Integer()
    profile_id = ma.Integer()
    admin = ma.Boolean()
    group = ma.Nested(GroupSchema)
    profile = ma.Nested(ProfileSchema)


group_member_schema = GroupMemberSchema()
group_members_schema = GroupMemberSchema(many=True)
