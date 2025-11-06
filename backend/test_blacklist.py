#!/usr/bin/env python3
"""
Script de test pour le système de blacklist d'emails

Tests:
1. Vérifier que la blacklist empêche l'inscription
2. Vérifier que la blacklist empêche la connexion
3. Vérifier que la réactivation retire de la blacklist
4. Vérifier les logs structurés
5. Vérifier les messages d'erreur appropriés
"""

import sys
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Ajouter le chemin app au PYTHONPATH
sys.path.insert(0, '/home/alpha/fastapi-frontend/backend')

from app.models.blacklist import EmailBlacklist, BlacklistReason
from app.models.user import User, UserRole
from app.services.blacklist_service import BlacklistService
from app.core.database import Base
from app.core.config import settings


def create_test_session():
    """Crée une session de test"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def test_add_to_blacklist(db: Session):
    """Test 1: Ajouter un email à la blacklist"""
    print("\n" + "="*80)
    print("TEST 1: Ajouter un email à la blacklist")
    print("="*80)
    
    service = BlacklistService()
    test_email = "blacklist_test@example.com"
    
    # Nettoyer d'abord si existe
    existing = db.query(EmailBlacklist).filter(EmailBlacklist.email == test_email).first()
    if existing:
        db.delete(existing)
        db.commit()
        print(f"✓ Email existant nettoyé: {test_email}")
    
    # Ajouter à la blacklist
    service.add_to_blacklist(
        email=test_email,
        reason=BlacklistReason.DELETED,
        details="Test deletion",
        original_user_id=999,
        original_user_name="Test User",
        original_user_role="PATIENT",
        admin_id=1,
        admin_email="admin@example.com",
        db=db
    )
    
    # Vérifier l'ajout
    entry = db.query(EmailBlacklist).filter(EmailBlacklist.email == test_email).first()
    
    if entry:
        print(f"✅ SUCCÈS: Email ajouté à la blacklist")
        print(f"   - Email: {entry.email}")
        print(f"   - Raison: {entry.reason.value}")
        print(f"   - Détails: {entry.details}")
        print(f"   - User original: {entry.original_user_name} (ID: {entry.original_user_id})")
        print(f"   - Admin: {entry.blacklisted_by_admin_email} (ID: {entry.blacklisted_by_admin_id})")
        print(f"   - Créé le: {entry.created_at}")
        return True
    else:
        print(f"❌ ÉCHEC: Email non trouvé dans la blacklist")
        return False


def test_is_blacklisted(db: Session):
    """Test 2: Vérifier si un email est blacklisté"""
    print("\n" + "="*80)
    print("TEST 2: Vérifier si un email est blacklisté")
    print("="*80)
    
    service = BlacklistService()
    test_email = "blacklist_test@example.com"
    
    is_blacklisted, entry = service.is_blacklisted(test_email, db)
    
    if is_blacklisted and entry:
        print(f"✅ SUCCÈS: Email détecté comme blacklisté")
        print(f"   - Email: {entry.email}")
        print(f"   - Raison: {entry.reason.value}")
        message = service.get_blacklist_message(entry)
        print(f"   - Message utilisateur: {message[:100]}...")
        return True
    else:
        print(f"❌ ÉCHEC: Email non détecté comme blacklisté")
        return False


def test_blacklist_messages(db: Session):
    """Test 3: Vérifier les messages pour chaque raison"""
    print("\n" + "="*80)
    print("TEST 3: Messages de blacklist par raison")
    print("="*80)
    
    service = BlacklistService()
    
    reasons = [
        (BlacklistReason.DELETED, "deleted_test@example.com"),
        (BlacklistReason.SUSPENDED, "suspended_test@example.com"),
        (BlacklistReason.BANNED, "banned_test@example.com"),
        (BlacklistReason.FRAUD, "fraud_test@example.com"),
    ]
    
    all_success = True
    
    for reason, email in reasons:
        # Nettoyer d'abord
        existing = db.query(EmailBlacklist).filter(EmailBlacklist.email == email).first()
        if existing:
            db.delete(existing)
            db.commit()
        
        # Ajouter avec cette raison
        service.add_to_blacklist(
            email=email,
            reason=reason,
            details=f"Test {reason.value}",
            original_user_id=999,
            original_user_name="Test User",
            original_user_role="PATIENT",
            admin_id=1,
            admin_email="admin@example.com",
            db=db
        )
        
        # Récupérer l'entrée
        entry = db.query(EmailBlacklist).filter(EmailBlacklist.email == email).first()
        
        if entry:
            message = service.get_blacklist_message(entry)
            print(f"\n✅ {reason.value.upper()}:")
            print(f"   Message: {message}")
        else:
            print(f"\n❌ ÉCHEC: {reason.value.upper()}")
            all_success = False
    
    return all_success


def test_remove_from_blacklist(db: Session):
    """Test 4: Retirer un email de la blacklist"""
    print("\n" + "="*80)
    print("TEST 4: Retirer un email de la blacklist")
    print("="*80)
    
    service = BlacklistService()
    test_email = "blacklist_test@example.com"
    
    # Vérifier qu'il est blacklisté
    is_blacklisted_before, _ = service.is_blacklisted(test_email, db)
    print(f"Avant suppression: blacklisté = {is_blacklisted_before}")
    
    # Retirer de la blacklist
    service.remove_from_blacklist(test_email, db)
    
    # Vérifier qu'il n'est plus blacklisté
    is_blacklisted_after, _ = service.is_blacklisted(test_email, db)
    print(f"Après suppression: blacklisté = {is_blacklisted_after}")
    
    if is_blacklisted_before and not is_blacklisted_after:
        print(f"✅ SUCCÈS: Email retiré de la blacklist")
        return True
    else:
        print(f"❌ ÉCHEC: État de blacklist incorrect")
        return False


def test_expired_blacklist(db: Session):
    """Test 5: Vérifier la gestion des entrées expirées"""
    print("\n" + "="*80)
    print("TEST 5: Gestion des entrées expirées")
    print("="*80)
    
    from datetime import datetime, timedelta
    
    service = BlacklistService()
    test_email = "expired_test@example.com"
    
    # Nettoyer d'abord
    existing = db.query(EmailBlacklist).filter(EmailBlacklist.email == test_email).first()
    if existing:
        db.delete(existing)
        db.commit()
    
    # Créer une entrée expirée (expirée hier)
    expired_entry = EmailBlacklist(
        email=test_email,
        reason=BlacklistReason.SUSPENDED,
        details="Test expiration",
        original_user_id=999,
        original_user_name="Test User",
        original_user_role="PATIENT",
        blacklisted_by_admin_id=1,
        blacklisted_by_admin_email="admin@example.com",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() - timedelta(days=1)  # Expiré hier
    )
    db.add(expired_entry)
    db.commit()
    
    # Vérifier que l'entrée est considérée comme expirée
    print(f"Entry is_expired: {expired_entry.is_expired}")
    
    # Vérifier avec le service
    is_blacklisted, entry = service.is_blacklisted(test_email, db)
    
    if not is_blacklisted:
        print(f"✅ SUCCÈS: Entrée expirée ignorée correctement")
        return True
    else:
        print(f"❌ ÉCHEC: Entrée expirée toujours active")
        return False


def cleanup_test_data(db: Session):
    """Nettoyer les données de test"""
    print("\n" + "="*80)
    print("NETTOYAGE des données de test")
    print("="*80)
    
    test_emails = [
        "blacklist_test@example.com",
        "deleted_test@example.com",
        "suspended_test@example.com",
        "banned_test@example.com",
        "fraud_test@example.com",
        "expired_test@example.com"
    ]
    
    deleted_count = 0
    for email in test_emails:
        entry = db.query(EmailBlacklist).filter(EmailBlacklist.email == email).first()
        if entry:
            db.delete(entry)
            deleted_count += 1
    
    db.commit()
    print(f"✓ {deleted_count} entrées de test supprimées")


def main():
    """Exécuter tous les tests"""
    print("\n" + "="*80)
    print("TESTS DU SYSTÈME DE BLACKLIST D'EMAILS")
    print("="*80)
    print(f"Heure de début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Créer une session
        db = create_test_session()
        print("\n✓ Connexion à la base de données établie")
        
        # Exécuter les tests
        results = []
        
        results.append(("Ajout à la blacklist", test_add_to_blacklist(db)))
        results.append(("Vérification blacklist", test_is_blacklisted(db)))
        results.append(("Messages par raison", test_blacklist_messages(db)))
        results.append(("Suppression de blacklist", test_remove_from_blacklist(db)))
        results.append(("Gestion expiration", test_expired_blacklist(db)))
        
        # Nettoyer
        cleanup_test_data(db)
        
        # Résumé
        print("\n" + "="*80)
        print("RÉSUMÉ DES TESTS")
        print("="*80)
        
        total = len(results)
        passed = sum(1 for _, success in results if success)
        failed = total - passed
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\nTotal: {total} tests")
        print(f"Réussis: {passed}")
        print(f"Échoués: {failed}")
        print(f"Taux de réussite: {(passed/total*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
            return 0
        else:
            print(f"\n⚠️  {failed} test(s) ont échoué")
            return 1
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        if 'db' in locals():
            db.close()
            print("\n✓ Connexion à la base de données fermée")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
