# 🏗️ Architecture du Module Doctor

## 📊 Diagramme de l'architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Frontend)                            │
│                   React / Svelte / Vue.js                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/REST + JWT
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       API LAYER (FastAPI)                            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              ENDPOINTS (doctor.py)                            │   │
│  │  - 20 routes API REST                                        │   │
│  │  - Validation des requêtes (Pydantic)                        │   │
│  │  - Authentification JWT                                      │   │
│  │  - Gestion des erreurs HTTP                                  │   │
│  └────────────────────┬──────────────────────────────────────────┘   │
│                       │                                              │
│  ┌────────────────────▼──────────────────────────────────────────┐   │
│  │           MIDDLEWARE & SECURITY                               │   │
│  │  - JWT Authentication                                         │   │
│  │  - Role-based Access Control (RBAC)                          │   │
│  │  - CORS                                                       │   │
│  │  - Rate Limiting                                              │   │
│  └────────────────────┬──────────────────────────────────────────┘   │
│                       │                                              │
│  ┌────────────────────▼──────────────────────────────────────────┐   │
│  │            BUSINESS LOGIC (doctor_service.py)                 │   │
│  │  - Création/mise à jour profils                              │   │
│  │  - Gestion disponibilités                                    │   │
│  │  - Gestion rendez-vous                                       │   │
│  │  - Statistiques                                              │   │
│  │  - Messagerie                                                │   │
│  │  - Documents                                                 │   │
│  └────────────────────┬──────────────────────────────────────────┘   │
│                       │                                              │
│  ┌────────────────────▼──────────────────────────────────────────┐   │
│  │          DATA ACCESS LAYER (SQLAlchemy ORM)                   │   │
│  │  - Models (doctor.py)                                        │   │
│  │  - Schemas (doctor.py)                                       │   │
│  │  - Relations entre entités                                   │   │
│  └────────────────────┬──────────────────────────────────────────┘   │
└───────────────────────┼──────────────────────────────────────────────┘
                        │ SQL Queries
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                             │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ doctor_profiles  │  │ appointments     │  │ doctor_reviews   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ availabilities   │  │ payments         │  │ doctor_messages  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐                         │
│  │ patient_docs     │  │ doctor_settings  │                         │
│  └──────────────────┘  └──────────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
```

## 🗂️ Structure des fichiers

```
backend/
├── app/
│   ├── models/
│   │   ├── doctor.py                    # 🟢 8 modèles SQLAlchemy
│   │   │   ├── DoctorProfile
│   │   │   ├── DoctorAvailability
│   │   │   ├── Appointment
│   │   │   ├── DoctorReview
│   │   │   ├── DoctorMessage
│   │   │   ├── Payment
│   │   │   ├── PatientDocument
│   │   │   └── DoctorSettings
│   │   └── user.py                      # Relations ajoutées
│   │
│   ├── schemas/
│   │   └── doctor.py                    # 🟢 30+ schémas Pydantic
│   │       ├── DoctorProfileCreate
│   │       ├── DoctorProfileResponse
│   │       ├── AvailabilityCreate
│   │       ├── AppointmentResponse
│   │       └── ...
│   │
│   ├── services/
│   │   └── doctor_service.py            # 🟢 Logique métier
│   │       ├── create_doctor_profile()
│   │       ├── create_availability()
│   │       ├── get_doctor_appointments()
│   │       ├── get_doctor_statistics()
│   │       └── ...
│   │
│   └── api/v1/
│       ├── __init__.py                  # 🟡 Router ajouté
│       └── endpoints/
│           └── doctor.py                # 🟢 20 routes API
│               ├── POST /doctors/
│               ├── GET /doctors/me
│               ├── PUT /doctors/me
│               └── ...
│
├── alembic/versions/
│   └── e7f0g1h2a3b4_add_doctor...py    # 🟢 Migration
│
├── tests/
│   ├── conftest.py                      # 🟢 Fixtures pytest
│   └── test_doctor_module.py            # 🟢 Tests unitaires
│
├── DOCTOR_MODULE_DOCUMENTATION.md       # 📚 Doc complète
├── DOCTOR_MODULE_README.md              # 📚 README
├── DOCTOR_QUICK_START.md                # 🚀 Guide rapide
└── test_doctor_module.sh                # 🧪 Script de test
```

## 🔄 Flux de données

### 1️⃣ Création d'un profil médecin

```
Client                API               Service            Database
  │                   │                   │                   │
  ├─POST /doctors/───►│                   │                   │
  │  + JWT Token      │                   │                   │
  │                   ├─Validate JWT────►│                   │
  │                   │                   │                   │
  │                   ├─Validate data────►│                   │
  │                   │  (Pydantic)       │                   │
  │                   │                   │                   │
  │                   │                   ├─Check role────── │
  │                   │                   │  (DOCTOR)         │
  │                   │                   │                   │
  │                   │                   ├─Check RPPS────── │
  │                   │                   │  (unique)         │
  │                   │                   │                   │
  │                   │                   ├─INSERT profile──►│
  │                   │                   │                   │
  │                   │                   ├─INSERT settings─►│
  │                   │                   │                   │
  │                   │◄──Profile created─┤                   │
  │                   │                   │                   │
  │◄──201 Created────┤                   │                   │
  │   + Profile data  │                   │                   │
