"""
Service pour la gestion des profils et actions des médecins
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from typing import Optional, List, Tuple
from datetime import datetime, date, time, timedelta
from fastapi import HTTPException, status, UploadFile
import os
import uuid

from app.models.doctor import (
    DoctorProfile,
    DoctorAvailability,
    Appointment,
    DoctorReview,
    DoctorMessage,
    Payment,
    PatientDocument,
    DoctorSettings,
    AppointmentStatusEnum,
    PaymentStatusEnum,
)
from app.models.user import User, UserRole
from app.schemas.doctor import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    AvailabilityCreate,
    AppointmentStatusUpdate,
    MessageCreate,
    ReviewResponseCreate,
    DoctorSettingsUpdate,
    DoctorStatistics,
)


class DoctorService:
    """Service pour gérer les opérations liées aux médecins"""

    @staticmethod
    def create_doctor_profile(
        db: Session,
        user_id: int,
        profile_data: DoctorProfileCreate
    ) -> DoctorProfile:
        """Créer un profil de médecin"""
        # Vérifier que l'utilisateur existe et a le rôle doctor
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        if user.role != UserRole.DOCTOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les utilisateurs avec le rôle 'doctor' peuvent créer un profil médecin"
            )
        
        # Vérifier que le profil n'existe pas déjà
        existing_profile = db.query(DoctorProfile).filter(
            DoctorProfile.user_id == user_id
        ).first()
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un profil médecin existe déjà pour cet utilisateur"
            )
        
        # Vérifier l'unicité du numéro RPPS (uniquement si fourni)
        if profile_data.rpps_number:
            existing_rpps = db.query(DoctorProfile).filter(
                DoctorProfile.rpps_number == profile_data.rpps_number
            ).first()
            if existing_rpps:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce numéro RPPS est déjà utilisé"
                )
        
        # Créer le profil
        doctor_profile = DoctorProfile(
            user_id=user_id,
            **profile_data.model_dump()
        )
        db.add(doctor_profile)
        db.flush()  # Force l'insertion pour obtenir l'ID sans committer
        
        # Créer les paramètres par défaut (maintenant que doctor_profile.id existe)
        settings = DoctorSettings(doctor_id=doctor_profile.id)
        db.add(settings)
        
        db.commit()
        db.refresh(doctor_profile)
        return doctor_profile

    @staticmethod
    def get_doctor_profile(db: Session, user_id: int) -> DoctorProfile:
        """Obtenir le profil du médecin connecté"""
        profile = db.query(DoctorProfile).filter(
            DoctorProfile.user_id == user_id
        ).options(joinedload(DoctorProfile.user)).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil médecin non trouvé"
            )
        
        return profile

    @staticmethod
    def update_doctor_profile(
        db: Session,
        user_id: int,
        profile_data: DoctorProfileUpdate
    ) -> DoctorProfile:
        """Mettre à jour le profil du médecin (ou le créer s'il n'existe pas)"""
        # Vérifier si le profil existe déjà
        profile = db.query(DoctorProfile).filter(
            DoctorProfile.user_id == user_id
        ).first()
        
        if not profile:
            # Créer le profil s'il n'existe pas
            # Convertir DoctorProfileUpdate en DoctorProfileCreate
            from app.schemas.doctor import DoctorProfileCreate
            create_data = DoctorProfileCreate(**profile_data.model_dump(exclude_unset=True))
            return DoctorService.create_doctor_profile(db, user_id, create_data)
        
        # Mettre à jour uniquement les champs fournis
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def get_public_doctor_profile(db: Session, doctor_id: int) -> DoctorProfile:
        """Obtenir le profil public d'un médecin"""
        profile = db.query(DoctorProfile).filter(
            DoctorProfile.id == doctor_id,
            DoctorProfile.is_public == True
        ).options(joinedload(DoctorProfile.user)).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil médecin non trouvé ou non public"
            )
        
        return profile

    # ========== Gestion des disponibilités ==========

    @staticmethod
    def create_availability(
        db: Session,
        doctor_id: int,
        availability_data: AvailabilityCreate
    ) -> DoctorAvailability:
        """Créer un créneau de disponibilité"""
        # Vérifier que le médecin existe
        doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil médecin non trouvé"
            )
        
        # Vérifier qu'il n'y a pas de chevauchement
        overlapping = db.query(DoctorAvailability).filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date == availability_data.date,
            DoctorAvailability.is_available == True,
            or_(
                and_(
                    DoctorAvailability.start_time <= availability_data.start_time,
                    DoctorAvailability.end_time > availability_data.start_time
                ),
                and_(
                    DoctorAvailability.start_time < availability_data.end_time,
                    DoctorAvailability.end_time >= availability_data.end_time
                )
            )
        ).first()
        
        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce créneau chevauche une disponibilité existante"
            )
        
        availability = DoctorAvailability(
            doctor_id=doctor_id,
            **availability_data.model_dump()
        )
        db.add(availability)
        db.commit()
        db.refresh(availability)
        return availability

    @staticmethod
    def get_doctor_availabilities(
        db: Session,
        doctor_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        available_only: bool = True
    ) -> List[DoctorAvailability]:
        """Obtenir les créneaux de disponibilité d'un médecin"""
        query = db.query(DoctorAvailability).filter(
            DoctorAvailability.doctor_id == doctor_id
        )
        
        if available_only:
            query = query.filter(
                DoctorAvailability.is_available == True,
                DoctorAvailability.is_booked == False
            )
        
        if start_date:
            query = query.filter(DoctorAvailability.date >= start_date)
        
        if end_date:
            query = query.filter(DoctorAvailability.date <= end_date)
        
        return query.order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()

    @staticmethod
    def delete_availability(db: Session, doctor_id: int, availability_id: int) -> None:
        """Supprimer un créneau de disponibilité"""
        availability = db.query(DoctorAvailability).filter(
            DoctorAvailability.id == availability_id,
            DoctorAvailability.doctor_id == doctor_id
        ).first()
        
        if not availability:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Créneau non trouvé"
            )
        
        if availability.is_booked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de supprimer un créneau déjà réservé"
            )
        
        db.delete(availability)
        db.commit()

    # ========== Gestion des rendez-vous ==========

    @staticmethod
    def get_doctor_appointments(
        db: Session,
        doctor_id: int,
        status_filter: Optional[AppointmentStatusEnum] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Appointment], int]:
        """Obtenir les rendez-vous d'un médecin"""
        query = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id
        ).options(joinedload(Appointment.patient))
        
        if status_filter:
            query = query.filter(Appointment.status == status_filter)
        
        if start_date:
            query = query.filter(Appointment.appointment_date >= start_date)
        
        if end_date:
            query = query.filter(Appointment.appointment_date <= end_date)
        
        total = query.count()
        
        appointments = query.order_by(desc(Appointment.appointment_date)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return appointments, total

    @staticmethod
    def get_appointment_details(
        db: Session,
        doctor_id: int,
        appointment_id: int
    ) -> Appointment:
        """Obtenir les détails d'un rendez-vous"""
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.doctor_id == doctor_id
        ).options(joinedload(Appointment.patient)).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rendez-vous non trouvé"
            )
        
        return appointment

    @staticmethod
    def update_appointment_status(
        db: Session,
        doctor_id: int,
        appointment_id: int,
        status_update: AppointmentStatusUpdate
    ) -> Appointment:
        """Mettre à jour le statut d'un rendez-vous"""
        appointment = DoctorService.get_appointment_details(db, doctor_id, appointment_id)
        
        old_status = appointment.status
        appointment.status = status_update.status
        
        if status_update.doctor_notes:
            appointment.doctor_notes = status_update.doctor_notes
        
        # Mettre à jour les timestamps
        if status_update.status == AppointmentStatusEnum.COMPLETED:
            appointment.completed_at = datetime.utcnow()
            # Incrémenter le compteur de consultations
            doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
            if doctor:
                doctor.total_consultations += 1
        elif status_update.status == AppointmentStatusEnum.CANCELLED:
            appointment.cancelled_at = datetime.utcnow()
            # Libérer le créneau si applicable
            if appointment.availability_id:
                availability = db.query(DoctorAvailability).filter(
                    DoctorAvailability.id == appointment.availability_id
                ).first()
                if availability:
                    availability.is_booked = False
        
        db.commit()
        db.refresh(appointment)
        return appointment

    # ========== Gestion des patients ==========

    @staticmethod
    def get_doctor_patients(
        db: Session,
        doctor_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[dict], int]:
        """Obtenir la liste des patients suivis par un médecin"""
        # Sous-requête pour compter les rendez-vous par patient
        subquery = db.query(
            Appointment.patient_id,
            func.count(Appointment.id).label('total_appointments'),
            func.max(Appointment.appointment_date).label('last_appointment_date')
        ).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status.in_([AppointmentStatusEnum.COMPLETED, AppointmentStatusEnum.CONFIRMED])
        ).group_by(Appointment.patient_id).subquery()
        
        # Requête principale
        query = db.query(
            User,
            subquery.c.total_appointments,
            subquery.c.last_appointment_date
        ).join(
            subquery, User.id == subquery.c.patient_id
        )
        
        total = query.count()
        
        results = query.order_by(desc(subquery.c.last_appointment_date)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        patients = []
        for user, total_appts, last_appt_date in results:
            patients.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "date_of_birth": user.date_of_birth,
                "total_appointments": total_appts or 0,
                "last_appointment_date": last_appt_date
            })
        
        return patients, total

    @staticmethod
    def get_patient_medical_record(
        db: Session,
        doctor_id: int,
        patient_id: int
    ) -> dict:
        """Obtenir le dossier médical d'un patient"""
        # Vérifier que le patient a bien consulté ce médecin
        has_consulted = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.patient_id == patient_id
        ).first()
        
        if not has_consulted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas accès au dossier de ce patient"
            )
        
        # Récupérer le patient
        patient = db.query(User).filter(User.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient non trouvé"
            )
        
        # Récupérer l'historique des rendez-vous
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.patient_id == patient_id
        ).order_by(desc(Appointment.appointment_date)).all()
        
        # Récupérer les documents
        documents = db.query(PatientDocument).filter(
            PatientDocument.doctor_id == doctor_id,
            PatientDocument.patient_id == patient_id
        ).order_by(desc(PatientDocument.created_at)).all()
        
        return {
            "patient": patient,
            "appointments": appointments,
            "documents": documents,
            "total_consultations": len([a for a in appointments if a.status == AppointmentStatusEnum.COMPLETED])
        }

    # ========== Statistiques ==========

    @staticmethod
    def get_doctor_statistics(db: Session, doctor_id: int) -> DoctorStatistics:
        """Générer les statistiques d'activité du médecin"""
        doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil médecin non trouvé"
            )
        
        # Compter les consultations par statut
        completed = db.query(func.count(Appointment.id)).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatusEnum.COMPLETED
        ).scalar() or 0
        
        cancelled = db.query(func.count(Appointment.id)).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatusEnum.CANCELLED
        ).scalar() or 0
        
        no_show = db.query(func.count(Appointment.id)).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatusEnum.NO_SHOW
        ).scalar() or 0
        
        total = completed + cancelled + no_show
        cancellation_rate = (cancelled + no_show) / total * 100 if total > 0 else 0
        
        # Patients nouveaux vs récurrents
        total_patients = db.query(func.count(func.distinct(Appointment.patient_id))).filter(
            Appointment.doctor_id == doctor_id
        ).scalar() or 0
        
        # Patients avec plus d'un rendez-vous
        returning_patients = db.query(func.count(func.distinct(Appointment.patient_id))).filter(
            Appointment.doctor_id == doctor_id
        ).group_by(Appointment.patient_id).having(
            func.count(Appointment.id) > 1
        ).count()
        
        new_patients = total_patients - returning_patients
        
        # Revenus
        total_revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.doctor_id == doctor_id,
            Payment.status == PaymentStatusEnum.COMPLETED
        ).scalar() or 0
        
        pending_revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.doctor_id == doctor_id,
            Payment.status == PaymentStatusEnum.PENDING
        ).scalar() or 0
        
        # Rendez-vous à venir
        now = datetime.utcnow()
        today_start = datetime.combine(date.today(), time.min)
        today_end = datetime.combine(date.today(), time.max)
        
        upcoming_appointments = db.query(func.count(Appointment.id)).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date > now,
            Appointment.status.in_([AppointmentStatusEnum.PENDING, AppointmentStatusEnum.CONFIRMED])
        ).scalar() or 0
        
        today_appointments = db.query(func.count(Appointment.id)).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date.between(today_start, today_end),
            Appointment.status.in_([AppointmentStatusEnum.PENDING, AppointmentStatusEnum.CONFIRMED])
        ).scalar() or 0
        
        return DoctorStatistics(
            total_consultations=total,
            completed_consultations=completed,
            cancelled_consultations=cancelled,
            no_show_consultations=no_show,
            cancellation_rate=round(cancellation_rate, 2),
            average_rating=doctor.average_rating,
            total_reviews=doctor.total_reviews,
            new_patients_count=new_patients,
            returning_patients_count=returning_patients,
            total_revenue=total_revenue,
            pending_revenue=pending_revenue,
            upcoming_appointments=upcoming_appointments,
            today_appointments=today_appointments
        )

    # ========== Messages ==========

    @staticmethod
    def get_doctor_messages(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[DoctorMessage], int]:
        """Obtenir les messages du médecin"""
        query = db.query(DoctorMessage).filter(
            or_(
                DoctorMessage.sender_id == user_id,
                DoctorMessage.recipient_id == user_id
            )
        ).options(
            joinedload(DoctorMessage.sender),
            joinedload(DoctorMessage.recipient)
        )
        
        total = query.count()
        
        messages = query.order_by(desc(DoctorMessage.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return messages, total

    @staticmethod
    def send_message(
        db: Session,
        sender_id: int,
        message_data: MessageCreate
    ) -> DoctorMessage:
        """Envoyer un message"""
        # Vérifier que le destinataire existe
        recipient = db.query(User).filter(User.id == message_data.recipient_id).first()
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destinataire non trouvé"
            )
        
        message = DoctorMessage(
            sender_id=sender_id,
            **message_data.model_dump()
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Charger les relations
        db.refresh(message)
        message.sender
        message.recipient
        
        return message

    # ========== Avis ==========

    @staticmethod
    def get_doctor_reviews(
        db: Session,
        doctor_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[DoctorReview], int]:
        """Obtenir les avis d'un médecin"""
        query = db.query(DoctorReview).filter(
            DoctorReview.doctor_id == doctor_id,
            DoctorReview.is_public == True
        ).options(joinedload(DoctorReview.patient))
        
        total = query.count()
        
        reviews = query.order_by(desc(DoctorReview.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return reviews, total

    @staticmethod
    def respond_to_review(
        db: Session,
        doctor_id: int,
        review_id: int,
        response_data: ReviewResponseCreate
    ) -> DoctorReview:
        """Répondre à un avis"""
        review = db.query(DoctorReview).filter(
            DoctorReview.id == review_id,
            DoctorReview.doctor_id == doctor_id
        ).first()
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Avis non trouvé"
            )
        
        review.doctor_response = response_data.response
        review.responded_at = datetime.utcnow()
        
        db.commit()
        db.refresh(review)
        return review

    # ========== Paiements ==========

    @staticmethod
    def get_doctor_payments(
        db: Session,
        doctor_id: int,
        status_filter: Optional[PaymentStatusEnum] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Payment], int]:
        """Obtenir l'historique des paiements"""
        query = db.query(Payment).filter(
            Payment.doctor_id == doctor_id
        ).options(joinedload(Payment.patient))
        
        if status_filter:
            query = query.filter(Payment.status == status_filter)
        
        total = query.count()
        
        payments = query.order_by(desc(Payment.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return payments, total

    # ========== Documents ==========

    @staticmethod
    async def upload_patient_document(
        db: Session,
        doctor_id: int,
        patient_id: int,
        file: UploadFile,
        title: str,
        description: Optional[str] = None,
        document_type: Optional[str] = None,
        appointment_id: Optional[int] = None
    ) -> PatientDocument:
        """Uploader un document pour un patient"""
        # Vérifier que le patient existe et a consulté ce médecin
        has_consulted = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.patient_id == patient_id
        ).first()
        
        if not has_consulted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez envoyer des documents qu'à vos patients"
            )
        
        # Créer le dossier uploads si nécessaire
        upload_dir = "uploads/documents"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Générer un nom de fichier unique
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Sauvegarder le fichier
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Créer l'entrée en base de données
        document = PatientDocument(
            doctor_id=doctor_id,
            patient_id=patient_id,
            appointment_id=appointment_id,
            title=title,
            description=description,
            file_path=file_path,
            file_name=file.filename,
            file_size=len(content),
            mime_type=file.content_type,
            document_type=document_type
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document

    # ========== Paramètres ==========

    @staticmethod
    def get_doctor_settings(db: Session, doctor_id: int) -> DoctorSettings:
        """Obtenir les paramètres du médecin"""
        settings = db.query(DoctorSettings).filter(
            DoctorSettings.doctor_id == doctor_id
        ).first()
        
        if not settings:
            # Créer des paramètres par défaut si inexistants
            settings = DoctorSettings(doctor_id=doctor_id)
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return settings

    @staticmethod
    def update_doctor_settings(
        db: Session,
        doctor_id: int,
        settings_data: DoctorSettingsUpdate
    ) -> DoctorSettings:
        """Mettre à jour les paramètres du médecin"""
        settings = DoctorService.get_doctor_settings(db, doctor_id)
        
        update_data = settings_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)
        
        db.commit()
        db.refresh(settings)
        return settings
