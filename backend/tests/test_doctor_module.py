"""
Tests unitaires pour le module Doctor
"""
import pytest
from datetime import date, time, datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User, UserRole
from app.models.doctor import (
    DoctorProfile,
    DoctorAvailability,
    Appointment,
    SpecialtyEnum,
    ConsultationTypeEnum,
    AppointmentStatusEnum,
)
from app.services.doctor_service import DoctorService
from app.schemas.doctor import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    AvailabilityCreate,
    AppointmentStatusUpdate,
)


class TestDoctorProfile:
    """Tests pour la gestion des profils médecins"""
    
    def test_create_doctor_profile_success(self, db: Session, doctor_user: User):
        """Test de création d'un profil médecin"""
        profile_data = DoctorProfileCreate(
            specialty=SpecialtyEnum.CARDIOLOGIST,
            rpps_number="12345678901",
            office_city="Paris",
            biography="Test biography",
            languages=["français", "anglais"],
            education=[],
            experience_years=10,
            consultation_price=50.0
        )
        
        profile = DoctorService.create_doctor_profile(db, doctor_user.id, profile_data)
        
        assert profile.id is not None
        assert profile.user_id == doctor_user.id
        assert profile.specialty == SpecialtyEnum.CARDIOLOGIST
        assert profile.rpps_number == "12345678901"
    
    def test_create_duplicate_rpps_fails(self, db: Session, doctor_user: User, another_doctor_user: User):
        """Test qu'on ne peut pas créer deux profils avec le même RPPS"""
        profile_data = DoctorProfileCreate(
            specialty=SpecialtyEnum.CARDIOLOGIST,
            rpps_number="12345678901",
            office_city="Paris",
            biography="Test",
            languages=["français"],
            education=[],
            experience_years=5,
            consultation_price=50.0
        )
        
        # Créer le premier profil
        DoctorService.create_doctor_profile(db, doctor_user.id, profile_data)
        
        # Tenter de créer un second profil avec le même RPPS
        with pytest.raises(HTTPException) as exc_info:
            DoctorService.create_doctor_profile(db, another_doctor_user.id, profile_data)
        
        assert exc_info.value.status_code == 400
        assert "RPPS" in str(exc_info.value.detail)
    
    def test_create_profile_requires_doctor_role(self, db: Session, patient_user: User):
        """Test qu'un patient ne peut pas créer un profil médecin"""
        profile_data = DoctorProfileCreate(
            specialty=SpecialtyEnum.CARDIOLOGIST,
            rpps_number="12345678901",
            office_city="Paris",
            biography="Test",
            languages=["français"],
            education=[],
            experience_years=5,
            consultation_price=50.0
        )
        
        with pytest.raises(HTTPException) as exc_info:
            DoctorService.create_doctor_profile(db, patient_user.id, profile_data)
        
        assert exc_info.value.status_code == 403
    
    def test_update_doctor_profile(self, db: Session, doctor_profile: DoctorProfile):
        """Test de mise à jour d'un profil"""
        update_data = DoctorProfileUpdate(
            biography="Updated biography",
            consultation_price=60.0,
            accepts_new_patients=False
        )
        
        updated_profile = DoctorService.update_doctor_profile(
            db, doctor_profile.user_id, update_data
        )
        
        assert updated_profile.biography == "Updated biography"
        assert updated_profile.consultation_price == 60.0
        assert updated_profile.accepts_new_patients is False
    
    def test_get_public_profile(self, db: Session, doctor_profile: DoctorProfile):
        """Test de récupération d'un profil public"""
        profile = DoctorService.get_public_doctor_profile(db, doctor_profile.id)
        
        assert profile.id == doctor_profile.id
        assert profile.is_public is True


