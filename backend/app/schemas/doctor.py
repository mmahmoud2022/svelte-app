"""
Schémas Pydantic pour le module Doctor
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict
from datetime import datetime, date, time
from app.models.doctor import (
    SpecialtyEnum,
    ConsultationTypeEnum,
    AppointmentStatusEnum,
    PaymentStatusEnum,
)


# ========== Doctor Profile Schemas ==========

class DoctorProfileBase(BaseModel):
    """Base schema pour le profil médecin"""
    specialty: SpecialtyEnum
    sub_specialty: Optional[str] = None
    rpps_number: Optional[str] = Field(None, min_length=11, max_length=11, description="Numéro RPPS (11 chiffres) - optionnel")
    
    office_address: Optional[str] = None
    office_city: Optional[str] = None
    office_postal_code: Optional[str] = None
    office_phone: Optional[str] = None
    
    biography: Optional[str] = Field(None, max_length=2000)
    languages: List[str] = Field(default_factory=list)
    education: List[Dict] = Field(default_factory=list)
    experience_years: int = Field(default=0, ge=0)
    
    consultation_types: ConsultationTypeEnum = ConsultationTypeEnum.BOTH
    consultation_duration: int = Field(default=30, ge=15, le=180)
    consultation_price: Optional[float] = Field(None, ge=0)
    accepts_new_patients: bool = True
    is_public: bool = True


class DoctorProfileCreate(DoctorProfileBase):
    """Schema pour la création d'un profil médecin"""
    pass


class DoctorProfileUpdate(BaseModel):
    """Schema pour la mise à jour d'un profil médecin"""
    specialty: Optional[SpecialtyEnum] = None
    sub_specialty: Optional[str] = None
    office_address: Optional[str] = None
    office_city: Optional[str] = None
    office_postal_code: Optional[str] = None
    office_phone: Optional[str] = None
    biography: Optional[str] = None
    languages: Optional[List[str]] = None
    education: Optional[List[Dict]] = None
    experience_years: Optional[int] = None
    consultation_types: Optional[ConsultationTypeEnum] = None
    consultation_duration: Optional[int] = Field(None, ge=15, le=180)
    consultation_price: Optional[float] = Field(None, ge=0)
    accepts_new_patients: Optional[bool] = None
    is_public: Optional[bool] = None


class DoctorProfileResponse(DoctorProfileBase):
    """Schema de réponse pour un profil médecin complet"""
    id: int
    user_id: int
    is_verified: bool
    total_consultations: int
    average_rating: float
    total_reviews: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Informations utilisateur
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


class DoctorPublicProfile(BaseModel):
    """Schema pour le profil public d'un médecin (accessible par les patients)"""
    id: int
    specialty: SpecialtyEnum
    sub_specialty: Optional[str]
    office_city: Optional[str]
    biography: Optional[str]
    languages: List[str]
    experience_years: int
    consultation_types: ConsultationTypeEnum
    consultation_duration: int
    consultation_price: Optional[float]
    accepts_new_patients: bool
    average_rating: float
    total_reviews: int
    total_consultations: int
    
    # Informations utilisateur publiques
    first_name: str
    last_name: str
    
    class Config:
        from_attributes = True


# ========== Availability Schemas ==========

class AvailabilityBase(BaseModel):
    """Base schema pour les créneaux de disponibilité récurrents"""
    day_of_week: int = Field(..., ge=0, le=6, description="Jour de la semaine (0=Dimanche, 1=Lundi, ..., 6=Samedi)")
    start_time: time
    end_time: time
    consultation_type: ConsultationTypeEnum
    is_available: bool = True

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError("L'heure de fin doit être après l'heure de début")
        return v


class AvailabilityCreate(AvailabilityBase):
    """Schema pour la création d'un créneau"""
    pass


class AvailabilityResponse(AvailabilityBase):
    """Schema de réponse pour un créneau"""
    id: int
    doctor_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Appointment Schemas ==========

class PatientInfo(BaseModel):
    """Schema pour les informations du patient"""
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    """Base schema pour les rendez-vous"""
    appointment_date: datetime
    consultation_type: ConsultationTypeEnum
    reason: Optional[str] = None
    patient_notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    """Schema pour la création d'un rendez-vous (par le patient)"""
    doctor_id: int
    availability_id: Optional[int] = None


class AppointmentUpdate(BaseModel):
    """Schema pour la mise à jour d'un rendez-vous"""
    appointment_date: Optional[datetime] = None
    consultation_type: Optional[ConsultationTypeEnum] = None
    reason: Optional[str] = None
    patient_notes: Optional[str] = None
    doctor_notes: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    """Schema pour la mise à jour du statut d'un rendez-vous"""
    status: AppointmentStatusEnum
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    """Schema de réponse pour un rendez-vous"""
    id: int
    doctor_id: int
    patient_id: int
    status: AppointmentStatusEnum
    duration: int
    price: Optional[float]
    is_paid: bool
    doctor_notes: Optional[str]
    notes: Optional[str]
    diagnosis: Optional[str]
    prescription: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Informations patient (pour le médecin)
    patient: Optional[PatientInfo] = None
    patient_first_name: Optional[str] = None
    patient_last_name: Optional[str] = None
    patient_phone: Optional[str] = None
    
    # Informations médecin (pour le patient)
    doctor_first_name: Optional[str] = None
    doctor_last_name: Optional[str] = None

    class Config:
        from_attributes = True


