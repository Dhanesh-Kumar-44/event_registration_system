"""change column type

Revision ID: 371654f38605
Revises: 
Create Date: 2023-12-18 21:02:21.377203

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '371654f38605'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_path', sa.String(length=255), nullable=True))

    # with op.batch_alter_table('participant', schema=None) as batch_op:
    #     batch_op.drop_column('profile_picture')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('participant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_picture', sa.VARCHAR(length=100), nullable=True))

    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_column('image_path')

    # ### end Alembic commands ###