```

### 2️⃣ Création d'un créneau de disponibilité

```
Client                API               Service            Database
  │                   │                   │                   │
  ├─POST availability►│                   │                   │
  │                   ├─Validate JWT────►│                   │
  │                   │                   │                   │
  │                   │                   ├─Get profile────► │
  │                   │                   │                   │
  │                   │                   ├─Check overlap──► │
  │                   │                   │                   │
  │                   │                   ├─INSERT slot────► │
  │                   │                   │                   │
  │◄──201 Created────┤◄──Slot created────┤                   │
```

### 3️⃣ Mise à jour du statut d'un rendez-vous

```
Client                API               Service            Database
  │                   │                   │                   │
  ├─PATCH status/42──►│                   │                   │
  │  "completed"      │                   │                   │
  │                   ├─Validate JWT────►│                   │
  │                   │                   │                   │
  │                   │                   ├─Get appointment─►│
  │                   │                   │                   │
  │                   │                   ├─UPDATE status───►│
  │                   │                   ├─SET completed_at►│
  │                   │                   │                   │
  │                   │                   ├─INCREMENT total─►│
  │                   │                   │  consultations    │
  │                   │                   │                   │
  │                   │                   ├─Free slot if────►│
  │                   │                   │  cancelled        │
  │                   │                   │                   │
  │◄──200 OK──────────┤◄──Updated─────────┤                   │
```

## 🔐 Sécurité - Couches de protection

```
┌─────────────────────────────────────────────────────────────┐
│ NIVEAU 1 : AUTHENTIFICATION                                 │
│ - JWT Token requis sur tous les endpoints                   │
│ - Token valide et non expiré                                │
│ - User actif et vérifié                                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│ NIVEAU 2 : AUTORISATION (RBAC)                             │
│ - require_role([UserRole.DOCTOR])                          │
│ - Vérification du rôle dans le JWT                         │
│ - Rejet si rôle incorrect (403)                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│ NIVEAU 3 : ISOLATION DES DONNÉES                           │
│ - Médecin accède uniquement à SES données                  │
│ - Filtrage par doctor_id/user_id                           │
│ - Pas d'accès inter-médecins                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│ NIVEAU 4 : VALIDATION DES DONNÉES                          │
│ - Schémas Pydantic stricts                                  │
│ - Types, formats, contraintes                              │
│ - Prévention injection SQL (ORM)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│ NIVEAU 5 : RÈGLES MÉTIER                                   │
│ - RPPS unique                                               │
│ - Pas de créneaux chevauchants                             │
│ - Accès dossier si consultation antérieure                 │
│ - Créneau réservé non supprimable                          │
└─────────────────────────────────────────────────────────────┘
```

## 💾 Modèle de données - Relations

```
┌─────────────┐
│    User     │
│             │
│ id          │◄──────────────────┐
│ email       │                   │
│ role        │                   │
└──────┬──────┘                   │
       │ 1                        │
       │                          │
       │ 1                        │
       ▼                          │
