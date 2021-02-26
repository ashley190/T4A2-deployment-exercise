"""Added in locations table

Revision ID: 5081a7a1eadb
Revises: 8b245d1be437
Create Date: 2021-02-26 15:26:36.794160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5081a7a1eadb'
down_revision = '8b245d1be437'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('postcode', sa.Integer(), nullable=False),
    sa.Column('suburb', sa.String(), nullable=False),
    sa.Column('state', sa.String(), nullable=False),
    sa.Column('profile_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('locations')
    # ### end Alembic commands ###
