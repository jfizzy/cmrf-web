"""Small change to FundingAccount

Revision ID: 4be14ef5fa4c
Revises: 3869f69a6f31
Create Date: 2016-12-09 11:11:49.720928

"""

# revision identifiers, used by Alembic.
revision = '4be14ef5fa4c'
down_revision = '3869f69a6f31'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('FUNDING_ACCOUNT', sa.Column('acc_other', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('FUNDING_ACCOUNT', 'acc_other')
    ### end Alembic commands ###
