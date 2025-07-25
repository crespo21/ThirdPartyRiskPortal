"""Add updated_at column to Company model

Revision ID: cb3159ff9d53
Revises: 6fd019176cc9
Create Date: 2025-07-05 15:20:42.284168

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb3159ff9d53'
down_revision: Union[str, None] = '6fd019176cc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('core_company', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('core_company', 'updated_at')
    # ### end Alembic commands ###
