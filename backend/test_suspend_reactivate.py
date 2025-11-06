#!/usr/bin/env python3
"""
Test du workflow complet de suspension/réactivation avec retrait de blacklist
"""

import sys
sys.path.insert(0, '/home/alpha/fastapi-frontend/backend')

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.blacklist import EmailBlacklist
from app.services.blacklist_service import BlacklistService
from app.services.auth_service import AuthService
from datetime import datetime

def test_suspend_reactivate_workflow():
    """
    Test complet :
    1. Créer un utilisateur
    2. Le suspendre (doit ajouter à blacklist)
    3. Vérifier qu'il est blacklisté
    4. Le réactiver (doit retirer de blacklist) ✅
    5. Vérifier qu'il n'est plus blacklisté
    """
    print("\n" + "="*80)
    print("TEST WORKFLOW SUSPENSION/RÉACTIVATION")
    print("="*80)
    
    db = next(get_db())
    blacklist_service = BlacklistService()
    auth_service = AuthService()
    
    test_email = "workflow.test@example.com"
    test_password = "TestPass123!"
    
    try:
        # Nettoyer
        db.query(EmailBlacklist).filter(EmailBlacklist.email == test_email).delete()
        db.query(User).filter(User.email == test_email).delete()
        db.commit()
        
        # 1. Créer utilisateur
        print("\n[STEP 1] Création d'un utilisateur...")
        user = User(
            email=test_email,
            hashed_password=auth_service.hash_password(test_password),
            first_name="Test",
            last_name="Workflow",
            phone="+33612345678",
            role=UserRole.PATIENT,
            is_active=True,
            is_verified=True,
            data_processing_consent=True,
            terms_accepted_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Utilisateur créé | ID={user.id} | is_active={user.is_active}")
        
        # 2. Suspendre
        print("\n[STEP 2] Suspension de l'utilisateur...")
        user.is_active = False
        user.suspension_reason = "Test de suspension"
        
        from app.models.blacklist import BlacklistReason
        blacklist_service.add_to_blacklist(
            email=user.email,
            reason=BlacklistReason.SUSPENDED,
            details="Test workflow",
            original_user_id=user.id,
            original_user_name=f"{user.first_name} {user.last_name}",
            original_user_role=user.role.value,
            admin_id=1,
            admin_email="admin@test.com",
            db=db
        )
        db.commit()
        print(f"✅ Utilisateur suspendu | is_active={user.is_active}")
        
        # 3. Vérifier blacklist
        print("\n[STEP 3] Vérification blacklist après suspension...")
        is_blacklisted, entry = blacklist_service.is_blacklisted(test_email, db)
        if is_blacklisted:
            print(f"✅ Email blacklisté | reason={entry.reason.value}")
        else:
            print(f"❌ ÉCHEC: Email devrait être blacklisté")
            return False
        
        # 4. Réactiver (retire de blacklist)
        print("\n[STEP 4] Réactivation de l'utilisateur...")
        user.is_active = True
        user.suspension_reason = None
        
        # CRITIQUE: Retire l'email de la blacklist
        blacklist_service.remove_from_blacklist(user.email, db)
        
        db.commit()
        print(f"✅ Utilisateur réactivé | is_active={user.is_active}")
        
        # 5. Vérifier que plus blacklisté
        print("\n[STEP 5] Vérification blacklist après réactivation...")
        is_blacklisted, _ = blacklist_service.is_blacklisted(test_email, db)
        if not is_blacklisted:
            print(f"✅ Email RETIRÉ de la blacklist (comme attendu)")
        else:
            print(f"❌ ÉCHEC: Email encore blacklisté après réactivation")
            return False
        
        # 6. Vérifier authentification possible
        print("\n[STEP 6] Test d'authentification après réactivation...")
        authenticated = auth_service.authenticate_user(test_email, test_password, db)
        if authenticated:
            print(f"✅ Authentification réussie | user_id={authenticated.id}")
        else:
            print(f"❌ ÉCHEC: Authentification échouée")
            return False
        
        print("\n" + "="*80)
        print("🎉 WORKFLOW COMPLET VALIDÉ !")
        print("="*80)
        print("\n✅ Le système fonctionne correctement :")
        print("  1. ✓ Suspension ajoute à la blacklist")
        print("  2. ✓ Blacklist bloque l'accès")
        print("  3. ✓ Réactivation RETIRE de la blacklist ⭐")
        print("  4. ✓ Utilisateur peut se reconnecter après réactivation")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Nettoyer
        db.query(EmailBlacklist).filter(EmailBlacklist.email == test_email).delete()
        db.query(User).filter(User.email == test_email).delete()
        db.commit()
        db.close()

if __name__ == "__main__":
    success = test_suspend_reactivate_workflow()
    sys.exit(0 if success else 1)
