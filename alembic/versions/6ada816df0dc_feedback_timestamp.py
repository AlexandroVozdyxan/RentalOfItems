"""feedback timestamp

Revision ID: 6ada816df0dc
Revises: 50abe22d9546
Create Date: 2025-02-26 15:30:40.265627
3
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ada816df0dc'
down_revision: Union[str, None] = '50abe22d9546'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feedback', sa.Column('timestamp', sa.DateTime(), server_default='datetime()', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('feedback', 'timestamp')
    # ### end Alembic commands ###
