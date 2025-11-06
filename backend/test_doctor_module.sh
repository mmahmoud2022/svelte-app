#!/bin/bash

# Script de test pour le module Doctor
# Usage: ./test_doctor_module.sh

# Configuration
BASE_URL="http://localhost:8000/api/v1"
CONTENT_TYPE="Content-Type: application/json"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables globales
DOCTOR_TOKEN=""
DOCTOR_USER_ID=""
DOCTOR_PROFILE_ID=""
PATIENT_TOKEN=""
PATIENT_USER_ID=""
AVAILABILITY_ID=""
APPOINTMENT_ID=""
REVIEW_ID=""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Test du Module Doctor - Backend API  ${NC}"
echo -e "${YELLOW}========================================${NC}\n"

# Fonction pour afficher les résultats
check_response() {
    local response=$1
    local expected=$2
    local test_name=$3
    
    if [[ $response == *"$expected"* ]]; then
        echo -e "${GREEN}✓ $test_name${NC}"
        return 0
    else
        echo -e "${RED}✗ $test_name${NC}"
        echo "Response: $response"
        return 1
    fi
}

# 1. Créer un compte médecin
echo -e "${YELLOW}1. Création d'un compte médecin...${NC}"
DOCTOR_REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
    -H "$CONTENT_TYPE" \
    -d '{
        "email": "test.doctor@example.com",
        "password": "SecurePass123!",
        "first_name": "Jean",
        "last_name": "Dupont",
        "role": "doctor",
        "phone": "+33123456789"
    }')

check_response "$DOCTOR_REGISTER_RESPONSE" "email" "Inscription médecin"
DOCTOR_USER_ID=$(echo $DOCTOR_REGISTER_RESPONSE | jq -r '.id')
echo "Doctor User ID: $DOCTOR_USER_ID"

# 2. Se connecter en tant que médecin
echo -e "\n${YELLOW}2. Connexion du médecin...${NC}"
DOCTOR_LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "$CONTENT_TYPE" \
    -d '{
        "email": "test.doctor@example.com",
        "password": "SecurePass123!"
    }')

check_response "$DOCTOR_LOGIN_RESPONSE" "access_token" "Connexion médecin"
DOCTOR_TOKEN=$(echo $DOCTOR_LOGIN_RESPONSE | jq -r '.access_token')
echo "Doctor Token obtenu"

# 3. Créer un profil médecin
echo -e "\n${YELLOW}3. Création du profil médecin...${NC}"
PROFILE_CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/doctors/" \
    -H "$CONTENT_TYPE" \
    -H "Authorization: Bearer $DOCTOR_TOKEN" \
    -d '{
        "specialty": "cardiologist",
        "sub_specialty": "Cardiologie interventionnelle",
        "rpps_number": "12345678901",
        "office_address": "123 Rue de la Santé",
        "office_city": "Paris",
        "office_postal_code": "75014",
        "office_phone": "+33123456789",
        "biography": "Cardiologue avec 15 ans d'\''expérience",
        "languages": ["français", "anglais"],
        "education": [
            {
                "degree": "Doctorat en Médecine",
                "institution": "Université Paris Descartes",
                "year": 2008
            }
        ],
        "experience_years": 15,
        "consultation_types": "both",
        "consultation_duration": 30,
        "consultation_price": 50.0,
        "accepts_new_patients": true,
        "is_public": true
    }')

check_response "$PROFILE_CREATE_RESPONSE" "rpps_number" "Création profil"
DOCTOR_PROFILE_ID=$(echo $PROFILE_CREATE_RESPONSE | jq -r '.id')
echo "Doctor Profile ID: $DOCTOR_PROFILE_ID"

# 4. Obtenir son profil
echo -e "\n${YELLOW}4. Récupération du profil médecin...${NC}"
PROFILE_GET_RESPONSE=$(curl -s -X GET "$BASE_URL/doctors/me" \
    -H "Authorization: Bearer $DOCTOR_TOKEN")

check_response "$PROFILE_GET_RESPONSE" "cardiologist" "Récupération profil"

# 5. Mettre à jour le profil
echo -e "\n${YELLOW}5. Mise à jour du profil...${NC}"
PROFILE_UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/doctors/me" \
    -H "$CONTENT_TYPE" \
    -H "Authorization: Bearer $DOCTOR_TOKEN" \
    -d '{
        "biography": "Cardiologue spécialisé en cardiologie interventionnelle avec 15 ans d'\''expérience",
        "consultation_price": 55.0
    }')

check_response "$PROFILE_UPDATE_RESPONSE" "55" "Mise à jour profil"

# 6. Créer des créneaux de disponibilité
echo -e "\n${YELLOW}6. Création de créneaux de disponibilité...${NC}"
AVAILABILITY_RESPONSE=$(curl -s -X POST "$BASE_URL/doctors/availability" \
    -H "$CONTENT_TYPE" \
    -H "Authorization: Bearer $DOCTOR_TOKEN" \
    -d '{
        "date": "2025-11-15",
        "start_time": "09:00:00",
        "end_time": "09:30:00",
        "consultation_type": "in_person",
        "location": "Cabinet Paris 14ème"
    }')

