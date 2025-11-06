"""
Script pour créer automatiquement les profils DoctorProfile manquants
pour les utilisateurs avec le rôle DOCTOR
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.doctor import DoctorProfile, DoctorSettings, SpecialtyEnum, ConsultationTypeEnum

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
            existing_profile = db.query(DoctorProfile).filter(
                DoctorProfile.user_id == doctor.id
            ).first()
            
            if existing_profile:
                print(f"✓ Profil existe déjà pour {doctor.email}")
                skipped_count += 1
                continue
            
            # Map specialization to enum value (lowercase)
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
            
            specialty_enum = 'general_practitioner'  # Default
            if doctor.specialization:
                specialty_enum = specialty_map.get(
                    doctor.specialization.lower(), 
                    'general_practitioner'
                )
            
            # No RPPS number - doctor will add it via settings
            
            # Créer le profil
            doctor_profile = DoctorProfile(
                user_id=doctor.id,
                specialty=specialty_enum,
                rpps_number=None,  # Optional - doctor can add it later
                biography=doctor.bio or "",
                languages=doctor.languages_spoken.split(',') if doctor.languages_spoken else ["Français"],
                education=[],
                experience_years=doctor.experience_years or 0,
                consultation_types='both',  # Use string value
                consultation_duration=30,
                consultation_price=float(doctor.consultation_fee / 100) if doctor.consultation_fee else 50.0,
                accepts_new_patients=doctor.accepting_new_patients if doctor.accepting_new_patients is not None else True,
                is_public=False,
                is_verified=doctor.is_verified
            )
            db.add(doctor_profile)
            db.flush()  # Get the ID
            
            # Créer les paramètres par défaut
            settings = DoctorSettings(doctor_id=doctor_profile.id)
            db.add(settings)
            
            print(f"✓ Profil créé pour {doctor.email} (RPPS: à compléter)")
            created_count += 1
        
        db.commit()
        
        print(f"\n=== Résumé ===")
        print(f"Profils créés: {created_count}")
        print(f"Profils existants: {skipped_count}")
        print(f"Total docteurs: {len(doctors)}")
        
    except Exception as e:
        db.rollback()
        print(f"Erreur: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Création des profils DoctorProfile manquants...")
    create_missing_profiles()
    print("Terminé!")
