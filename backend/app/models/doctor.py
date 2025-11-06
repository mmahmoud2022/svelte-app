"""
Modèles de données pour le module Doctor
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, Float, Enum, Date, Time, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date, time
import enum

from app.core.database import Base


class SpecialtyEnum(str, enum.Enum):
    """Spécialités médicales"""
    GENERAL_PRACTITIONER = "general_practitioner"
    CARDIOLOGIST = "cardiologist"
    DERMATOLOGIST = "dermatologist"
    PEDIATRICIAN = "pediatrician"
    GYNECOLOGIST = "gynecologist"
    PSYCHIATRIST = "psychiatrist"
    OPHTHALMOLOGIST = "ophthalmologist"
    DENTIST = "dentist"
    ORTHOPEDIST = "orthopedist"
    NEUROLOGIST = "neurologist"
    RADIOLOGIST = "radiologist"
    SURGEON = "surgeon"
    OTHER = "other"


class ConsultationTypeEnum(str, enum.Enum):
    """Types de consultation"""
    IN_PERSON = "in_person"
    TELECONSULTATION = "teleconsultation"
    BOTH = "both"


class AppointmentStatusEnum(str, enum.Enum):
    """Statuts de rendez-vous"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PaymentStatusEnum(str, enum.Enum):
    """Statuts de paiement"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class DoctorProfile(Base):
    """Profil professionnel du médecin"""
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Informations professionnelles
    specialty = Column(Enum(SpecialtyEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    sub_specialty = Column(String(100), nullable=True)
    rpps_number = Column(String(50), unique=True, nullable=True, index=True)  # Numéro RPPS - now optional
    
    # Informations de contact
    office_address = Column(Text, nullable=True)
    office_city = Column(String(100), nullable=True)
    office_postal_code = Column(String(20), nullable=True)
    office_phone = Column(String(20), nullable=True)
    
    # Informations publiques
    biography = Column(Text, nullable=True)
    languages = Column(JSON, default=list)  # Liste de langues parlées
    education = Column(JSON, default=list)  # Formation et diplômes
    experience_years = Column(Integer, default=0)
    
    # Paramètres de consultation
    consultation_types = Column(Enum(ConsultationTypeEnum, values_callable=lambda x: [e.value for e in x]), default=ConsultationTypeEnum.BOTH)
    consultation_duration = Column(Integer, default=30)  # Durée en minutes
    consultation_price = Column(Float, nullable=True)  # Tarif
    accepts_new_patients = Column(Boolean, default=True)
    
    # Paramètres de visibilité
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Statistiques
    total_consultations = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="doctor_profile")
    availabilities = relationship("DoctorAvailability", back_populates="doctor", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    reviews = relationship("DoctorReview", back_populates="doctor", cascade="all, delete-orphan")
    # Messages are handled through user.messages_sent and user.messages_received
    payments = relationship("Payment", back_populates="doctor", cascade="all, delete-orphan")
    documents = relationship("PatientDocument", back_populates="doctor", cascade="all, delete-orphan")


class DoctorAvailability(Base):
    """Créneaux de disponibilité récurrents du médecin (par jour de semaine)"""
    __tablename__ = "doctor_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informations du créneau récurrent
    day_of_week = Column(Integer, nullable=False, index=True)  # 0=Dimanche, 1=Lundi, ..., 6=Samedi
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Type de consultation
    consultation_type = Column(Enum(ConsultationTypeEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    # Statut
    is_available = Column(Boolean, default=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    doctor = relationship("DoctorProfile", back_populates="availabilities")


class Appointment(Base):
    """Rendez-vous médical"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    availability_id = Column(Integer, ForeignKey("doctor_availabilities.id", ondelete="SET NULL"), nullable=True)
    
    # Informations du rendez-vous
    appointment_date = Column(DateTime(timezone=True), nullable=False, index=True)
    duration = Column(Integer, default=30)  # en minutes
    consultation_type = Column(Enum(ConsultationTypeEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    # Motif et notes
    reason = Column(Text, nullable=True)
    patient_notes = Column(Text, nullable=True)
    doctor_notes = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)  # Notes générales
    diagnosis = Column(Text, nullable=True)  # Diagnostic médical
    prescription = Column(Text, nullable=True)  # Prescription
    
    # Statut
    status = Column(Enum(AppointmentStatusEnum, values_callable=lambda x: [e.value for e in x]), default=AppointmentStatusEnum.PENDING, index=True)
    
    # Paiement
    price = Column(Float, nullable=True)
    is_paid = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    doctor = relationship("DoctorProfile", back_populates="appointments")
    patient = relationship("User", back_populates="appointments")


class DoctorReview(Base):
    """Avis et notes des patients"""
    __tablename__ = "doctor_reviews"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    
    # Note et commentaire
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    
    # Réponse du médecin
    doctor_response = Column(Text, nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Visibilité
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    doctor = relationship("DoctorProfile", back_populates="reviews")
    patient = relationship("User", back_populates="reviews_given")


class DoctorMessage(Base):
    """Messages entre médecin et patient"""
    __tablename__ = "doctor_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Contenu
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    
    # Statut
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Métadonnées
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="messages_received")


class Payment(Base):
    """Paiements pour les consultations"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    
    # Informations de paiement
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    status = Column(Enum(PaymentStatusEnum, values_callable=lambda x: [e.value for e in x]), default=PaymentStatusEnum.PENDING, index=True)
    
    # Méthode de paiement
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(255), unique=True, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    doctor = relationship("DoctorProfile", back_populates="payments")
    patient = relationship("User", back_populates="payments")


class PatientDocument(Base):
    """Documents médicaux partagés avec les patients"""
    __tablename__ = "patient_documents"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    
    # Informations du document
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # en bytes
    mime_type = Column(String(100), nullable=True)
    
    # Métadonnées
    document_type = Column(String(50), nullable=True)  # prescription, certificate, report, etc.
    is_patient_visible = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    doctor = relationship("DoctorProfile", back_populates="documents")
    patient = relationship("User", back_populates="documents_received")


class DoctorSettings(Base):
    """Paramètres et préférences du médecin"""
    __tablename__ = "doctor_settings"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Notifications
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    appointment_reminders = Column(Boolean, default=True)
    
    # Visibilité
    profile_visibility = Column(String(20), default="public")  # public, private, restricted
    show_phone = Column(Boolean, default=True)
    show_email = Column(Boolean, default=True)
    
    # Préférences
    language = Column(String(5), default="fr")
    timezone = Column(String(50), default="Europe/Paris")
    
    # Paiement
    payment_enabled = Column(Boolean, default=False)
    payment_methods = Column(JSON, default=list)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
