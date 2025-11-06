"""
Endpoints pour le module Doctor
Routes pour la gestion des profils, disponibilités, rendez-vous, messages, avis, etc.
"""
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.doctor import AppointmentStatusEnum, PaymentStatusEnum
from app.services.doctor_service import DoctorService
from app.schemas.doctor import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileResponse,
    DoctorPublicProfile,
    AvailabilityCreate,
    AvailabilityResponse,
    AppointmentResponse,
    AppointmentStatusUpdate,
    MessageCreate,
    MessageResponse,
    ReviewResponse,
    ReviewResponseCreate,
    PaymentResponse,
    DocumentResponse,
    DoctorSettingsUpdate,
    DoctorSettingsResponse,
    DoctorStatistics,
    PatientBasicInfo,
    AppointmentListResponse,
    MessageListResponse,
    ReviewListResponse,
    PaymentListResponse,
    PatientListResponse,
)

router = APIRouter(prefix="/doctors", tags=["doctors"])


# ========== 1️⃣ Créer un profil praticien ==========
@router.post("/", response_model=DoctorProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor_profile(
    profile_data: DoctorProfileCreate,
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Créer un profil professionnel pour un médecin.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.create_doctor_profile(db, current_user.id, profile_data)
    
    # Enrichir avec les données utilisateur
    response = DoctorProfileResponse.model_validate(profile)
    response.first_name = current_user.first_name
    response.last_name = current_user.last_name
    response.email = current_user.email
    
    return response


# ========== 2️⃣ Obtenir le profil du médecin connecté ==========
@router.get("/me", response_model=DoctorProfileResponse)
async def get_my_doctor_profile(
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Obtenir le profil professionnel du médecin connecté.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    
    # Enrichir avec les données utilisateur
    response = DoctorProfileResponse.model_validate(profile)
    response.first_name = current_user.first_name
    response.last_name = current_user.last_name
    response.email = current_user.email
    
    return response


# ========== 3️⃣ Mettre à jour le profil du médecin ==========
@router.put("/me", response_model=DoctorProfileResponse)
async def update_my_doctor_profile(
    profile_data: DoctorProfileUpdate,
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour le profil professionnel du médecin connecté.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.update_doctor_profile(db, current_user.id, profile_data)
    
    # Enrichir avec les données utilisateur
    response = DoctorProfileResponse.model_validate(profile)
    response.first_name = current_user.first_name
    response.last_name = current_user.last_name
    response.email = current_user.email
    
    return response


# ========== 6️⃣ Créer un créneau de disponibilité ==========
@router.post("/availability", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_availability(
    availability_data: AvailabilityCreate,
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Créer un créneau de disponibilité dans l'agenda.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    availability = DoctorService.create_availability(db, profile.id, availability_data)
    return AvailabilityResponse.model_validate(availability)


# ========== 7️⃣ Supprimer un créneau de disponibilité ==========
@router.delete("/availability/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_availability(
    availability_id: int,
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Supprimer un créneau de disponibilité non réservé.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    DoctorService.delete_availability(db, profile.id, availability_id)
    return None


# ========== 8️⃣ Liste des rendez-vous du médecin ==========
@router.get("/appointments", response_model=AppointmentListResponse)
async def get_my_appointments(
    status_filter: Optional[AppointmentStatusEnum] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Obtenir la liste des rendez-vous du médecin connecté.
    
    Filtres disponibles : statut, date de début, date de fin.
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    appointments, total = DoctorService.get_doctor_appointments(
        db, profile.id, status_filter, start_date, end_date, page, page_size
    )
    
    # Enrichir avec les données patient
    items = []
    for appt in appointments:
        response = AppointmentResponse.model_validate(appt)
        # Créer l'objet patient pour le frontend
        if appt.patient:
            from app.schemas.doctor import PatientInfo
            response.patient = PatientInfo(
                id=appt.patient.id,
                email=appt.patient.email,
                full_name=appt.patient.full_name,
                phone=appt.patient.phone
            )
        # Garder aussi les champs individuels pour compatibilité
        response.patient_first_name = appt.patient.first_name
        response.patient_last_name = appt.patient.last_name
        response.patient_phone = appt.patient.phone
        items.append(response)
    
    return AppointmentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


# ========== 9️⃣ Détails d'un rendez-vous ==========
@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment_details(
    appointment_id: int,
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Obtenir les détails d'un rendez-vous spécifique.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    appointment = DoctorService.get_appointment_details(db, profile.id, appointment_id)
    
    # Enrichir avec les données patient
    response = AppointmentResponse.model_validate(appointment)
    if appointment.patient:
        from app.schemas.doctor import PatientInfo
        response.patient = PatientInfo(
            id=appointment.patient.id,
            email=appointment.patient.email,
            full_name=appointment.patient.full_name,
            phone=appointment.patient.phone
        )
    response.patient_first_name = appointment.patient.first_name
    response.patient_last_name = appointment.patient.last_name
    response.patient_phone = appointment.patient.phone
    
    return response


# ========== 🔟 Modifier le statut d'un rendez-vous ==========
@router.patch("/appointments/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: int,
    status_update: AppointmentStatusUpdate,
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Modifier le statut d'un rendez-vous (confirmé, terminé, annulé, absent).
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    appointment = DoctorService.update_appointment_status(
        db, profile.id, appointment_id, status_update
    )
    
    # Enrichir avec les données patient
    response = AppointmentResponse.model_validate(appointment)
    if appointment.patient:
        from app.schemas.doctor import PatientInfo
        response.patient = PatientInfo(
            id=appointment.patient.id,
            email=appointment.patient.email,
            full_name=appointment.patient.full_name,
            phone=appointment.patient.phone
        )
    response.patient_first_name = appointment.patient.first_name
    response.patient_last_name = appointment.patient.last_name
    response.patient_phone = appointment.patient.phone
    
    return response


# ========== 11️⃣ Liste des patients suivis ==========
@router.get("/patients", response_model=PatientListResponse)
async def get_my_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Obtenir la liste des patients ayant consulté le médecin.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    patients, total = DoctorService.get_doctor_patients(db, profile.id, page, page_size)
    
    items = [PatientBasicInfo(**patient) for patient in patients]
    
    return PatientListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


# ========== 12️⃣ Dossier médical d'un patient ==========
@router.get("/patients/{patient_id}", response_model=dict)
async def get_patient_medical_record(
    patient_id: int,
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Obtenir le dossier médical complet d'un patient.
    
    Nécessite le rôle DOCTOR et que le patient ait consulté ce médecin.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    record = DoctorService.get_patient_medical_record(db, profile.id, patient_id)
    
    return {
        "patient": {
            "id": record["patient"].id,
            "first_name": record["patient"].first_name,
            "last_name": record["patient"].last_name,
            "email": record["patient"].email,
            "phone": record["patient"].phone,
            "date_of_birth": record["patient"].date_of_birth,
            "gender": record["patient"].gender,
            "address_line1": record["patient"].address_line1,
            "city": record["patient"].city,
            "postal_code": record["patient"].postal_code,
        },
        "appointments": [AppointmentResponse.model_validate(a) for a in record["appointments"]],
        "documents": [DocumentResponse.model_validate(d) for d in record["documents"]],
        "total_consultations": record["total_consultations"]
    }


# ========== 13️⃣ Statistiques d'activité ==========
@router.get("/statistics", response_model=DoctorStatistics)
async def get_my_statistics(
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Obtenir les statistiques d'activité du médecin.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    statistics = DoctorService.get_doctor_statistics(db, profile.id)
    return statistics


# ========== 14️⃣ Configurations du compte ==========
@router.put("/settings", response_model=DoctorSettingsResponse)
async def update_my_settings(
    settings_data: DoctorSettingsUpdate,
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour les paramètres et préférences du compte.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    settings = DoctorService.update_doctor_settings(db, profile.id, settings_data)
    return DoctorSettingsResponse.model_validate(settings)


@router.get("/settings", response_model=DoctorSettingsResponse)
async def get_my_settings(
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Obtenir les paramètres actuels du compte.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    settings = DoctorService.get_doctor_settings(db, profile.id)
    return DoctorSettingsResponse.model_validate(settings)


# ========== 15️⃣ Envoyer un document patient ==========
@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_patient_document(
    patient_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    appointment_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Uploader un document médical pour un patient.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    document = await DoctorService.upload_patient_document(
        db, profile.id, patient_id, file, title, description, document_type, appointment_id
    )
    
    # Enrichir avec les données patient
    patient = db.query(User).filter(User.id == patient_id).first()
    response = DocumentResponse.model_validate(document)
    response.patient_first_name = patient.first_name
    response.patient_last_name = patient.last_name
    
    return response


# ========== 16️⃣ Boîte de messagerie ==========
@router.get("/messages", response_model=MessageListResponse)
async def get_my_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Obtenir la liste des messages reçus et envoyés.
    
    Nécessite le rôle DOCTOR.
    """
    messages, total = DoctorService.get_doctor_messages(db, current_user.id, page, page_size)
    
    # Enrichir avec les données utilisateur
    items = []
    for msg in messages:
        response = MessageResponse.model_validate(msg)
        response.sender_first_name = msg.sender.first_name
        response.sender_last_name = msg.sender.last_name
        response.recipient_first_name = msg.recipient.first_name
        response.recipient_last_name = msg.recipient.last_name
        items.append(response)
    
    return MessageListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


# ========== 17️⃣ Envoyer un message ==========
@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Envoyer un message sécurisé à un patient.
    
    Nécessite le rôle DOCTOR.
    """
    message = DoctorService.send_message(db, current_user.id, message_data)
    
    # Enrichir avec les données utilisateur
    response = MessageResponse.model_validate(message)
    response.sender_first_name = message.sender.first_name
    response.sender_last_name = message.sender.last_name
    response.recipient_first_name = message.recipient.first_name
    response.recipient_last_name = message.recipient.last_name
    
    return response


# ========== 18️⃣ Historique des paiements ==========
@router.get("/payments", response_model=PaymentListResponse)
async def get_my_payments(
    status_filter: Optional[PaymentStatusEnum] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Obtenir l'historique des paiements reçus.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    payments, total = DoctorService.get_doctor_payments(
        db, profile.id, status_filter, page, page_size
    )
    
    # Enrichir avec les données patient
    items = []
    for payment in payments:
        response = PaymentResponse.model_validate(payment)
        response.patient_first_name = payment.patient.first_name
        response.patient_last_name = payment.patient.last_name
        items.append(response)
    
    return PaymentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


# ========== 19️⃣ Avis patients ==========
@router.get("/reviews", response_model=ReviewListResponse)
async def get_my_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Obtenir les avis et notes reçus des patients.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    reviews, total = DoctorService.get_doctor_reviews(db, profile.id, page, page_size)
    
    # Enrichir avec les données patient
    items = []
    for review in reviews:
        response = ReviewResponse.model_validate(review)
        response.patient_first_name = review.patient.first_name
        response.patient_last_name = review.patient.last_name
        items.append(response)
    
    return ReviewListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


# ========== 20️⃣ Répondre à un avis ==========
@router.post("/reviews/{review_id}/respond", response_model=ReviewResponse)
async def respond_to_review(
    review_id: int,
    response_data: ReviewResponseCreate,
    current_user: User = Depends(require_role([UserRole.DOCTOR])),
    db: Session = Depends(get_db)
):
    """
    Répondre à un avis patient.
    
    Nécessite le rôle DOCTOR.
    """
    profile = DoctorService.get_doctor_profile(db, current_user.id)
    review = DoctorService.respond_to_review(db, profile.id, review_id, response_data)
    
    # Enrichir avec les données patient
    db.refresh(review)
    response = ReviewResponse.model_validate(review)
    response.patient_first_name = review.patient.first_name
    response.patient_last_name = review.patient.last_name
    
    return response


# ========== 4️⃣ Consulter un profil public de médecin (DOIT ÊTRE EN DERNIER) ==========
@router.get("/{doctor_id}", response_model=DoctorPublicProfile)
async def get_doctor_public_profile(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Consulter le profil public d'un médecin.
    
    Accessible par tous les utilisateurs authentifiés.
    ⚠️ Cette route DOIT être définie en dernier car elle capture tous les IDs.
    """
    profile = DoctorService.get_public_doctor_profile(db, doctor_id)
    
    # Créer la réponse avec les données publiques
    return DoctorPublicProfile(
        id=profile.id,
        specialty=profile.specialty,
        sub_specialty=profile.sub_specialty,
        office_city=profile.office_city,
        biography=profile.biography,
        languages=profile.languages,
        experience_years=profile.experience_years,
        consultation_types=profile.consultation_types,
        consultation_duration=profile.consultation_duration,
        consultation_price=profile.consultation_price,
        accepts_new_patients=profile.accepts_new_patients,
        average_rating=profile.average_rating,
        total_reviews=profile.total_reviews,
        total_consultations=profile.total_consultations,
        first_name=profile.user.first_name,
        last_name=profile.user.last_name
    )


# ========== 5️⃣ Voir les créneaux disponibles d'un médecin ==========
@router.get("/{doctor_id}/availability", response_model=List[AvailabilityResponse])
async def get_doctor_availability(
    doctor_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtenir les créneaux disponibles d'un médecin.
    
    Accessible par tous les utilisateurs authentifiés.
    """
    availabilities = DoctorService.get_doctor_availabilities(
        db, doctor_id, start_date, end_date, available_only=True
    )
    return [AvailabilityResponse.model_validate(av) for av in availabilities]
