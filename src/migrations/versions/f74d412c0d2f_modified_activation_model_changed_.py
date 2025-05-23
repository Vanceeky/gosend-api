"""modified activation model, changed status into string

Revision ID: f74d412c0d2f
Revises: bceb6fca572d
Create Date: 2025-03-25 13:52:17.912211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'f74d412c0d2f'
down_revision: Union[str, None] = 'bceb6fca572d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('activation_history', 'status',
               existing_type=mysql.ENUM('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED'),
               type_=sa.String(length=50),
               existing_nullable=False,
               existing_server_default=sa.text("'PENDING'"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('activation_history', 'status',
               existing_type=sa.String(length=50),
               type_=mysql.ENUM('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED'),
               existing_nullable=False,
               existing_server_default=sa.text("'PENDING'"))
    # ### end Alembic commands ###
