# Module Doctor - Documentation Backend

## Vue d'ensemble

Ce module permet la gestion complète des profils de médecins, de leurs disponibilités, rendez-vous, messages, avis et paiements.

## Architecture

### Modèles de données (models/doctor.py)

#### Tables créées :
1. **doctor_profiles** - Profils professionnels des médecins
2. **doctor_availabilities** - Créneaux de disponibilité
3. **appointments** - Rendez-vous médicaux
4. **doctor_reviews** - Avis et notes des patients
5. **doctor_messages** - Messagerie sécurisée
6. **payments** - Paiements des consultations
7. **patient_documents** - Documents médicaux partagés
8. **doctor_settings** - Paramètres et préférences

#### Enums définis :
- **SpecialtyEnum** : Spécialités médicales (general_practitioner, cardiologist, etc.)
- **ConsultationTypeEnum** : Types de consultation (in_person, teleconsultation, both)
- **AppointmentStatusEnum** : Statuts de rendez-vous (pending, confirmed, completed, cancelled, no_show)
- **PaymentStatusEnum** : Statuts de paiement (pending, completed, failed, refunded)

## Routes API (20 endpoints)

### 1️⃣ Créer un profil praticien
```http
POST /api/v1/doctors/
Authorization: Bearer <token>
Content-Type: application/json

{
  "specialty": "cardiologist",
  "sub_specialty": "Cardiologie interventionnelle",
  "rpps_number": "12345678901",
  "office_address": "123 Rue de la Santé",
  "office_city": "Paris",
  "office_postal_code": "75014",
  "office_phone": "+33123456789",
  "biography": "Cardiologue avec 15 ans d'expérience...",
  "languages": ["français", "anglais", "espagnol"],
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
}
```

**Réponse 201 :**
```json
{
  "id": 1,
  "user_id": 42,
  "specialty": "cardiologist",
  "rpps_number": "12345678901",
  "office_city": "Paris",
  "biography": "Cardiologue avec 15 ans d'expérience...",
  "is_verified": false,
  "total_consultations": 0,
  "average_rating": 0.0,
  "total_reviews": 0,
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@example.com",
  "created_at": "2025-11-06T10:00:00Z"
}
```

### 2️⃣ Obtenir son propre profil
```http
GET /api/v1/doctors/me
Authorization: Bearer <token>
```

### 3️⃣ Mettre à jour son profil
```http
PUT /api/v1/doctors/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "biography": "Nouvelle biographie mise à jour...",
  "consultation_price": 55.0,
  "accepts_new_patients": false
}
```

### 4️⃣ Consulter un profil public de médecin
```http
GET /api/v1/doctors/{doctor_id}
Authorization: Bearer <token>
```

**Réponse 200 :**
```json
{
  "id": 1,
  "specialty": "cardiologist",
  "office_city": "Paris",
  "biography": "Cardiologue avec 15 ans d'expérience...",
  "languages": ["français", "anglais"],
  "experience_years": 15,
  "consultation_price": 50.0,
  "average_rating": 4.7,
  "total_reviews": 23,
  "first_name": "Jean",
  "last_name": "Dupont"
}
```

### 5️⃣ Voir les créneaux disponibles d'un médecin
```http
GET /api/v1/doctors/{doctor_id}/availability?start_date=2025-11-10&end_date=2025-11-15
Authorization: Bearer <token>
```

**Réponse 200 :**
```json
[
  {
    "id": 1,
    "doctor_id": 1,
    "date": "2025-11-10",
    "start_time": "09:00:00",
    "end_time": "09:30:00",
    "consultation_type": "both",
    "is_available": true,
    "is_booked": false
  }
]
```

### 6️⃣ Créer un créneau de disponibilité
```http
POST /api/v1/doctors/availability
Authorization: Bearer <token>
Content-Type: application/json

{
  "date": "2025-11-10",
  "start_time": "09:00:00",
  "end_time": "09:30:00",
  "consultation_type": "in_person",
  "location": "Cabinet Paris 14ème",
  "notes": "Consultation normale"
}
```

