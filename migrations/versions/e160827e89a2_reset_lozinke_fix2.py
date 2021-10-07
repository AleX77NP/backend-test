"""reset lozinke fix2

Revision ID: e160827e89a2
Revises: 4e86660db904
Create Date: 2021-10-07 15:35:01.676397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e160827e89a2'
down_revision = '4e86660db904'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reset_lozinke', sa.Column('token', sa.String(length=24), nullable=False))
    op.drop_column('reset_lozinke', 'kod')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reset_lozinke', sa.Column('kod', sa.VARCHAR(length=5), autoincrement=False, nullable=False))
    op.drop_column('reset_lozinke', 'token')
    # ### end Alembic commands ###