┌──────────────────┐              │
│ DoctorProfile    │              │
│                  │              │ N
│ id               │         ┌────┴──────────┐
│ user_id  (FK)    │         │  Appointment  │
│ specialty        │         │               │
│ rpps_number (!)  │    ┌───►│ id            │
│ biography        │    │ 1  │ doctor_id (FK)│
│ consultation_fee │    │    │ patient_id(FK)│
└──────┬───────────┘    │    │ status        │
       │ 1              │    │ date          │
       │                │    └───────────────┘
       ├────────────────┤
       │                │
       │ N              │ N
       ▼                ▼
┌──────────────┐  ┌─────────────┐
│Availability  │  │   Review    │
│              │  │             │
│ date         │  │ rating      │
│ start_time   │  │ comment     │
│ end_time     │  │ response    │
└──────────────┘  └─────────────┘

       │
       ├─────────N──────┬─────────N───────┬──────N──────┐
       │                │                 │             │
       ▼                ▼                 ▼             ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────┐
│  Message   │  │  Payment   │  │  Document  │  │Settings │
│            │  │            │  │            │  │         │
│ content    │  │ amount     │  │ file_path  │  │ notifs  │
│ is_read    │  │ status     │  │ title      │  │ language│
└────────────┘  └────────────┘  └────────────┘  └─────────┘

Légende:
  (FK) = Foreign Key
  (!)  = Unique constraint
  N    = Relation one-to-many
  1    = Relation many-to-one
```

## 🔄 États et transitions

### États d'un rendez-vous

```
     ┌─────────┐
     │ PENDING │ (Initial)
     └────┬────┘
          │
          ├──────────┬──────────┐
          │          │          │
          ▼          ▼          ▼
    ┌──────────┐  ┌─────────┐  ┌─────────┐
    │CONFIRMED │  │CANCELLED│  │ NO_SHOW │
    └────┬─────┘  └─────────┘  └─────────┘
         │
         ▼
    ┌──────────┐
    │COMPLETED │ (Final)
    └──────────┘
```

### États d'un paiement

```
    ┌─────────┐
    │ PENDING │ (Initial)
    └────┬────┘
         │
         ├───────────┬──────────┐
         │           │          │
         ▼           ▼          ▼
    ┌──────────┐  ┌──────┐  ┌────────┐
    │COMPLETED │  │FAILED│  │REFUNDED│
    └──────────┘  └──────┘  └────────┘
```

## 📈 Métriques et indicateurs

### Statistiques disponibles

```
┌───────────────────────────────────────────────┐
│            DOCTOR STATISTICS                   │
├───────────────────────────────────────────────┤
│                                               │
│  📊 Activité                                  │
│    - Total consultations                      │
│    - Consultations terminées                  │
│    - Consultations annulées                   │
│    - Taux d'annulation                        │
│                                               │
│  ⭐ Réputation                                │
│    - Note moyenne                             │
│    - Nombre d'avis                            │
│                                               │
│  👥 Patients                                  │
│    - Nouveaux patients                        │
│    - Patients récurrents                      │
│                                               │
│  💰 Revenus                                   │
│    - Revenus totaux                           │
│    - Revenus en attente                       │
│                                               │
│  📅 Agenda                                    │
│    - Rendez-vous à venir                      │
│    - Rendez-vous du jour                      │
│                                               │
└───────────────────────────────────────────────┘
```

## 🚀 Performance

### Optimisations implémentées

1. **Index de base de données**
   - Index sur `doctor_id`, `patient_id`, `date`
   - Index sur `status`, `rpps_number`
   - Requêtes optimisées

2. **Eager Loading**
   - `joinedload()` pour les relations
   - Évite le problème N+1

3. **Pagination**
   - Limite par défaut : 50 items
   - Maximum : 100 items
   - Offset/limit pour la performance

4. **Validation Pydantic**
   - Validation rapide des données
   - Erreurs précoces

## 🔮 Évolutions futures

```
Phase 1 (Actuel)      Phase 2              Phase 3
─────────────────     ────────────────     ──────────────────
✅ Profil médecin     📅 Calendrier        🎥 Téléconsult
✅ Disponibilités     📧 Notifications     💳 Paiement en ligne
✅ Rendez-vous        🔍 Recherche avancée 📊 Analytics avancés
✅ Messages           🤖 Suggestions IA    🌍 Multi-langues
✅ Documents          📱 App mobile        🔗 Intégrations
✅ Statistiques       ⚡ Cache Redis       🏥 Dossier médical
```

---

**Architecture solide, sécurisée et évolutive ! 🎉**
