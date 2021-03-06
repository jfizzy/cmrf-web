"""User Model Migration to add PI first and last name

Revision ID: 48fed0beea72
Revises: 349314394abf
Create Date: 2017-09-13 10:48:44.148074

"""

# revision identifiers, used by Alembic.
revision = '48fed0beea72'
down_revision = '349314394abf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('USER', sa.Column('pi_fname', sa.String(length=64), nullable=False, server_default='Ian'))
    op.add_column('USER', sa.Column('pi_lname', sa.String(length=64), nullable=False, server_default='Lewis'))
    op.drop_column('USER', 'lab')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('USER', sa.Column('lab', sa.VARCHAR(length=64), nullable=True, server_default='CMRF'))
    op.drop_column('USER', 'pi_lname')
    op.drop_column('USER', 'pi_fname')
    ### end Alembic commands ###