class TestDoctorAvailability:
    """Tests pour la gestion des disponibilités"""
    
    def test_create_availability(self, db: Session, doctor_profile: DoctorProfile):
        """Test de création d'un créneau"""
        tomorrow = date.today() + timedelta(days=1)
        availability_data = AvailabilityCreate(
            date=tomorrow,
            start_time=time(9, 0),
            end_time=time(9, 30),
            consultation_type=ConsultationTypeEnum.IN_PERSON,
            location="Cabinet Paris"
        )
        
        availability = DoctorService.create_availability(
            db, doctor_profile.id, availability_data
        )
        
        assert availability.id is not None
        assert availability.doctor_id == doctor_profile.id
        assert availability.is_available is True
        assert availability.is_booked is False
    
    def test_create_overlapping_availability_fails(self, db: Session, doctor_profile: DoctorProfile):
        """Test qu'on ne peut pas créer de créneaux chevauchants"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Créer un premier créneau
        availability_data1 = AvailabilityCreate(
            date=tomorrow,
            start_time=time(9, 0),
            end_time=time(10, 0),
            consultation_type=ConsultationTypeEnum.IN_PERSON
        )
        DoctorService.create_availability(db, doctor_profile.id, availability_data1)
        
        # Tenter de créer un créneau chevauchant
        availability_data2 = AvailabilityCreate(
            date=tomorrow,
            start_time=time(9, 30),
            end_time=time(10, 30),
            consultation_type=ConsultationTypeEnum.IN_PERSON
        )
        
        with pytest.raises(HTTPException) as exc_info:
            DoctorService.create_availability(db, doctor_profile.id, availability_data2)
        
        assert exc_info.value.status_code == 400
        assert "chevauche" in str(exc_info.value.detail).lower()
    
    def test_get_doctor_availabilities(self, db: Session, doctor_profile: DoctorProfile):
        """Test de récupération des créneaux"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Créer plusieurs créneaux
        for hour in [9, 10, 11]:
            availability_data = AvailabilityCreate(
                date=tomorrow,
                start_time=time(hour, 0),
                end_time=time(hour, 30),
                consultation_type=ConsultationTypeEnum.IN_PERSON
            )
            DoctorService.create_availability(db, doctor_profile.id, availability_data)
        
        # Récupérer les créneaux
        availabilities = DoctorService.get_doctor_availabilities(
            db, doctor_profile.id, start_date=tomorrow, end_date=tomorrow
        )
        
        assert len(availabilities) == 3
    
    def test_delete_availability(self, db: Session, doctor_profile: DoctorProfile):
        """Test de suppression d'un créneau"""
        tomorrow = date.today() + timedelta(days=1)
        availability_data = AvailabilityCreate(
            date=tomorrow,
            start_time=time(9, 0),
            end_time=time(9, 30),
            consultation_type=ConsultationTypeEnum.IN_PERSON
        )
        
        availability = DoctorService.create_availability(
            db, doctor_profile.id, availability_data
        )
        
        # Supprimer le créneau
        DoctorService.delete_availability(db, doctor_profile.id, availability.id)
        
        # Vérifier qu'il n'existe plus
        availabilities = DoctorService.get_doctor_availabilities(
            db, doctor_profile.id, start_date=tomorrow, end_date=tomorrow
        )
        assert len(availabilities) == 0
    
    def test_cannot_delete_booked_availability(self, db: Session, doctor_profile: DoctorProfile):
        """Test qu'on ne peut pas supprimer un créneau réservé"""
        tomorrow = date.today() + timedelta(days=1)
        availability_data = AvailabilityCreate(
            date=tomorrow,
            start_time=time(9, 0),
            end_time=time(9, 30),
            consultation_type=ConsultationTypeEnum.IN_PERSON
        )
        
        availability = DoctorService.create_availability(
            db, doctor_profile.id, availability_data
        )
        
        # Marquer comme réservé
        availability.is_booked = True
        db.commit()
        
        # Tenter de supprimer
        with pytest.raises(HTTPException) as exc_info:
            DoctorService.delete_availability(db, doctor_profile.id, availability.id)
        
        assert exc_info.value.status_code == 400


class TestAppointments:
    """Tests pour la gestion des rendez-vous"""
    
    def test_get_doctor_appointments(self, db: Session, doctor_profile: DoctorProfile, appointment: Appointment):
        """Test de récupération des rendez-vous"""
        appointments, total = DoctorService.get_doctor_appointments(
            db, doctor_profile.id
        )
        
        assert total >= 1
        assert len(appointments) >= 1
        assert appointments[0].doctor_id == doctor_profile.id
    
    def test_get_appointment_details(self, db: Session, doctor_profile: DoctorProfile, appointment: Appointment):
        """Test de récupération des détails d'un rendez-vous"""
        details = DoctorService.get_appointment_details(
            db, doctor_profile.id, appointment.id
        )
        
        assert details.id == appointment.id
        assert details.doctor_id == doctor_profile.id
    
    def test_update_appointment_status(self, db: Session, doctor_profile: DoctorProfile, appointment: Appointment):
        """Test de mise à jour du statut d'un rendez-vous"""
        status_update = AppointmentStatusUpdate(
            status=AppointmentStatusEnum.COMPLETED,
            doctor_notes="Consultation terminée avec succès"
        )
        
        updated = DoctorService.update_appointment_status(
            db, doctor_profile.id, appointment.id, status_update
        )
        
        assert updated.status == AppointmentStatusEnum.COMPLETED
        assert updated.doctor_notes == "Consultation terminée avec succès"
        assert updated.completed_at is not None
    
    def test_completed_appointment_increments_counter(self, db: Session, doctor_profile: DoctorProfile, appointment: Appointment):
        """Test que marquer un RDV comme terminé incrémente le compteur"""
        initial_count = doctor_profile.total_consultations
        
        status_update = AppointmentStatusUpdate(
            status=AppointmentStatusEnum.COMPLETED
        )
        
        DoctorService.update_appointment_status(
            db, doctor_profile.id, appointment.id, status_update
        )
        
        db.refresh(doctor_profile)
        assert doctor_profile.total_consultations == initial_count + 1


