#!/usr/bin/env python3
"""
Script de test pour l'authentification avec logs détaillés
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/auth"

def test_register_patient():
    """Test d'enregistrement d'un patient"""
    print("\n=== Test d'enregistrement d'un patient ===")
    
    data = {
        "email": "patient.test@example.com",
        "password": "SecurePass123!",
        "first_name": "Jean",
        "last_name": "Dupont",
        "phone": "+33612345678",
        "date_of_birth": "1990-05-15",
        "gender": "male",
        "emergency_contact_name": "Marie Dupont",
        "emergency_contact_phone": "+33698765432",
        "marketing_consent": True
    }
    
    response = requests.post(f"{BASE_URL}/register/patient", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_login(email, password):
    """Test de connexion"""
    print(f"\n=== Test de connexion pour {email} ===")
    
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_get_me(access_token):
    """Test de récupération du profil utilisateur"""
    print("\n=== Test de récupération du profil ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_register_practitioner():
    """Test d'enregistrement d'un praticien"""
    print("\n=== Test d'enregistrement d'un praticien ===")
    
    data = {
        "email": "doctor.test@example.com",
        "password": "SecurePass123!",
        "first_name": "Marie",
        "last_name": "Martin",
        "phone": "+33623456789",
        "date_of_birth": "1985-08-20",
        "gender": "female",
        "specialization": "Médecine Générale",
        "license_number": "RPPS12345678",
        "consultation_duration": 30,
        "consultation_price": 25.0
    }
    
    response = requests.post(f"{BASE_URL}/register/practitioner", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

if __name__ == "__main__":
    try:
        # Test 1: Enregistrement d'un patient
        patient_result = test_register_patient()
        patient_email = patient_result.get("user", {}).get("email")
        
        # Test 2: Connexion du patient (devrait échouer car email non vérifié)
        print("\n⚠️  La connexion devrait échouer car l'email n'est pas vérifié")
        try:
            login_result = test_login(patient_email, "SecurePass123!")
        except Exception as e:
            print(f"Erreur attendue: {e}")
        
        # Test 3: Enregistrement d'un praticien
        practitioner_result = test_register_practitioner()
        
        print("\n" + "="*60)
        print("✅ Tests terminés avec succès!")
        print("="*60)
        print("\n📧 Vérifiez vos emails dans Mailpit: http://localhost:8025")
        print("   - Email de vérification pour le patient")
        print("   - Email de vérification pour le praticien")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur FastAPI est démarré sur le port 8000")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
