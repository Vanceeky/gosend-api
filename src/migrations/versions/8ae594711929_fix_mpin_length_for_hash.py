"""fix mpin length for hash

Revision ID: 8ae594711929
Revises: f70b3e71adcd
Create Date: 2025-03-13 16:01:41.730878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '8ae594711929'
down_revision: Union[str, None] = 'f70b3e71adcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('members', 'mpin',
               existing_type=mysql.VARCHAR(length=4),
               type_=sa.String(length=255),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('members', 'mpin',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=4),
               existing_nullable=True)
    # ### end Alembic commands ###
