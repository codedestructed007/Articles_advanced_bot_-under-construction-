"""Created date and image fields

Revision ID: 6e87340db92c
Revises: d364d58f8426
Create Date: 2024-02-03 13:22:20.131307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e87340db92c'
down_revision = 'd364d58f8426'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('image', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.drop_column('image')
        batch_op.drop_column('date')

    # ### end Alembic commands ###