### 7️⃣ Supprimer un créneau
```http
DELETE /api/v1/doctors/availability/{availability_id}
Authorization: Bearer <token>
```

**Réponse 204 :** No Content

### 8️⃣ Liste des rendez-vous du médecin
```http
GET /api/v1/doctors/appointments?status_filter=pending&page=1&page_size=20
Authorization: Bearer <token>
```

**Réponse 200 :**
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "doctor_id": 1,
      "patient_id": 10,
      "status": "pending",
      "appointment_date": "2025-11-10T09:00:00Z",
      "consultation_type": "in_person",
      "reason": "Contrôle annuel",
      "patient_first_name": "Marie",
      "patient_last_name": "Martin",
      "patient_phone": "+33612345678"
    }
  ]
}
```

### 9️⃣ Détails d'un rendez-vous
```http
GET /api/v1/doctors/appointments/{appointment_id}
Authorization: Bearer <token>
```

### 🔟 Modifier le statut d'un rendez-vous
```http
PATCH /api/v1/doctors/appointments/{appointment_id}/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "completed",
  "doctor_notes": "Patient en bonne santé. Contrôle à refaire dans 1 an."
}
```

**Statuts possibles :** `pending`, `confirmed`, `completed`, `cancelled`, `no_show`

### 11️⃣ Liste des patients suivis
```http
GET /api/v1/doctors/patients?page=1&page_size=50
Authorization: Bearer <token>
```

**Réponse 200 :**
```json
{
  "total": 150,
  "page": 1,
  "page_size": 50,
  "items": [
    {
      "id": 10,
      "first_name": "Marie",
      "last_name": "Martin",
      "email": "marie.martin@example.com",
      "phone": "+33612345678",
      "date_of_birth": "1985-05-15T00:00:00Z",
      "total_appointments": 5,
      "last_appointment_date": "2025-10-20T14:00:00Z"
    }
  ]
}
```

### 12️⃣ Dossier médical d'un patient
```http
GET /api/v1/doctors/patients/{patient_id}
Authorization: Bearer <token>
```

**Réponse 200 :**
```json
{
  "patient": {
    "id": 10,
    "first_name": "Marie",
    "last_name": "Martin",
    "email": "marie.martin@example.com",
    "phone": "+33612345678",
    "date_of_birth": "1985-05-15T00:00:00Z",
    "gender": "female",
    "city": "Paris"
  },
  "appointments": [...],
  "documents": [...],
  "total_consultations": 5
}
```

### 13️⃣ Statistiques d'activité
```http
GET /api/v1/doctors/statistics
Authorization: Bearer <token>
```

**Réponse 200 :**
```json
{
  "total_consultations": 120,
  "completed_consultations": 110,
  "cancelled_consultations": 8,
  "no_show_consultations": 2,
  "cancellation_rate": 8.33,
  "average_rating": 4.7,
  "total_reviews": 45,
  "new_patients_count": 30,
  "returning_patients_count": 25,
  "total_revenue": 5500.0,
  "pending_revenue": 450.0,
  "upcoming_appointments": 15,
  "today_appointments": 3
}
```

### 14️⃣ Mettre à jour les paramètres
```http
PUT /api/v1/doctors/settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "email_notifications": true,
  "sms_notifications": false,
  "appointment_reminders": true,
  "profile_visibility": "public",
  "show_phone": true,
  "show_email": false,
  "language": "fr",
  "timezone": "Europe/Paris"
}
```

### 15️⃣ Envoyer un document patient
```http
POST /api/v1/doctors/documents
Authorization: Bearer <token>
Content-Type: multipart/form-data

