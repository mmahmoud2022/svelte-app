"""
Script de test pour le service email
Exécutez avec: python test_email_manual.py
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.services.email_service import get_email_service
from app.core.config import settings


async def test_simple_email():
    """Test d'envoi d'email simple"""
    print("=" * 60)
    print("TEST 1: Envoi d'email simple")
    print("=" * 60)
    
    email_service = get_email_service()
    
    result = await email_service.send_email(
        to_email="test@example.com",
        subject="Test Email - Santé App",
        html_content="<h1>Email de test</h1><p>Ceci est un test du service email.</p>",
        plain_content="Email de test\n\nCeci est un test du service email."
    )
    
    if result["success"]:
        print("✅ Email envoyé avec succès!")
        print(f"   Provider: {result.get('provider', 'unknown')}")
        print(f"   Message ID: {result['message_id']}")
        print(f"   Note: {result.get('note', '')}")
    else:
        print("❌ Erreur lors de l'envoi:")
        print(f"   {result['error']}")
    
    return result


async def test_appointment_confirmation():
    """Test d'envoi de confirmation de rendez-vous"""
    print("\n" + "=" * 60)
    print("TEST 2: Confirmation de rendez-vous")
    print("=" * 60)
    
    email_service = get_email_service()
    
    result = await email_service.send_appointment_confirmation(
        to_email="patient@example.com",
        patient_name="Jean Dupont",
        doctor_name="Dr. Marie Martin",
        appointment_date="15 novembre 2025",
        appointment_time="14:30",
        appointment_type="Consultation générale",
        cancellation_url="https://sante-app.com/cancel/abc123"
    )
    
    if result["success"]:
        print("✅ Confirmation de rendez-vous envoyée!")
        print(f"   Message ID: {result['message_id']}")
    else:
        print("❌ Erreur lors de l'envoi:")
        print(f"   {result['error']}")
    
    return result


async def test_password_reset():
    """Test d'envoi de réinitialisation de mot de passe"""
    print("\n" + "=" * 60)
    print("TEST 3: Réinitialisation de mot de passe")
    print("=" * 60)
    
    email_service = get_email_service()
    
    result = await email_service.send_password_reset(
        to_email="user@example.com",
        first_name="Sophie",
        reset_url="https://sante-app.com/reset-password/token123",
        expiry_minutes=15
    )
    
    if result["success"]:
        print("✅ Email de réinitialisation envoyé!")
        print(f"   Message ID: {result['message_id']}")
    else:
        print("❌ Erreur lors de l'envoi:")
        print(f"   {result['error']}")
    
    return result


async def test_appointment_reminder():
    """Test d'envoi de rappel de rendez-vous"""
    print("\n" + "=" * 60)
    print("TEST 4: Rappel de rendez-vous")
    print("=" * 60)
    
    email_service = get_email_service()
    
    result = await email_service.send_appointment_reminder(
        to_email="patient@example.com",
        patient_name="Pierre Durand",
        doctor_name="Dr. Jean Lefebvre",
        appointment_date="16 novembre 2025",
        appointment_time="10:00"
    )
    
    if result["success"]:
        print("✅ Rappel de rendez-vous envoyé!")
        print(f"   Message ID: {result['message_id']}")
    else:
        print("❌ Erreur lors de l'envoi:")
        print(f"   {result['error']}")
    
    return result


async def main():
    """Fonction principale"""
    print("\n" + "🔧 " * 20)
    print("TEST DU SERVICE EMAIL - SANTÉ APP")
    print("🔧 " * 20)
    
    print(f"\nConfiguration actuelle:")
    print(f"  - Provider: {settings.EMAIL_PROVIDER}")
    print(f"  - SMTP Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    print(f"  - Email From: {settings.EMAIL_FROM}")
    print(f"  - Email Enabled: {settings.EMAIL_ENABLED}")
    
    if settings.EMAIL_PROVIDER == "smtp":
        print(f"\n💡 Interface Mailpit: http://localhost:8025")
        print(f"   Tous les emails envoyés seront visibles ici!\n")
    
    try:
        # Exécuter les tests
        await test_simple_email()
        await test_appointment_confirmation()
        await test_password_reset()
        await test_appointment_reminder()
        
        print("\n" + "✅ " * 20)
        print("TOUS LES TESTS SONT TERMINÉS!")
        print("✅ " * 20)
        
        if settings.EMAIL_PROVIDER == "smtp":
            print("\n👉 Consultez les emails à: http://localhost:8025")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
