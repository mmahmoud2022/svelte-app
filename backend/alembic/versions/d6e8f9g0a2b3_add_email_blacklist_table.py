"""add_email_blacklist_table

Revision ID: d6e8f9g0a2b3
Revises: c5d7e8f9a1b2
Create Date: 2025-11-05 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd6e8f9g0a2b3'
down_revision = 'c5d7e8f9a1b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for blacklist reason only if it doesn't exist
    conn = op.get_bind()
    
    # Check if the enum type already exists
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'blacklistreason')"
    ))
    enum_exists = result.scalar()
    
    if not enum_exists:
        # Create the enum type
        op.execute("CREATE TYPE blacklistreason AS ENUM ('deleted', 'suspended', 'banned', 'fraud')")
    
    # Create email_blacklist table
    op.create_table(
        'email_blacklist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('reason', postgresql.ENUM('deleted', 'suspended', 'banned', 'fraud', name='blacklistreason', create_type=False), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('original_user_id', sa.Integer(), nullable=True),
        sa.Column('original_user_name', sa.String(length=200), nullable=True),
        sa.Column('original_user_role', sa.String(length=50), nullable=True),
        sa.Column('blacklisted_by_admin_id', sa.Integer(), nullable=True),
        sa.Column('blacklisted_by_admin_email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_email_blacklist_email', 'email_blacklist', ['email'], unique=True)
    op.create_index('ix_email_blacklist_id', 'email_blacklist', ['id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_email_blacklist_id', table_name='email_blacklist')
    op.drop_index('ix_email_blacklist_email', table_name='email_blacklist')
    
    # Drop table
    op.drop_table('email_blacklist')
    
    # Drop enum type
    sa.Enum(name='blacklistreason').drop(op.get_bind(), checkfirst=True)
