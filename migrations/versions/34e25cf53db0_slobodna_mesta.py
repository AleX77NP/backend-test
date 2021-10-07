"""slobodna mesta 

Revision ID: 34e25cf53db0
Revises: bd92357c58db
Create Date: 2021-10-07 12:31:50.414712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34e25cf53db0'
down_revision = 'bd92357c58db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('aranzman', sa.Column('slobodna_mesta', sa.Integer(), nullable=True))
    op.drop_constraint('rezervacija_aranzman_fkey', 'rezervacija', type_='foreignkey')
    op.create_foreign_key(None, 'rezervacija', 'aranzman', ['aranzman'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'rezervacija', type_='foreignkey')
    op.create_foreign_key('rezervacija_aranzman_fkey', 'rezervacija', 'aranzman', ['aranzman'], ['id'])
    op.drop_column('aranzman', 'slobodna_mesta')
    # ### end Alembic commands ###