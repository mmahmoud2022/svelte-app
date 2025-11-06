"""add_admin_approved_field_to_users

Revision ID: c5d7e8f9a1b2
Revises: 98050874729b
Create Date: 2025-11-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5d7e8f9a1b2'
down_revision = '98050874729b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add admin_approved column to users table
    op.add_column('users', sa.Column('admin_approved', sa.Boolean(), nullable=False, server_default='false'))
    
    # Set admin_approved to True for existing non-doctor users (patients and admins)
    op.execute("UPDATE users SET admin_approved = true WHERE role IN ('PATIENT', 'ADMIN')")


def downgrade() -> None:
    # Remove admin_approved column
    op.drop_column('users', 'admin_approved')