class TestDoctorStatistics:
    """Tests pour les statistiques"""
    
    def test_get_statistics(self, db: Session, doctor_profile: DoctorProfile):
        """Test de récupération des statistiques"""
        stats = DoctorService.get_doctor_statistics(db, doctor_profile.id)
        
        assert stats.total_consultations >= 0
        assert stats.average_rating >= 0
        assert stats.cancellation_rate >= 0
        assert stats.total_revenue >= 0


class TestDoctorPatients:
    """Tests pour la gestion des patients"""
    
    def test_get_doctor_patients(self, db: Session, doctor_profile: DoctorProfile, appointment: Appointment):
        """Test de récupération de la liste des patients"""
        patients, total = DoctorService.get_doctor_patients(db, doctor_profile.id)
        
        assert total >= 1
        assert len(patients) >= 1
    
    def test_get_patient_medical_record(self, db: Session, doctor_profile: DoctorProfile, appointment: Appointment):
        """Test de récupération du dossier médical"""
        record = DoctorService.get_patient_medical_record(
            db, doctor_profile.id, appointment.patient_id
        )
        
        assert record["patient"].id == appointment.patient_id
        assert len(record["appointments"]) >= 1
        assert record["total_consultations"] >= 0
    
    def test_cannot_access_non_patient_record(self, db: Session, doctor_profile: DoctorProfile, patient_user: User):
        """Test qu'on ne peut pas accéder au dossier d'un non-patient"""
        with pytest.raises(HTTPException) as exc_info:
            DoctorService.get_patient_medical_record(
                db, doctor_profile.id, patient_user.id
            )
        
        assert exc_info.value.status_code == 403


# Fixtures pytest
@pytest.fixture
def doctor_user(db: Session):
    """Créer un utilisateur médecin de test"""
    user = User(
        email="doctor@test.com",
        hashed_password="hashed_password",
        first_name="John",
        last_name="Doe",
        role=UserRole.DOCTOR,
        is_active=True,
        is_verified=True,
        admin_approved=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def another_doctor_user(db: Session):
    """Créer un autre utilisateur médecin"""
    user = User(
        email="doctor2@test.com",
        hashed_password="hashed_password",
        first_name="Jane",
        last_name="Smith",
        role=UserRole.DOCTOR,
        is_active=True,
        is_verified=True,
        admin_approved=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def patient_user(db: Session):
    """Créer un utilisateur patient de test"""
    user = User(
        email="patient@test.com",
        hashed_password="hashed_password",
        first_name="Marie",
        last_name="Martin",
        role=UserRole.PATIENT,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def doctor_profile(db: Session, doctor_user: User):
    """Créer un profil médecin de test"""
    profile = DoctorProfile(
        user_id=doctor_user.id,
        specialty=SpecialtyEnum.CARDIOLOGIST,
        rpps_number="12345678901",
        office_city="Paris",
        biography="Test doctor",
        languages=["français"],
        education=[],
        experience_years=10,
        consultation_price=50.0,
        is_public=True
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@pytest.fixture
def appointment(db: Session, doctor_profile: DoctorProfile, patient_user: User):
    """Créer un rendez-vous de test"""
    tomorrow = datetime.now() + timedelta(days=1)
    appointment = Appointment(
        doctor_id=doctor_profile.id,
        patient_id=patient_user.id,
        appointment_date=tomorrow,
        consultation_type=ConsultationTypeEnum.IN_PERSON,
        status=AppointmentStatusEnum.PENDING,
        duration=30,
        reason="Consultation de routine"
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
