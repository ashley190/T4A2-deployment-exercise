from main import ma
from models.Posts import Posts
from marshmallow.validate import Length


class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        mode = Posts

    id = ma.Integer()
    date = ma.DateTime()
    post = ma.String(required=True, validate=Length(min=1))


post_schema = PostSchema()
posts_schema = PostSchema(many=True)
