# Configuration Email - Mailpit + Amazon SES

## 📧 Changements effectués

### 1. Dépendances ajoutées (`requirements.txt`)
- `boto3==1.35.76` - Client Amazon SES
- `aiosmtplib==3.0.2` - Client SMTP asynchrone

### 2. Docker Compose
Ajout du service **Mailpit** :
- Interface web : http://localhost:8025
- SMTP server : localhost:1025

### 3. Configuration (`app/core/config.py`)
Nouvelles variables d'environnement :
- `EMAIL_PROVIDER` : "smtp" (dev) ou "ses" (prod)
- `SMTP_*` : Configuration SMTP/Mailpit
- `AWS_SES_*` : Configuration Amazon SES

### 4. Service Email (`app/services/email_service.py`)
- Support SMTP (Mailpit) pour développement
- Support Amazon SES pour production
- Méthodes helper pour templates courants

### 5. Tâches Celery (`app/tasks.py`)
- Envoi d'emails en arrière-plan
- Rappels automatiques de rendez-vous
- Réinitialisation de mot de passe

## 🚀 Installation et démarrage

### 1. Installer les dépendances
```bash
cd backend
pip install -r requirements.txt
```

### 2. Démarrer Mailpit
```bash
docker-compose up mailpit
```

### 3. Configurer les variables d'environnement
```bash
cp .env.example .env
```

Éditer `.env` :
```env
EMAIL_ENABLED=true
EMAIL_PROVIDER=smtp
SMTP_HOST=localhost
SMTP_PORT=1025
EMAIL_FROM=noreply@sante-app.com
```

### 4. Démarrer l'application
```bash
fastapi dev app/main.py
```

### 5. Voir les emails
Ouvrez http://localhost:8025 dans votre navigateur

## 📝 Utilisation

### Envoi simple
```python
from app.services.email_service import get_email_service

email_service = get_email_service()
result = await email_service.send_email(
    to_email="patient@example.com",
    subject="Test",
    html_content="<h1>Hello!</h1>"
)
```

### Avec Celery (arrière-plan)
```python
from app.tasks import send_email_task

send_email_task.delay(
    to_email="patient@example.com",
    subject="Test",
    html_content="<h1>Hello!</h1>"
)
```

### Templates prédéfinis
```python
# Confirmation de rendez-vous
await email_service.send_appointment_confirmation(
    to_email="patient@example.com",
    patient_name="Jean Dupont",
    doctor_name="Dr. Martin",
    appointment_date="15 nov 2025",
    appointment_time="14:30",
    appointment_type="Consultation"
)

# Réinitialisation mot de passe
await email_service.send_password_reset(
    to_email="user@example.com",
    first_name="Jean",
    reset_url="https://app.com/reset/token"
)
```

## 🌍 Migration vers Production (Amazon SES)

### 1. Créer un compte AWS et configurer SES
```bash
# Vérifier un domaine
aws ses verify-domain-identity --domain votredomaine.com

# Ou vérifier un email (sandbox)
aws ses verify-email-identity --email-address noreply@votredomaine.com
```

### 2. Créer un utilisateur IAM avec permissions SES
```json
{
  "Effect": "Allow",
  "Action": ["ses:SendEmail", "ses:SendRawEmail"],
  "Resource": "*"
}
```

### 3. Mettre à jour `.env`
```env
EMAIL_PROVIDER=ses
AWS_SES_REGION=us-east-1
AWS_SES_ACCESS_KEY_ID=AKIA...
AWS_SES_SECRET_ACCESS_KEY=...
```

### 4. Redémarrer l'application
Le service basculera automatiquement sur Amazon SES !

## 💰 Coûts

- **Mailpit** : Gratuit (développement)
- **Amazon SES** : 
  - 62,000 emails/mois gratuits (avec EC2)
  - $0.10 / 1,000 emails ensuite
  - Très économique !

## 📚 Documentation complète

Voir [docs/EMAIL_SERVICE.md](docs/EMAIL_SERVICE.md) pour la documentation complète.

## 🔍 Tests

```bash
# Tester l'envoi d'email
pytest tests/test_email_service.py -v

# Vérifier les emails dans Mailpit
# http://localhost:8025
```

## ❓ Dépannage

**Erreur "Connection refused"**
- Vérifiez que Mailpit est démarré : `docker-compose ps mailpit`
- Si en Docker, utilisez `SMTP_HOST=mailpit` au lieu de `localhost`

**Les emails n'arrivent pas**
- Vérifiez `EMAIL_ENABLED=true`
- Consultez les logs : `docker-compose logs backend`
- Pour SES : vérifiez que le domaine/email est vérifié

## 🎯 Prochaines étapes

1. ✅ Configuration Mailpit (développement)
2. ✅ Service email avec SMTP et SES
3. ✅ Templates d'emails
4. ✅ Tâches Celery
5. ⏳ Tests unitaires
6. ⏳ Configuration SES production
7. ⏳ Monitoring et alertes
