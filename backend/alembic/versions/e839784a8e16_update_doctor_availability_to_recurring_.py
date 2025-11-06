"""update_doctor_availability_to_recurring_schedule

Revision ID: e839784a8e16
Revises: e1c17f7c30ee
Create Date: 2025-11-06 23:48:28.837694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e839784a8e16'
down_revision: Union[str, None] = 'e1c17f7c30ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update doctor_availabilities table for recurring schedule
    # Drop columns we don't need anymore
    op.drop_column('doctor_availabilities', 'date')
    op.drop_column('doctor_availabilities', 'location')
    op.drop_column('doctor_availabilities', 'is_booked')
    op.drop_column('doctor_availabilities', 'notes')
    
    # Add day_of_week for recurring schedule (0=Sunday, 1=Monday, ..., 6=Saturday)
    op.add_column('doctor_availabilities', sa.Column('day_of_week', sa.Integer(), nullable=False, server_default='1'))
    op.create_index('ix_doctor_availabilities_day_of_week', 'doctor_availabilities', ['day_of_week'])
    
    # Remove server default after adding the column
    op.alter_column('doctor_availabilities', 'day_of_week', server_default=None)
    
    # Add new fields to appointments table for medical records
    op.add_column('appointments', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('appointments', sa.Column('diagnosis', sa.Text(), nullable=True))
    op.add_column('appointments', sa.Column('prescription', sa.Text(), nullable=True))


def downgrade() -> None:
    # Reverse the changes for appointments
    op.drop_column('appointments', 'prescription')
    op.drop_column('appointments', 'diagnosis')
    op.drop_column('appointments', 'notes')
    
    # Reverse the changes for doctor_availabilities
    op.drop_index('ix_doctor_availabilities_day_of_week', 'doctor_availabilities')
    op.drop_column('doctor_availabilities', 'day_of_week')
    
    # Re-add the old columns
    op.add_column('doctor_availabilities', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('doctor_availabilities', sa.Column('is_booked', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('doctor_availabilities', sa.Column('location', sa.String(length=255), nullable=True))
    op.add_column('doctor_availabilities', sa.Column('date', sa.Date(), nullable=False, server_default='2025-01-01'))
