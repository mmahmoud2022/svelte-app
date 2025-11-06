#!/usr/bin/env python3
"""
Test simple de l'enregistrement patient avec tous les logs
"""
import requests
import json

def test_patient_registration():
    url = "http://localhost:8000/api/v1/auth/register/patient"
    
    data = {
        "email": "marie.test@example.com",
        "password": "SecurePass123!",
        "first_name": "Marie",
        "last_name": "Martin",
        "phone": "+33612345679",
        "date_of_birth": "1985-03-20",
        "gender": "female",
        "emergency_contact_name": "Pierre Martin",
        "emergency_contact_phone": "+33687654321",
        "emergency_contact_relationship": "Époux",
        "marketing_consent": True
    }
    
    print("=" * 60)
    print("Test d'enregistrement d'un patient")
    print("=" * 60)
    print(f"\nEnvoi de la requête à: {url}")
    print(f"Données: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("\n" + "=" * 60)
    
    try:
        response = requests.post(url, json=data)
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"\nRéponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 201:
            print("\n" + "=" * 60)
            print("✅ SUCCÈS! Patient enregistré")
            print("📧 Vérifiez Mailpit: http://localhost:8025")
            print("=" * 60)
        else:
            print("\n❌ Échec de l'enregistrement")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur FastAPI est démarré")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    test_patient_registration()
