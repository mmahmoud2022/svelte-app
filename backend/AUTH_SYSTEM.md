# 🏥 Santé - Système d'Authentification Complet

## 📋 Vue d'ensemble

Système d'authentification moderne inspiré de Doctolib pour une plateforme médicale avec support complet pour :

- **3 types d'utilisateurs** : Patients, Praticiens (Médecins), Administrateurs
- **Authentification complète** : Registration, Login, JWT tokens
- **Vérification email** : Tokens sécurisés avec expiration
- **Reset de mot de passe** : Process complet avec tokens
- **Sécurité renforcée** : Rate limiting, password strength, audit logs

## 🏗️ Architecture

### Modèles de Base de Données

1. **User** - Modèle utilisateur principal avec tous les profils
   - Support multi-rôles (PATIENT, DOCTOR, ADMIN)
   - Informations professionnelles (médecins)
   - Gestion des permissions (admins)
   
2. **VerificationToken** - Tokens de vérification email et reset password
3. **RefreshToken** - JWT refresh tokens avec tracking des devices
4. **LoginAttempt** - Audit des tentatives de connexion pour sécurité

### Endpoints API (Préfixe: `/api/v1/auth`)

#### **Registration**
- `POST /register/patient` - Inscription patient
- `POST /register/practitioner` - Inscription praticien
- `POST /register/admin` - Inscription admin (require secret)

#### **Authentication**
- `POST /login` - Connexion (returns access + refresh tokens)
- `POST /refresh` - Renouveler l'access token
- `POST /logout` - Déconnexion
- `POST /logout-all` - Déconnexion de tous les appareils

#### **Email Verification**
- `POST /verify-email` - Vérifier email avec token
- `POST /resend-verification` - Renvoyer l'email de vérification

#### **Password Management**
- `POST /request-password-reset` - Demander reset de password
- `POST /reset-password` - Réinitialiser password avec token
- `POST /change-password` - Changer password (when logged in)

#### **User Info**
- `GET /me` - Obtenir les informations de l'utilisateur connecté

## 🚀 Installation et Démarrage

### 1. Démarrer les services (Docker)

```bash
cd /home/alpha/fastapi-frontend

# Démarrer PostgreSQL
docker compose up postgres -d

# Démarrer Mailpit (pour les emails)
docker compose up mailpit -d

# Démarrer Redis (optionnel, pour Celery)
docker compose up redis -d
```

### 2. Créer et appliquer les migrations

```bash
cd backend

# Créer la base de données (si nécessaire)
# La DB est créée automatiquement par Docker

# Appliquer les migrations
/home/alpha/fastapi-frontend/.venv/bin/alembic upgrade head
```

### 3. Démarrer l'application FastAPI

```bash
cd backend

# Mode développement avec hot reload
/home/alpha/fastapi-frontend/.venv/bin/fastapi dev app/main.py

# OU mode production
/home/alpha/fastapi-frontend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Accès aux services

- **API** : http://localhost:8000
- **Documentation interactive** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **Mailpit (emails)** : http://localhost:8025
- **Health Check** : http://localhost:8000/health

## 📝 Exemples d'utilisation

### 1. Inscription Patient

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/patient" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "SecurePass123",
    "first_name": "Jean",
    "last_name": "Dupont",
    "phone": "+33612345678",
    "marketing_consent": true
  }'
```

**Réponse** :
```json
{
  "id": 1,
  "email": "patient@example.com",
  "first_name": "Jean",
  "last_name": "Dupont",
  "role": "patient",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-05T..."
}
```

### 2. Inscription Praticien

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/practitioner" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.martin@example.com",
    "password": "DoctorPass123",
    "first_name": "Marie",
    "last_name": "Martin",
    "phone": "+33687654321",
    "specialization": "Cardiologie",
    "license_number": "LIC123456",
    "bio": "Cardiologue avec 10 ans d'\''expérience",
    "consultation_fee": 5000,
    "languages_spoken": "Français, Anglais"
  }'
```

### 3. Inscription Admin

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/admin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sante.com",
    "password": "AdminPass123",
    "first_name": "Admin",
    "last_name": "System",
    "admin_secret": "ADMIN_SECRET_2025_CHANGE_IN_PRODUCTION"
  }'
```

### 4. Vérification Email

**Étape 1** : L'utilisateur reçoit un email avec un token (visible dans Mailpit : http://localhost:8025)

**Étape 2** : Vérifier l'email avec le token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_FROM_EMAIL"
  }'
```

### 5. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "SecurePass123",
    "remember_me": true
  }'
```

**Réponse** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "refresh_token_string",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "role": "patient",
    "is_verified": true
  }
}
```

### 6. Utiliser l'Access Token

```bash
# Obtenir les infos de l'utilisateur connecté
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Reset de Password

