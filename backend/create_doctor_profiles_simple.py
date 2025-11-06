"""
Script simple pour créer les profils DoctorProfile manquants
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.services.doctor_service import DoctorService
from app.schemas.doctor import DoctorProfileCreate

def create_missing_profiles():
    """Créer les profils manquants pour les docteurs existants"""
    db: Session = SessionLocal()
    
    try:
        # Trouver tous les docteurs sans profil
        doctors = db.query(User).filter(User.role == UserRole.DOCTOR).all()
        
        created_count = 0
        skipped_count = 0
        
        for doctor in doctors:
            # Vérifier si le profil existe déjà
            try:
                profile = DoctorService.get_doctor_profile(db, doctor.id)
                print(f"✓ Profil existe déjà pour {doctor.email}")
                skipped_count += 1
                continue
            except:
                pass  # Profile doesn't exist, create it
            
            # Map specialization
            specialty_map = {
                'general_practitioner': 'general_practitioner',
                'cardiologist': 'cardiologist',
                'dermatologist': 'dermatologist',
                'pediatrician': 'pediatrician',
                'gynecologist': 'gynecologist',
                'psychiatrist': 'psychiatrist',
                'ophthalmologist': 'ophthalmologist',
                'dentist': 'dentist',
                'orthopedist': 'orthopedist',
                'neurologist': 'neurologist',
                'radiologist': 'radiologist',
                'surgeon': 'surgeon',
            }
            
            specialty = 'general_practitioner'
            if doctor.specialization:
                specialty = specialty_map.get(
                    doctor.specialization.lower(), 
                    'general_practitioner'
                )
            
            # Créer le profil via le service
            profile_data = DoctorProfileCreate(
                specialty=specialty,
                rpps_number=None,  # Optional now
                sub_specialty=None,
                office_address=None,
                office_city=None,
                office_postal_code=None,
                office_phone=None,
                biography=doctor.bio or "",
                languages=doctor.languages_spoken.split(',') if doctor.languages_spoken else ["Français"],
                education=[],
                experience_years=doctor.experience_years or 0,
                consultation_types='both',
                consultation_duration=30,
                consultation_price=float(doctor.consultation_fee / 100) if doctor.consultation_fee else 50.0,
                accepts_new_patients=doctor.accepting_new_patients if doctor.accepting_new_patients is not None else True,
                is_public=False
            )
            
            try:
                profile = DoctorService.create_doctor_profile(db, doctor.id, profile_data)
                print(f"✓ Profil créé pour {doctor.email} (ID: {profile.id})")
                created_count += 1
            except Exception as e:
                print(f"✗ Erreur pour {doctor.email}: {e}")
        
        print(f"\n=== Résumé ===")
        print(f"Profils créés: {created_count}")
        print(f"Profils existants: {skipped_count}")
        print(f"Total docteurs: {len(doctors)}")
        
    except Exception as e:
        print(f"Erreur: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Création des profils DoctorProfile manquants...")
    create_missing_profiles()
    print("Terminé!")