patient_id: 10
title: "Ordonnance du 06/11/2025"
description: "Traitement pour l'hypertension"
document_type: "prescription"
file: [fichier PDF]
```

**Réponse 201 :**
```json
{
  "id": 1,
  "doctor_id": 1,
  "patient_id": 10,
  "title": "Ordonnance du 06/11/2025",
  "file_name": "ordonnance.pdf",
  "file_size": 245678,
  "mime_type": "application/pdf",
  "document_type": "prescription",
  "is_patient_visible": true,
  "created_at": "2025-11-06T10:30:00Z",
  "patient_first_name": "Marie",
  "patient_last_name": "Martin"
}
```

### 16️⃣ Boîte de messagerie
```http
GET /api/v1/doctors/messages?page=1&page_size=50
Authorization: Bearer <token>
```

**Réponse 200 :**
```json
{
  "total": 25,
  "page": 1,
  "page_size": 50,
  "items": [
    {
      "id": 1,
      "sender_id": 1,
      "recipient_id": 10,
      "subject": "Résultats de vos analyses",
      "content": "Bonjour, vos résultats sont disponibles...",
      "is_read": false,
      "created_at": "2025-11-06T09:00:00Z",
      "sender_first_name": "Jean",
      "sender_last_name": "Dupont",
      "recipient_first_name": "Marie",
      "recipient_last_name": "Martin"
    }
  ]
}
```

### 17️⃣ Envoyer un message
```http
POST /api/v1/doctors/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "recipient_id": 10,
  "subject": "Rappel rendez-vous",
  "content": "Bonjour, je vous rappelle votre rendez-vous de demain à 9h.",
  "appointment_id": 5
}
```

### 18️⃣ Historique des paiements
```http
GET /api/v1/doctors/payments?status_filter=completed&page=1&page_size=50
Authorization: Bearer <token>
```

**Réponse 200 :**
```json
{
  "total": 98,
  "page": 1,
  "page_size": 50,
  "items": [
    {
      "id": 1,
      "doctor_id": 1,
      "patient_id": 10,
      "amount": 50.0,
      "currency": "EUR",
      "status": "completed",
      "payment_method": "card",
      "transaction_id": "txn_123456789",
      "created_at": "2025-11-01T14:30:00Z",
      "paid_at": "2025-11-01T14:30:15Z",
      "patient_first_name": "Marie",
      "patient_last_name": "Martin"
    }
  ]
}
```

### 19️⃣ Avis patients
```http
GET /api/v1/doctors/reviews?page=1&page_size=20
Authorization: Bearer <token>
```

**Réponse 200 :**
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "doctor_id": 1,
      "patient_id": 10,
      "rating": 5,
      "comment": "Excellent médecin, très à l'écoute !",
      "doctor_response": "Merci pour votre confiance.",
      "responded_at": "2025-11-02T10:00:00Z",
      "is_public": true,
      "created_at": "2025-11-01T16:00:00Z",
      "patient_first_name": "Marie",
      "patient_last_name": "Martin"
    }
  ]
}
```

### 20️⃣ Répondre à un avis
```http
POST /api/v1/doctors/reviews/{review_id}/respond
Authorization: Bearer <token>
Content-Type: application/json

{
  "response": "Merci beaucoup pour votre retour positif. Au plaisir de vous revoir !"
}
```

## Installation et migration

### 1. Appliquer la migration

```bash
cd backend
alembic upgrade head
```

### 2. Vérifier les tables créées

```sql
-- Connexion à PostgreSQL
psql -U postgres -d healthcare_db

-- Lister les tables
\dt

-- Vérifier la structure d'une table
\d doctor_profiles
```

### 3. Créer un utilisateur avec le rôle DOCTOR

```bash
# Via l'API d'inscription avec admin_approved=True
POST /api/v1/auth/register
{
  "email": "doctor@example.com",
  "password": "SecurePass123!",
  "first_name": "Jean",
  "last_name": "Dupont",
  "role": "doctor"
}

# L'admin doit ensuite approuver le compte
PATCH /api/v1/admin/users/{user_id}/approve
```

## Sécurité et autorisations

