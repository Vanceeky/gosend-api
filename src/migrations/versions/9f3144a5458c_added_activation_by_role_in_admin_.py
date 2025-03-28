"""added activation by role  in admin accounts

Revision ID: 9f3144a5458c
Revises: cef94a890f6d
Create Date: 2025-03-27 12:56:21.591135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f3144a5458c'
down_revision: Union[str, None] = 'cef94a890f6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activation_history', sa.Column('activated_by_role', sa.Enum('LEADER', 'CUSTOMER SUPPORT', 'MEMBER'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('activation_history', 'activated_by_role')
    # ### end Alembic commands ###
