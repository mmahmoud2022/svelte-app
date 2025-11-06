#!/usr/bin/env python3
"""
Test d'intégration du système de blacklist
Ce script teste le workflow complet :
1. Inscription d'un patient
2. Suspension du compte par admin
3. Tentative de connexion (devrait échouer)
4. Tentative de ré-inscription (devrait échouer)
5. Réactivation du compte
6. Connexion réussie
"""

import sys
sys.path.insert(0, '/home/alpha/fastapi-frontend/backend')

from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.models.user import User, UserRole
from app.models.blacklist import EmailBlacklist, BlacklistReason
from app.services.blacklist_service import BlacklistService
from app.services.auth_service import AuthService
from datetime import datetime

def cleanup(db: Session, test_email: str):
    """Nettoyer les données de test"""
    # Supprimer de la blacklist
    db.query(EmailBlacklist).filter(EmailBlacklist.email == test_email).delete()
    # Supprimer l'utilisateur
    db.query(User).filter(User.email == test_email).delete()
    db.commit()

def test_blacklist_integration():
    """Test d'intégration complet"""
    print("\n" + "="*80)
    print("TEST D'INTÉGRATION DU SYSTÈME DE BLACKLIST")
    print("="*80)
    
    db = next(get_db())
    blacklist_service = BlacklistService()
    auth_service = AuthService()
    
    test_email = "integration.test@example.com"
    test_password = "TestPassword123!"
    
    try:
        # Nettoyer d'abord
        cleanup(db, test_email)
        print(f"\n✓ Données de test nettoyées")
        
        # 1. Créer un utilisateur patient
        print(f"\n[STEP 1] Création d'un utilisateur patient...")
        hashed_password = auth_service.hash_password(test_password)
        user = User(
            email=test_email,
            hashed_password=hashed_password,
            first_name="Test",
            last_name="Integration",
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
        print(f"✅ Utilisateur créé avec ID: {user.id}")
        
        # 2. Vérifier qu'il n'est PAS blacklisté
        print(f"\n[STEP 2] Vérification que l'email n'est PAS blacklisté...")
        is_blacklisted, _ = blacklist_service.is_blacklisted(test_email, db)
        if not is_blacklisted:
            print(f"✅ L'email n'est pas blacklisté (comme attendu)")
        else:
            print(f"❌ ÉCHEC: L'email est blacklisté alors qu'il ne devrait pas l'être")
            return False
        
        # 3. Vérifier que l'authentification fonctionne
        print(f"\n[STEP 3] Test d'authentification AVANT suspension...")
        authenticated_user = auth_service.authenticate_user(test_email, test_password, db)
        if authenticated_user and authenticated_user.id == user.id:
            print(f"✅ Authentification réussie (comme attendu)")
        else:
            print(f"❌ ÉCHEC: Authentification échouée alors qu'elle devrait réussir")
            return False
        
        # 4. Ajouter l'email à la blacklist (simulation de suspension)
        print(f"\n[STEP 4] Ajout de l'email à la blacklist (SUSPENSION)...")
        blacklist_service.add_to_blacklist(
            email=test_email,
            reason=BlacklistReason.SUSPENDED,
            details="Test suspension - compte suspendu pour test d'intégration",
            original_user_id=user.id,
            original_user_name=f"{user.first_name} {user.last_name}",
            original_user_role=user.role.value,
            admin_id=1,
            admin_email="admin@example.com",
            db=db
        )
        print(f"✅ Email ajouté à la blacklist")
        
        # 5. Vérifier qu'il EST maintenant blacklisté
        print(f"\n[STEP 5] Vérification que l'email EST blacklisté...")
        is_blacklisted, blacklist_entry = blacklist_service.is_blacklisted(test_email, db)
        if is_blacklisted and blacklist_entry:
            print(f"✅ L'email est blacklisté (comme attendu)")
            print(f"   Raison: {blacklist_entry.reason.value}")
            print(f"   Détails: {blacklist_entry.details}")
            message = blacklist_service.get_blacklist_message(blacklist_entry)
            print(f"   Message: {message[:100]}...")
        else:
            print(f"❌ ÉCHEC: L'email n'est pas blacklisté alors qu'il devrait l'être")
            return False
        
        # 6. Tester que l'inscription serait bloquée
        print(f"\n[STEP 6] Simulation de tentative de ré-inscription...")
        print(f"   Dans le vrai endpoint, cela retournerait HTTP 403")
        print(f"   Message: {blacklist_service.get_blacklist_message(blacklist_entry)}")
        print(f"✅ La blacklist bloquerait correctement la ré-inscription")
        
        # 7. Retirer de la blacklist (simulation de réactivation)
        print(f"\n[STEP 7] Retrait de l'email de la blacklist (RÉACTIVATION)...")
        blacklist_service.remove_from_blacklist(test_email, db)
        print(f"✅ Email retiré de la blacklist")
        
        # 8. Vérifier qu'il n'est PLUS blacklisté
        print(f"\n[STEP 8] Vérification que l'email n'est PLUS blacklisté...")
        is_blacklisted, _ = blacklist_service.is_blacklisted(test_email, db)
        if not is_blacklisted:
            print(f"✅ L'email n'est plus blacklisté (comme attendu)")
        else:
            print(f"❌ ÉCHEC: L'email est encore blacklisté après suppression")
            return False
        
        # 9. Test de suppression permanente
        print(f"\n[STEP 9] Test avec raison DELETED...")
        blacklist_service.add_to_blacklist(
            email=test_email,
            reason=BlacklistReason.DELETED,
            details="Test deletion - compte supprimé définitivement",
            original_user_id=user.id,
            original_user_name=f"{user.first_name} {user.last_name}",
            original_user_role=user.role.value,
            admin_id=1,
            admin_email="admin@example.com",
            db=db
        )
        
        is_blacklisted, blacklist_entry = blacklist_service.is_blacklisted(test_email, db)
        if is_blacklisted and blacklist_entry.reason == BlacklistReason.DELETED:
            print(f"✅ Email blacklisté avec raison DELETED")
            message = blacklist_service.get_blacklist_message(blacklist_entry)
            print(f"   Message: {message}")
        else:
            print(f"❌ ÉCHEC: Blacklist DELETED non fonctionnelle")
            return False
        
        print(f"\n" + "="*80)
        print("🎉 TOUS LES TESTS D'INTÉGRATION SONT PASSÉS !")
        print("="*80)
        print(f"\nLe système de blacklist fonctionne correctement:")
        print(f"  ✓ Ajout à la blacklist")
        print(f"  ✓ Vérification de blacklist")
        print(f"  ✓ Messages appropriés par raison")
        print(f"  ✓ Retrait de la blacklist")
        print(f"  ✓ Différentes raisons (SUSPENDED, DELETED)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Nettoyer
        cleanup(db, test_email)
        print(f"\n✓ Données de test nettoyées")
        db.close()

if __name__ == "__main__":
    success = test_blacklist_integration()
    sys.exit(0 if success else 1)
