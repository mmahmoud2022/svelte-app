# 🩺 Module Doctor - Guide de Démarrage Rapide

## 🚀 Mise en route en 5 minutes

### Étape 1 : Appliquer la migration

```bash
cd /home/alpha/fastapi-frontend/backend
alembic upgrade head
```

### Étape 2 : Redémarrer le backend

```bash
cd /home/alpha/fastapi-frontend
docker-compose restart backend
```

### Étape 3 : Vérifier que tout fonctionne

Ouvrir dans un navigateur : **http://localhost:8000/docs**

Vous devriez voir une nouvelle section **"doctors"** avec 20 endpoints.

## 📋 Checklist de vérification

- [ ] Migration appliquée (`alembic upgrade head`)
- [ ] Backend redémarré
- [ ] 20 routes visibles dans Swagger
- [ ] Tables créées dans PostgreSQL

### Vérifier les tables PostgreSQL

```bash
docker-compose exec postgres psql -U postgres -d healthcare_db -c "\dt"
```

Vous devriez voir :
- `doctor_profiles`
- `doctor_availabilities`
- `appointments`
- `doctor_reviews`
- `doctor_messages`
- `payments`
- `patient_documents`
- `doctor_settings`

## 🧪 Test rapide avec curl

### 1. Créer un compte médecin

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.test@example.com",
    "password": "SecurePass123!",
    "first_name": "Jean",
    "last_name": "Dupont",
    "role": "doctor"
  }'
```

### 2. Se connecter

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.test@example.com",
    "password": "SecurePass123!"
  }'
```

**Copier le token JWT retourné !**

### 3. Créer son profil médecin

```bash
TOKEN="VOTRE_TOKEN_ICI"

curl -X POST http://localhost:8000/api/v1/doctors/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "specialty": "cardiologist",
    "rpps_number": "12345678901",
    "office_address": "123 Rue de la Santé",
    "office_city": "Paris",
    "office_postal_code": "75014",
    "biography": "Cardiologue avec 15 ans d'\''expérience",
    "languages": ["français", "anglais"],
    "experience_years": 15,
    "consultation_price": 50.0
  }'
```

### 4. Créer un créneau de disponibilité

```bash
curl -X POST http://localhost:8000/api/v1/doctors/availability \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-11-15",
    "start_time": "09:00:00",
    "end_time": "09:30:00",
    "consultation_type": "in_person"
  }'
```

### 5. Voir ses statistiques

```bash
curl -X GET http://localhost:8000/api/v1/doctors/statistics \
  -H "Authorization: Bearer $TOKEN"
```

## 🎯 Les 20 Endpoints Disponibles

### Profil (4)
1. `POST /doctors/` - Créer profil
2. `GET /doctors/me` - Mon profil
3. `PUT /doctors/me` - Mettre à jour
4. `GET /doctors/{id}` - Profil public

### Disponibilités (3)
5. `POST /doctors/availability` - Créer créneau
6. `GET /doctors/{id}/availability` - Voir créneaux
7. `DELETE /doctors/availability/{id}` - Supprimer

### Rendez-vous (3)
8. `GET /doctors/appointments` - Liste
9. `GET /doctors/appointments/{id}` - Détails
10. `PATCH /doctors/appointments/{id}/status` - Statut

### Patients (2)
11. `GET /doctors/patients` - Liste patients
12. `GET /doctors/patients/{id}` - Dossier

### Autres (8)
13. `GET /doctors/statistics` - Stats
14. `PUT /doctors/settings` - Paramètres
15. `POST /doctors/documents` - Upload doc
16. `GET /doctors/messages` - Messagerie
17. `POST /doctors/messages` - Envoyer
18. `GET /doctors/payments` - Paiements
19. `GET /doctors/reviews` - Avis
20. `POST /doctors/reviews/{id}/respond` - Répondre

## 📊 Structure des données principales

### DoctorProfile
```json
{
  "specialty": "cardiologist | pediatrician | ...",
  "rpps_number": "11 chiffres uniques",
  "office_city": "Paris",
  "biography": "Description...",
  "languages": ["français", "anglais"],
  "experience_years": 15,
  "consultation_price": 50.0,
  "accepts_new_patients": true
}
```

### Availability
```json
{
  "date": "2025-11-15",
  "start_time": "09:00:00",
  "end_time": "09:30:00",
  "consultation_type": "in_person | teleconsultation | both",
  "location": "Cabinet Paris 14ème"
}
```

### Appointment
```json
{
  "appointment_date": "2025-11-15T09:00:00Z",
  "status": "pending | confirmed | completed | cancelled | no_show",
  "consultation_type": "in_person",
  "reason": "Consultation de routine",
  "doctor_notes": "Notes privées du médecin"
}
```

## 🔐 Sécurité

### Authentification requise
Tous les endpoints nécessitent un JWT Bearer token :
```
Authorization: Bearer <votre_token>
```

### Rôle DOCTOR requis
La plupart des endpoints nécessitent `role="doctor"` sauf :
- `GET /doctors/{id}` (profil public)
- `GET /doctors/{id}/availability` (créneaux publics)

### Isolation des données
- Un médecin ne voit que **ses propres** données
- Accès aux dossiers patients **uniquement si consultation**
- RPPS unique par médecin

## 🐛 Problèmes fréquents

### "Table does not exist"
→ Exécuter `alembic upgrade head`

### "403 Forbidden"
→ Vérifier que l'utilisateur a `role="doctor"`

### "RPPS déjà utilisé"
→ Chaque RPPS doit être unique (11 chiffres)

### "Créneau chevauche"
→ Pas de créneaux qui se chevauchent le même jour

## 📚 Documentation complète

- **README complet** : `DOCTOR_MODULE_README.md`
- **Documentation API** : `DOCTOR_MODULE_DOCUMENTATION.md`
- **Swagger UI** : http://localhost:8000/docs
- **Tests** : `test_doctor_module.sh`

## ✅ Validation de l'installation

Exécuter le script de test complet :

```bash
cd /home/alpha/fastapi-frontend/backend
./test_doctor_module.sh
```

Le script va :
1. ✅ Créer un compte médecin
2. ✅ Se connecter
3. ✅ Créer un profil
4. ✅ Créer des créneaux
5. ✅ Tester toutes les routes

## 🎉 C'est tout !

Le module Doctor est maintenant **opérationnel** !

### Prochaines étapes suggérées :

1. **Tester dans Swagger** : http://localhost:8000/docs
2. **Développer le frontend** : Interface pour les médecins
3. **Module Patient** : Permettre la prise de RDV
4. **Notifications** : Emails/SMS automatiques
5. **Téléconsultation** : Intégration vidéo

---

💡 **Besoin d'aide ?**
- Vérifier les logs : `docker-compose logs backend`
- Consulter Swagger : http://localhost:8000/docs
- Lire la doc complète : `DOCTOR_MODULE_DOCUMENTATION.md`
