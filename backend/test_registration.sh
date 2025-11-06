#!/bin/bash

echo "========================================"
echo "Test d'enregistrement d'un patient"
echo "========================================"
echo ""

# Attendre que le serveur soit prêt
sleep 2

# Enregistrer un nouveau patient
echo "1. Enregistrement du patient..."
curl -X POST "http://localhost:8000/api/v1/auth/register/patient" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.patient@example.com",
    "password": "SecurePass123!",
    "first_name": "Jean",
    "last_name": "Dupont",
    "phone": "+33612345678",
    "date_of_birth": "1990-05-15",
    "gender": "male",
    "emergency_contact_name": "Marie Dupont",
    "emergency_contact_phone": "+33698765432",
    "marketing_consent": true
  }' \
  | python3 -m json.tool

echo ""
echo ""
echo "========================================"
echo "✅ Vérifiez les logs du serveur pour voir les détails"
echo "📧 Vérifiez Mailpit: http://localhost:8025"
echo "========================================"