check_response "$AVAILABILITY_RESPONSE" "date" "Création créneau"
AVAILABILITY_ID=$(echo $AVAILABILITY_RESPONSE | jq -r '.id')
echo "Availability ID: $AVAILABILITY_ID"

# Créer d'autres créneaux
for hour in 10 11 14 15; do
    curl -s -X POST "$BASE_URL/doctors/availability" \
        -H "$CONTENT_TYPE" \
        -H "Authorization: Bearer $DOCTOR_TOKEN" \
        -d "{
            \"date\": \"2025-11-15\",
            \"start_time\": \"${hour}:00:00\",
            \"end_time\": \"${hour}:30:00\",
            \"consultation_type\": \"both\",
            \"location\": \"Cabinet Paris 14ème\"
        }" > /dev/null
done
echo -e "${GREEN}✓ Plusieurs créneaux créés${NC}"

# 7. Voir les créneaux disponibles
echo -e "\n${YELLOW}7. Consultation des créneaux...${NC}"
AVAILABILITY_LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/doctors/$DOCTOR_PROFILE_ID/availability?start_date=2025-11-15&end_date=2025-11-15" \
    -H "Authorization: Bearer $DOCTOR_TOKEN")

check_response "$AVAILABILITY_LIST_RESPONSE" "09:00:00" "Liste créneaux"

# 8. Créer un compte patient
echo -e "\n${YELLOW}8. Création d'un compte patient...${NC}"
PATIENT_REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
    -H "$CONTENT_TYPE" \
    -d '{
        "email": "test.patient@example.com",
        "password": "SecurePass123!",
        "first_name": "Marie",
        "last_name": "Martin",
        "role": "patient",
        "phone": "+33612345678"
    }')

check_response "$PATIENT_REGISTER_RESPONSE" "email" "Inscription patient"
PATIENT_USER_ID=$(echo $PATIENT_REGISTER_RESPONSE | jq -r '.id')
echo "Patient User ID: $PATIENT_USER_ID"

# 9. Voir le profil public du médecin (en tant que patient)
echo -e "\n${YELLOW}9. Consultation du profil public...${NC}"
PATIENT_LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "$CONTENT_TYPE" \
    -d '{
        "email": "test.patient@example.com",
        "password": "SecurePass123!"
    }')
PATIENT_TOKEN=$(echo $PATIENT_LOGIN_RESPONSE | jq -r '.access_token')

PUBLIC_PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/doctors/$DOCTOR_PROFILE_ID" \
    -H "Authorization: Bearer $PATIENT_TOKEN")

check_response "$PUBLIC_PROFILE_RESPONSE" "cardiologist" "Profil public"

# 10. Mettre à jour les paramètres du médecin
echo -e "\n${YELLOW}10. Configuration des paramètres...${NC}"
SETTINGS_RESPONSE=$(curl -s -X PUT "$BASE_URL/doctors/settings" \
    -H "$CONTENT_TYPE" \
    -H "Authorization: Bearer $DOCTOR_TOKEN" \
    -d '{
        "email_notifications": true,
        "sms_notifications": false,
        "appointment_reminders": true,
        "profile_visibility": "public",
        "language": "fr",
        "timezone": "Europe/Paris"
    }')

check_response "$SETTINGS_RESPONSE" "email_notifications" "Paramètres"

# 11. Obtenir les statistiques
echo -e "\n${YELLOW}11. Consultation des statistiques...${NC}"
STATS_RESPONSE=$(curl -s -X GET "$BASE_URL/doctors/statistics" \
    -H "Authorization: Bearer $DOCTOR_TOKEN")

check_response "$STATS_RESPONSE" "total_consultations" "Statistiques"

# 12. Supprimer un créneau
echo -e "\n${YELLOW}12. Suppression d'un créneau...${NC}"
DELETE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/doctors/availability/$AVAILABILITY_ID" \
    -H "Authorization: Bearer $DOCTOR_TOKEN" \
    -w "%{http_code}")

if [[ $DELETE_RESPONSE == *"204"* ]]; then
    echo -e "${GREEN}✓ Suppression créneau${NC}"
else
    echo -e "${RED}✗ Suppression créneau${NC}"
fi

# Résumé
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}         Résumé des tests               ${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "Doctor User ID: $DOCTOR_USER_ID"
echo -e "Doctor Profile ID: $DOCTOR_PROFILE_ID"
echo -e "Patient User ID: $PATIENT_USER_ID"
echo -e "\n${GREEN}Tests terminés !${NC}"
echo -e "\nPour voir la documentation complète des endpoints:"
echo -e "  ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "\nPour tester manuellement les autres endpoints:"
echo -e "  - Liste des rendez-vous: GET /api/v1/doctors/appointments"
echo -e "  - Liste des patients: GET /api/v1/doctors/patients"
echo -e "  - Messagerie: GET /api/v1/doctors/messages"
echo -e "  - Avis: GET /api/v1/doctors/reviews"
echo -e "  - Paiements: GET /api/v1/doctors/payments"
