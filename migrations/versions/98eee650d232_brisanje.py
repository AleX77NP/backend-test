"""brisanje

Revision ID: 98eee650d232
Revises: 34e25cf53db0
Create Date: 2021-10-07 12:33:35.360683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98eee650d232'
down_revision = '34e25cf53db0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('aranzman', 'slobodna_mesta',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint('aranzman_admin_fkey', 'aranzman', type_='foreignkey')
    op.drop_constraint('aranzman_vodic_fkey', 'aranzman', type_='foreignkey')
    op.create_foreign_key(None, 'aranzman', 'korisnik', ['vodic'], ['korisnicko_ime'], ondelete='CASCADE')
    op.create_foreign_key(None, 'aranzman', 'korisnik', ['admin'], ['korisnicko_ime'], ondelete='SET NULL')
    op.drop_constraint('rezervacija_korisnik_fkey', 'rezervacija', type_='foreignkey')
    op.create_foreign_key(None, 'rezervacija', 'korisnik', ['korisnik'], ['korisnicko_ime'], ondelete='CASCADE')
    op.drop_constraint('zahtev_podnosilac_fkey', 'zahtev', type_='foreignkey')
    op.create_foreign_key(None, 'zahtev', 'korisnik', ['podnosilac'], ['korisnicko_ime'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'zahtev', type_='foreignkey')
    op.create_foreign_key('zahtev_podnosilac_fkey', 'zahtev', 'korisnik', ['podnosilac'], ['korisnicko_ime'])
    op.drop_constraint(None, 'rezervacija', type_='foreignkey')
    op.create_foreign_key('rezervacija_korisnik_fkey', 'rezervacija', 'korisnik', ['korisnik'], ['korisnicko_ime'])
    op.drop_constraint(None, 'aranzman', type_='foreignkey')
    op.drop_constraint(None, 'aranzman', type_='foreignkey')
    op.create_foreign_key('aranzman_vodic_fkey', 'aranzman', 'korisnik', ['vodic'], ['korisnicko_ime'])
    op.create_foreign_key('aranzman_admin_fkey', 'aranzman', 'korisnik', ['admin'], ['korisnicko_ime'])
    op.alter_column('aranzman', 'slobodna_mesta',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