# ========== Review Schemas ==========

class ReviewBase(BaseModel):
    """Base schema pour les avis"""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewCreate(ReviewBase):
    """Schema pour la création d'un avis (par le patient)"""
    doctor_id: int
    appointment_id: Optional[int] = None


class ReviewResponse(ReviewBase):
    """Schema de réponse pour un avis"""
    id: int
    doctor_id: int
    patient_id: int
    doctor_response: Optional[str]
    responded_at: Optional[datetime]
    is_public: bool
    created_at: datetime
    
    # Informations patient
    patient_first_name: str
    patient_last_name: str

    class Config:
        from_attributes = True


class ReviewResponseCreate(BaseModel):
    """Schema pour la réponse d'un médecin à un avis"""
    response: str = Field(..., max_length=1000)


# ========== Message Schemas ==========

class MessageBase(BaseModel):
    """Base schema pour les messages"""
    subject: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1, max_length=5000)


class MessageCreate(MessageBase):
    """Schema pour la création d'un message"""
    recipient_id: int
    appointment_id: Optional[int] = None


class MessageResponse(MessageBase):
    """Schema de réponse pour un message"""
    id: int
    sender_id: int
    recipient_id: int
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    # Informations expéditeur
    sender_first_name: str
    sender_last_name: str
    
    # Informations destinataire
    recipient_first_name: str
    recipient_last_name: str

    class Config:
        from_attributes = True


# ========== Payment Schemas ==========

class PaymentBase(BaseModel):
    """Base schema pour les paiements"""
    amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR", max_length=3)
    payment_method: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Schema pour la création d'un paiement"""
    appointment_id: int


class PaymentResponse(PaymentBase):
    """Schema de réponse pour un paiement"""
    id: int
    doctor_id: int
    patient_id: int
    appointment_id: Optional[int]
    status: PaymentStatusEnum
    transaction_id: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]
    
    # Informations patient
    patient_first_name: str
    patient_last_name: str

    class Config:
        from_attributes = True


# ========== Document Schemas ==========

class DocumentBase(BaseModel):
    """Base schema pour les documents"""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    document_type: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Schema pour la création d'un document"""
    patient_id: int
    appointment_id: Optional[int] = None


class DocumentResponse(DocumentBase):
    """Schema de réponse pour un document"""
    id: int
    doctor_id: int
    patient_id: int
    file_name: str
    file_size: Optional[int]
    mime_type: Optional[str]
    is_patient_visible: bool
    created_at: datetime
    
    # Informations patient
    patient_first_name: str
    patient_last_name: str

    class Config:
        from_attributes = True


# ========== Settings Schemas ==========

class DoctorSettingsUpdate(BaseModel):
    """Schema pour la mise à jour des paramètres"""
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    appointment_reminders: Optional[bool] = None
    profile_visibility: Optional[str] = Field(None, pattern="^(public|private|restricted)$")
    show_phone: Optional[bool] = None
    show_email: Optional[bool] = None
    language: Optional[str] = Field(None, max_length=5)
    timezone: Optional[str] = Field(None, max_length=50)
    payment_enabled: Optional[bool] = None
    payment_methods: Optional[List[str]] = None


class DoctorSettingsResponse(BaseModel):
    """Schema de réponse pour les paramètres"""
    id: int
    doctor_id: int
    email_notifications: bool
    sms_notifications: bool
    appointment_reminders: bool
    profile_visibility: str
    show_phone: bool
    show_email: bool
    language: str
    timezone: str
    payment_enabled: bool
    payment_methods: List[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ========== Statistics Schemas ==========

class DoctorStatistics(BaseModel):
    """Schema pour les statistiques du médecin"""
    total_consultations: int
    completed_consultations: int
    cancelled_consultations: int
    no_show_consultations: int
    cancellation_rate: float
    average_rating: float
    total_reviews: int
    new_patients_count: int
    returning_patients_count: int
    total_revenue: float
    pending_revenue: float
    upcoming_appointments: int
    today_appointments: int


# ========== Patient List Schemas ==========

class PatientBasicInfo(BaseModel):
    """Schema pour les informations de base d'un patient"""
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[datetime]
    total_appointments: int
    last_appointment_date: Optional[datetime]

    class Config:
        from_attributes = True


# ========== List Response Schemas ==========

class PaginatedResponse(BaseModel):
    """Schema générique pour les réponses paginées"""
    total: int
    page: int
    page_size: int
    items: List


class AvailabilityListResponse(PaginatedResponse):
    """Réponse paginée pour les créneaux"""
    items: List[AvailabilityResponse]


class AppointmentListResponse(PaginatedResponse):
    """Réponse paginée pour les rendez-vous"""
    items: List[AppointmentResponse]


class MessageListResponse(PaginatedResponse):
    """Réponse paginée pour les messages"""
    items: List[MessageResponse]


class PaymentListResponse(PaginatedResponse):
    """Réponse paginée pour les paiements"""
    items: List[PaymentResponse]


class ReviewListResponse(PaginatedResponse):
    """Réponse paginée pour les avis"""
    items: List[ReviewResponse]


class PatientListResponse(PaginatedResponse):
    """Réponse paginée pour les patients"""
    items: List[PatientBasicInfo]
