"""make_rpps_number_optional

Revision ID: e1c17f7c30ee
Revises: e7f0g1h2a3b4
Create Date: 2025-11-06 19:07:06.994837

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1c17f7c30ee'
down_revision: Union[str, None] = 'e7f0g1h2a3b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
