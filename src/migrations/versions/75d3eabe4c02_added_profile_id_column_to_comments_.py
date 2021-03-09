"""added profile_id column to comments table

Revision ID: 75d3eabe4c02
Revises: 38432cc0ee6f
Create Date: 2021-03-06 12:53:09.023673

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75d3eabe4c02'
down_revision = '38432cc0ee6f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('profile_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'comments', 'profile', ['profile_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.drop_column('comments', 'profile_id')
    # ### end Alembic commands ###