### Contrôles d'accès :
- **Toutes les routes** nécessitent une authentification Bearer token
- **Routes /doctors/*** (sauf GET /{doctor_id}) nécessitent le rôle `DOCTOR`
- Un médecin ne peut accéder qu'à **ses propres données** (profil, rendez-vous, messages)
- Un médecin ne peut voir le dossier d'un patient que si ce patient l'a **déjà consulté**

### Validation des données :
- Numéro RPPS : exactement 11 chiffres, unique
- Notes : entre 1 et 5 étoiles
- Dates : créneaux futurs, pas de chevauchement
- Fichiers : validés par type MIME et taille

## Exemples de flux utilisateur

### Flux 1 : Création d'un profil médecin complet

```bash
# 1. S'inscrire en tant que doctor
POST /api/v1/auth/register
{
  "email": "dr.martin@hospital.com",
  "password": "SecurePass123!",
  "first_name": "Sophie",
  "last_name": "Martin",
  "role": "doctor"
}

# 2. Attendre l'approbation admin (admin_approved=true)

# 3. Se connecter
POST /api/v1/auth/login
{
  "email": "dr.martin@hospital.com",
  "password": "SecurePass123!"
}
# → Récupérer le token JWT

# 4. Créer son profil professionnel
POST /api/v1/doctors/
Authorization: Bearer <token>
{
  "specialty": "pediatrician",
  "rpps_number": "98765432101",
  "office_address": "45 Avenue des Enfants",
  "office_city": "Lyon",
  "office_postal_code": "69003",
  "biography": "Pédiatre spécialisée en néonatologie",
  "languages": ["français", "anglais"],
  "experience_years": 10,
  "consultation_price": 45.0
}

# 5. Configurer ses créneaux de disponibilité
POST /api/v1/doctors/availability
{
  "date": "2025-11-10",
  "start_time": "09:00:00",
  "end_time": "09:30:00",
  "consultation_type": "in_person"
}
```

### Flux 2 : Gestion d'un rendez-vous

```bash
# 1. Voir ses rendez-vous du jour
GET /api/v1/doctors/appointments?start_date=2025-11-06T00:00:00&end_date=2025-11-06T23:59:59

# 2. Consulter les détails d'un rendez-vous
GET /api/v1/doctors/appointments/42

# 3. Confirmer le rendez-vous
PATCH /api/v1/doctors/appointments/42/status
{
  "status": "confirmed"
}

# 4. Après la consultation, marquer comme terminé
PATCH /api/v1/doctors/appointments/42/status
{
  "status": "completed",
  "doctor_notes": "Consultation normale. Patient en bonne santé."
}

# 5. Envoyer un document au patient
POST /api/v1/doctors/documents
patient_id: 10
title: "Certificat médical"
file: [fichier PDF]

# 6. Envoyer un message de suivi
POST /api/v1/doctors/messages
{
  "recipient_id": 10,
  "subject": "Suivi consultation",
  "content": "Bonjour, voici votre certificat médical.",
  "appointment_id": 42
}
```

### Flux 3 : Consultation des statistiques

```bash
# Obtenir un aperçu de son activité
GET /api/v1/doctors/statistics

# Voir la liste de tous ses patients
GET /api/v1/doctors/patients

# Consulter le dossier complet d'un patient
GET /api/v1/doctors/patients/10

# Voir l'historique des paiements
GET /api/v1/doctors/payments?status_filter=completed
```

## Prochaines étapes

### Fonctionnalités à développer :
1. **Module Patient** : Permettre aux patients de prendre rendez-vous, laisser des avis
2. **Notifications** : Emails/SMS automatiques pour rappels de rendez-vous
3. **Téléconsultation** : Intégration vidéo (WebRTC, Jitsi)
4. **Paiement en ligne** : Intégration Stripe/PayPal
5. **Calendrier** : Vue calendrier interactive des disponibilités
6. **Export de données** : PDF des ordonnances, factures
7. **Recherche avancée** : Rechercher des médecins par spécialité, ville, disponibilité

### Tests à ajouter :
- Tests unitaires des services
- Tests d'intégration des endpoints
- Tests de permissions et sécurité
- Tests de validation des données

## Support

Pour toute question ou problème :
- Vérifier les logs : `docker-compose logs backend`
- Consulter la documentation Swagger : `http://localhost:8000/docs`
- Vérifier les erreurs de validation dans les réponses 400/422
