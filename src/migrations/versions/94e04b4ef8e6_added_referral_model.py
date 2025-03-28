"""added referral model

Revision ID: 94e04b4ef8e6
Revises: a8faee34d8ae
Create Date: 2025-03-11 14:18:00.683655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94e04b4ef8e6'
down_revision: Union[str, None] = 'a8faee34d8ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('referrals',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('referred_by', sa.String(length=36), nullable=False),
    sa.Column('referred_member', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['referred_by'], ['members.member_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['referred_member'], ['members.member_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('referrals')
    # ### end Alembic commands ###
