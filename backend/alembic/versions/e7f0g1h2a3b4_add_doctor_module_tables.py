"""add_doctor_module_tables

Revision ID: e7f0g1h2a3b4
Revises: d6e8f9g0a2b3
Create Date: 2025-11-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e7f0g1h2a3b4'
down_revision = 'd6e8f9g0a2b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types with checkfirst to avoid duplicates
    from sqlalchemy.dialects.postgresql import ENUM
    
    specialty_enum = ENUM(
        'general_practitioner', 'cardiologist', 'dermatologist', 
        'pediatrician', 'gynecologist', 'psychiatrist', 
        'ophthalmologist', 'dentist', 'orthopedist', 
        'neurologist', 'radiologist', 'surgeon', 'other',
        name='specialtyenum',
        create_type=False
    )
    
    consultation_type_enum = ENUM(
        'in_person', 'teleconsultation', 'both',
        name='consultationtypeenum',
        create_type=False
    )
    
    appointment_status_enum = ENUM(
        'pending', 'confirmed', 'completed', 'cancelled', 'no_show',
        name='appointmentstatusenum',
        create_type=False
    )
    
    payment_status_enum = ENUM(
        'pending', 'completed', 'failed', 'refunded',
        name='paymentstatusenum',
        create_type=False
    )
    
    # Create types if they don't exist
    connection = op.get_bind()
    
    # Check and create each enum type
    from sqlalchemy import text
    connection.execute(text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'specialtyenum') THEN
                CREATE TYPE specialtyenum AS ENUM (
                    'general_practitioner', 'cardiologist', 'dermatologist', 
                    'pediatrician', 'gynecologist', 'psychiatrist', 
                    'ophthalmologist', 'dentist', 'orthopedist', 
                    'neurologist', 'radiologist', 'surgeon', 'other'
                );
            END IF;
        END $$;
    """))
    
    connection.execute(text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'consultationtypeenum') THEN
                CREATE TYPE consultationtypeenum AS ENUM (
                    'in_person', 'teleconsultation', 'both'
                );
            END IF;
        END $$;
    """))
    
    connection.execute(text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'appointmentstatusenum') THEN
                CREATE TYPE appointmentstatusenum AS ENUM (
                    'pending', 'confirmed', 'completed', 'cancelled', 'no_show'
                );
            END IF;
        END $$;
    """))
    
    connection.execute(text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'paymentstatusenum') THEN
                CREATE TYPE paymentstatusenum AS ENUM (
                    'pending', 'completed', 'failed', 'refunded'
                );
            END IF;
        END $$;
    """))
    
    # Create doctor_profiles table
    op.create_table(
        'doctor_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('specialty', specialty_enum, nullable=False),
        sa.Column('sub_specialty', sa.String(length=100), nullable=True),
        sa.Column('rpps_number', sa.String(length=50), nullable=False),
        sa.Column('office_address', sa.Text(), nullable=True),
        sa.Column('office_city', sa.String(length=100), nullable=True),
        sa.Column('office_postal_code', sa.String(length=20), nullable=True),
        sa.Column('office_phone', sa.String(length=20), nullable=True),
        sa.Column('biography', sa.Text(), nullable=True),
        sa.Column('languages', sa.JSON(), nullable=True),
        sa.Column('education', sa.JSON(), nullable=True),
        sa.Column('experience_years', sa.Integer(), nullable=True, default=0),
        sa.Column('consultation_types', consultation_type_enum, 
                  nullable=True, default='both'),
        sa.Column('consultation_duration', sa.Integer(), nullable=True, default=30),
        sa.Column('consultation_price', sa.Float(), nullable=True),
        sa.Column('accepts_new_patients', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('total_consultations', sa.Integer(), nullable=True, default=0),
        sa.Column('average_rating', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_reviews', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('rpps_number')
    )
    op.create_index('ix_doctor_profiles_id', 'doctor_profiles', ['id'])
    op.create_index('ix_doctor_profiles_user_id', 'doctor_profiles', ['user_id'])
    op.create_index('ix_doctor_profiles_rpps_number', 'doctor_profiles', ['rpps_number'])
    
    # Create doctor_availabilities table
    op.create_table(
        'doctor_availabilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('consultation_type', consultation_type_enum, nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_booked', sa.Boolean(), nullable=True, default=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_doctor_availabilities_id', 'doctor_availabilities', ['id'])
    op.create_index('ix_doctor_availabilities_doctor_id', 'doctor_availabilities', ['doctor_id'])
    op.create_index('ix_doctor_availabilities_date', 'doctor_availabilities', ['date'])
    
    # Create appointments table
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('availability_id', sa.Integer(), nullable=True),
        sa.Column('appointment_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True, default=30),
        sa.Column('consultation_type', consultation_type_enum, nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('patient_notes', sa.Text(), nullable=True),
        sa.Column('doctor_notes', sa.Text(), nullable=True),
        sa.Column('status', appointment_status_enum, nullable=True, default='pending'),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('is_paid', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['availability_id'], ['doctor_availabilities.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_appointments_id', 'appointments', ['id'])
    op.create_index('ix_appointments_doctor_id', 'appointments', ['doctor_id'])
    op.create_index('ix_appointments_patient_id', 'appointments', ['patient_id'])
    op.create_index('ix_appointments_appointment_date', 'appointments', ['appointment_date'])
    op.create_index('ix_appointments_status', 'appointments', ['status'])
    
    # Create doctor_reviews table
    op.create_table(
        'doctor_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('doctor_response', sa.Text(), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_doctor_reviews_id', 'doctor_reviews', ['id'])
    op.create_index('ix_doctor_reviews_doctor_id', 'doctor_reviews', ['doctor_id'])
    op.create_index('ix_doctor_reviews_patient_id', 'doctor_reviews', ['patient_id'])
    
    # Create doctor_messages table
    op.create_table(
        'doctor_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=True, default=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_doctor_messages_id', 'doctor_messages', ['id'])
    op.create_index('ix_doctor_messages_sender_id', 'doctor_messages', ['sender_id'])
    op.create_index('ix_doctor_messages_recipient_id', 'doctor_messages', ['recipient_id'])
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, default='EUR'),
        sa.Column('status', payment_status_enum, nullable=True, default='pending'),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('transaction_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )
    op.create_index('ix_payments_id', 'payments', ['id'])
    op.create_index('ix_payments_doctor_id', 'payments', ['doctor_id'])
    op.create_index('ix_payments_patient_id', 'payments', ['patient_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])
    
    # Create patient_documents table
    op.create_table(
        'patient_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('document_type', sa.String(length=50), nullable=True),
        sa.Column('is_patient_visible', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_patient_documents_id', 'patient_documents', ['id'])
    op.create_index('ix_patient_documents_doctor_id', 'patient_documents', ['doctor_id'])
    op.create_index('ix_patient_documents_patient_id', 'patient_documents', ['patient_id'])
    
    # Create doctor_settings table
    op.create_table(
        'doctor_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('email_notifications', sa.Boolean(), nullable=True, default=True),
        sa.Column('sms_notifications', sa.Boolean(), nullable=True, default=False),
        sa.Column('appointment_reminders', sa.Boolean(), nullable=True, default=True),
        sa.Column('profile_visibility', sa.String(length=20), nullable=True, default='public'),
        sa.Column('show_phone', sa.Boolean(), nullable=True, default=True),
        sa.Column('show_email', sa.Boolean(), nullable=True, default=True),
        sa.Column('language', sa.String(length=5), nullable=True, default='fr'),
        sa.Column('timezone', sa.String(length=50), nullable=True, default='Europe/Paris'),
        sa.Column('payment_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('payment_methods', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doctor_id')
    )
    op.create_index('ix_doctor_settings_id', 'doctor_settings', ['id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_doctor_settings_id', table_name='doctor_settings')
    op.drop_table('doctor_settings')
    
    op.drop_index('ix_patient_documents_patient_id', table_name='patient_documents')
    op.drop_index('ix_patient_documents_doctor_id', table_name='patient_documents')
    op.drop_index('ix_patient_documents_id', table_name='patient_documents')
    op.drop_table('patient_documents')
    
    op.drop_index('ix_payments_status', table_name='payments')
    op.drop_index('ix_payments_patient_id', table_name='payments')
    op.drop_index('ix_payments_doctor_id', table_name='payments')
    op.drop_index('ix_payments_id', table_name='payments')
    op.drop_table('payments')
    
    op.drop_index('ix_doctor_messages_recipient_id', table_name='doctor_messages')
    op.drop_index('ix_doctor_messages_sender_id', table_name='doctor_messages')
    op.drop_index('ix_doctor_messages_id', table_name='doctor_messages')
    op.drop_table('doctor_messages')
    
    op.drop_index('ix_doctor_reviews_patient_id', table_name='doctor_reviews')
    op.drop_index('ix_doctor_reviews_doctor_id', table_name='doctor_reviews')
    op.drop_index('ix_doctor_reviews_id', table_name='doctor_reviews')
    op.drop_table('doctor_reviews')
    
    op.drop_index('ix_appointments_status', table_name='appointments')
    op.drop_index('ix_appointments_appointment_date', table_name='appointments')
    op.drop_index('ix_appointments_patient_id', table_name='appointments')
    op.drop_index('ix_appointments_doctor_id', table_name='appointments')
    op.drop_index('ix_appointments_id', table_name='appointments')
    op.drop_table('appointments')
    
    op.drop_index('ix_doctor_availabilities_date', table_name='doctor_availabilities')
    op.drop_index('ix_doctor_availabilities_doctor_id', table_name='doctor_availabilities')
    op.drop_index('ix_doctor_availabilities_id', table_name='doctor_availabilities')
    op.drop_table('doctor_availabilities')
    
    op.drop_index('ix_doctor_profiles_rpps_number', table_name='doctor_profiles')
    op.drop_index('ix_doctor_profiles_user_id', table_name='doctor_profiles')
    op.drop_index('ix_doctor_profiles_id', table_name='doctor_profiles')
    op.drop_table('doctor_profiles')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS paymentstatusenum')
    op.execute('DROP TYPE IF EXISTS appointmentstatusenum')
    op.execute('DROP TYPE IF EXISTS consultationtypeenum')
    op.execute('DROP TYPE IF EXISTS specialtyenum')
