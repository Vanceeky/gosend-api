"""added investor enum in admin accounts

Revision ID: cacd2328f6a8
Revises: bcdfae64414c
Create Date: 2025-03-20 16:16:49.253259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cacd2328f6a8'
down_revision: Union[str, None] = 'bcdfae64414c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
