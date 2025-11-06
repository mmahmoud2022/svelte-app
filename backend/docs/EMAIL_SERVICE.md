# Email Service Documentation

## Vue d'ensemble

Le service email supporte deux providers :
- **SMTP (Mailpit)** : Pour le développement et les tests
- **Amazon SES** : Pour la production

## Configuration

### Développement avec Mailpit

1. **Démarrer Mailpit avec Docker Compose** :
```bash
docker-compose up mailpit
```

2. **Configuration dans `.env`** :
```env
EMAIL_ENABLED=true
EMAIL_PROVIDER=smtp
SMTP_HOST=localhost  # ou "mailpit" si dans Docker
SMTP_PORT=1025
EMAIL_FROM=noreply@sante-app.com
```

3. **Interface Web Mailpit** :
- Accédez à http://localhost:8025
- Tous les emails envoyés s'affichent ici
- Parfait pour tester sans envoyer de vrais emails

### Production avec Amazon SES

1. **Prérequis AWS** :
   - Compte AWS actif
   - Accès IAM avec permissions SES
   - Domaine vérifié dans SES (ou emails vérifiés en sandbox)

2. **Configuration dans `.env`** :
```env
EMAIL_ENABLED=true
EMAIL_PROVIDER=ses
AWS_SES_REGION=us-east-1
AWS_SES_ACCESS_KEY_ID=your-access-key
AWS_SES_SECRET_ACCESS_KEY=your-secret-key
EMAIL_FROM=noreply@votredomaine.com
```

3. **Vérification du domaine dans SES** :
```bash
# Vérifier un email (mode sandbox)
aws ses verify-email-identity --email-address noreply@votredomaine.com

# Vérifier un domaine (production)
aws ses verify-domain-identity --domain votredomaine.com
```

4. **Permissions IAM nécessaires** :
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

## Utilisation

### Envoi d'email simple

```python
from app.services.email_service import get_email_service

email_service = get_email_service()

result = await email_service.send_email(
    to_email="patient@example.com",
    subject="Bienvenue",
    html_content="<h1>Bienvenue sur Santé!</h1>",
    plain_content="Bienvenue sur Santé!"
)

if result["success"]:
    print(f"Email envoyé avec succès! ID: {result['message_id']}")
else:
    print(f"Erreur: {result['error']}")
```

### Utilisation des templates

```python
# Confirmation de rendez-vous
result = await email_service.send_appointment_confirmation(
    to_email="patient@example.com",
    patient_name="Jean Dupont",
    doctor_name="Dr. Martin",
    appointment_date="15 novembre 2025",
    appointment_time="14:30",
    appointment_type="Consultation générale",
    cancellation_url="https://app.sante.com/cancel/abc123"
)

# Rappel de rendez-vous
result = await email_service.send_appointment_reminder(
    to_email="patient@example.com",
    patient_name="Jean Dupont",
    doctor_name="Dr. Martin",
    appointment_date="15 novembre 2025",
    appointment_time="14:30"
)

# Réinitialisation de mot de passe
result = await email_service.send_password_reset(
    to_email="user@example.com",
    first_name="Jean",
    reset_url="https://app.sante.com/reset-password/token123",
    expiry_minutes=15
)

# Ordonnance prête
result = await email_service.send_prescription_ready(
    to_email="patient@example.com",
    patient_name="Jean Dupont",
    medication_name="Amoxicilline 500mg",
    pickup_instructions="Pharmacie du Centre, disponible dès aujourd'hui"
)
```

### Avec pièces jointes

```python
attachments = [
    {
        "content": base64_encoded_content,
        "filename": "ordonnance.pdf",
        "type": "application/pdf"
    }
]

result = await email_service.send_email(
    to_email="patient@example.com",
    subject="Votre ordonnance",
    html_content="<p>Votre ordonnance est en pièce jointe.</p>",
    attachments=attachments
)
```

### Avec métadonnées (pour tracking)

```python
result = await email_service.send_email(
    to_email="patient@example.com",
    subject="Notification",
    html_content="<p>Contenu du message</p>",
    metadata={
        "user_id": "123",
        "notification_type": "appointment",
        "campaign": "reminders"
    }
)
```

## Intégration avec Celery (Tâches asynchrones)

Pour envoyer des emails en arrière-plan :

```python
from app.tasks import send_email_task

# Dans votre endpoint FastAPI
@router.post("/appointments/")
async def create_appointment(...):
    # ... créer le rendez-vous ...
    
    # Envoyer l'email de confirmation en arrière-plan
    send_email_task.delay(
        to_email=patient.email,
        template="appointment_confirmation",
        context={
            "patient_name": patient.name,
            "doctor_name": doctor.name,
            "appointment_date": appointment.date,
            "appointment_time": appointment.time,
            "appointment_type": appointment.type
        }
    )
    
    return appointment
```

## Coûts et Limites

### Mailpit (Développement)
- **Gratuit** : Open source
- **Limite** : Aucune (local)
- **Idéal pour** : Développement, tests

### Amazon SES
- **Gratuit** : 62,000 emails/mois si hébergé sur EC2
- **Payant** : $0.10 pour 1,000 emails ensuite
- **Limite** : 
  - Sandbox : 200 emails/jour, seulement emails vérifiés
  - Production : Jusqu'à 50,000 emails/jour (augmentable)
- **Idéal pour** : Production, volume élevé

## Tests

### Test local avec Mailpit

```bash
# Démarrer Mailpit
docker-compose up mailpit

# Dans un autre terminal, exécuter les tests
pytest tests/test_email_service.py -v

# Vérifier les emails à http://localhost:8025
```

### Test du service email

```python
# tests/test_email_service.py
import pytest
from app.services.email_service import get_email_service

@pytest.mark.asyncio
async def test_send_email():
    email_service = get_email_service()
    
    result = await email_service.send_email(
        to_email="test@example.com",
        subject="Test Email",
        html_content="<h1>Test</h1>",
        plain_content="Test"
    )
    
    assert result["success"] is True
    assert "message_id" in result
```

## Dépannage

### Erreur : "Email sending is disabled"
- Vérifiez `EMAIL_ENABLED=true` dans `.env`

### Erreur : "Connection refused" (SMTP)
- Vérifiez que Mailpit est démarré : `docker-compose ps mailpit`
- Vérifiez le host : `localhost` (local) ou `mailpit` (Docker)

### Erreur : "The security token included in the request is invalid" (SES)
- Vérifiez vos credentials AWS
- Vérifiez les permissions IAM

### Emails non reçus (SES)
- En mode sandbox, vérifiez que l'email destinataire est vérifié
- Vérifiez les limites d'envoi SES
- Consultez les bounces/complaints dans la console SES

## Migration Développement → Production

1. **Mettre à jour `.env`** :
```env
EMAIL_PROVIDER=ses  # Changez de "smtp" à "ses"
AWS_SES_REGION=us-east-1
AWS_SES_ACCESS_KEY_ID=...
AWS_SES_SECRET_ACCESS_KEY=...
```

2. **Vérifier le domaine** dans AWS SES

3. **Tester en staging** avant la production

4. **Monitorer** les bounces et complaints

## Ressources

- [Documentation Mailpit](https://github.com/axllent/mailpit)
- [Documentation Amazon SES](https://docs.aws.amazon.com/ses/)
- [Tarifs Amazon SES](https://aws.amazon.com/ses/pricing/)
- [Bonnes pratiques SES](https://docs.aws.amazon.com/ses/latest/dg/best-practices.html)