**Étape 1** : Demander un reset
```bash
curl -X POST "http://localhost:8000/api/v1/auth/request-password-reset" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com"
  }'
```

**Étape 2** : Reset avec le token (reçu par email)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_FROM_EMAIL",
    "new_password": "NewSecurePass123"
  }'
```

## 🔒 Sécurité

### Validation des Passwords

Les passwords doivent respecter :
- Minimum 8 caractères
- Au moins 1 majuscule
- Au moins 1 minuscule
- Au moins 1 chiffre

### Rate Limiting

- 5 tentatives de login max par 15 minutes
- Protection contre le brute force

### Tokens

- **Access Token** : 30 minutes (configurable)
- **Refresh Token** : 7 jours (30 jours avec "remember me")
- **Verification Token** : 24 heures
- **Reset Password Token** : 1 heure

## 📧 Emails

Tous les emails sont envoyés via Mailpit en développement.

**Accédez à l'interface Mailpit** : http://localhost:8025

Types d'emails envoyés :
- ✉️ Vérification d'email (registration)
- 🔐 Reset de password
- ✅ Confirmation d'actions

## 🧪 Tests

### Test Manuel avec Swagger UI

1. Ouvrir http://localhost:8000/docs
2. Tester chaque endpoint interactivement
3. Voir les réponses en temps réel

### Workflow de Test Complet

```bash
# 1. Inscription
POST /api/v1/auth/register/patient

# 2. Vérifier email dans Mailpit
# http://localhost:8025

# 3. Vérifier email
POST /api/v1/auth/verify-email

# 4. Login
POST /api/v1/auth/login

# 5. Utiliser access token pour accéder aux ressources protégées
GET /api/v1/auth/me
```

## 🗂️ Structure des Fichiers Créés

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py          # Router API v1
│   │       └── endpoints/
│   │           └── auth.py          # 🆕 Endpoints authentification
│   ├── core/
│   │   ├── dependencies.py          # 🆕 Dependencies auth (get_current_user, etc.)
│   │   └── ...
│   ├── models/
│   │   ├── __init__.py              # ✏️ Export modèles
│   │   ├── user.py                  # User model (existant)
│   │   └── auth.py                  # 🆕 VerificationToken, RefreshToken, LoginAttempt
│   ├── schemas/
│   │   └── auth.py                  # 🆕 Schémas Pydantic pour auth
│   ├── services/
│   │   ├── auth_service.py          # 🆕 Service authentification
│   │   └── email_service.py         # Service email (existant)
│   ├── templates/
│   │   └── email_templates.py       # Templates email (existant)
│   └── main.py                      # ✏️ Ajout routes auth
├── alembic/
│   ├── env.py                       # ✏️ Configuration Alembic
│   └── versions/                    # Migrations
├── alembic.ini                      # ✏️ Config Alembic
├── .env                             # Variables d'environnement
└── AUTH_SYSTEM.md                   # 🆕 Cette documentation
```

## 🎯 Prochaines Étapes

1. ✅ Système d'authentification - **TERMINÉ**
2. ⏳ Tests unitaires automatisés
3. ⏳ Intégration frontend Svelte
4. ⏳ OAuth2 (Google, Facebook)
5. ⏳ Two-Factor Authentication (2FA)
6. ⏳ Rate limiting avancé
7. ⏳ Session management dashboard

## 🐛 Dépannage

### Erreur : "Connection refused" (PostgreSQL)

```bash
# Vérifier que PostgreSQL est démarré
docker compose ps postgres

# Démarrer PostgreSQL
docker compose up postgres -d
```

### Erreur : "Email not sent"

```bash
# Vérifier que Mailpit est démarré
docker compose ps mailpit

# Démarrer Mailpit
docker compose up mailpit -d

# Vérifier les logs
docker compose logs mailpit
```

### Erreur : "Invalid credentials"

- Vérifier que l'email est bien vérifié (`is_verified=true`)
- Vérifier le password (sensible à la casse)
- Vérifier les logs dans le terminal

## 📚 Documentation Complète

- **API Documentation** : http://localhost:8000/docs
- **Email Service** : `docs/EMAIL_SERVICE.md`
- **Configuration** : `.env.example`

## 🎉 C'est Prêt !

Votre système d'authentification complet est opérationnel ! Vous pouvez maintenant :

1. ✅ Créer des comptes (patients, praticiens, admins)
2. ✅ Vérifier les emails
3. ✅ Se connecter avec JWT
4. ✅ Réinitialiser les passwords
5. ✅ Gérer les sessions multi-appareils

**Testez maintenant avec Swagger UI** : http://localhost:8000/docs 🚀
