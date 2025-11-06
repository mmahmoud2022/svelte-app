# Endpoints Admin pour la Gestion des Utilisateurs

## Date : 5 novembre 2025

## Vue d'ensemble

Cette documentation décrit les endpoints admin permettant de gérer les comptes utilisateurs (patients et docteurs) : lister, suspendre, réactiver et supprimer.

---

## Endpoints Disponibles

### 1. Lister Tous les Utilisateurs
**Endpoint** : `GET /api/v1/admin/users`

Liste tous les utilisateurs avec filtres optionnels et pagination.

**Authentification** : Requiert le rôle ADMIN

**Query Parameters** :
- `role` (optionnel) : Filtrer par rôle (`patient`, `doctor`, `admin`)
- `is_active` (optionnel) : Filtrer par statut actif (`true`/`false`)
- `is_verified` (optionnel) : Filtrer par vérification email (`true`/`false`)
- `admin_approved` (optionnel) : Filtrer par approbation admin (`true`/`false`)
- `skip` (optionnel) : Pagination - nombre d'enregistrements à sauter (défaut: 0)
- `limit` (optionnel) : Pagination - nombre max d'enregistrements (défaut: 100, max: 500)

**Exemples** :
```bash
# Tous les utilisateurs
curl -X GET "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Seulement les patients
curl -X GET "http://localhost:8000/api/v1/admin/users?role=patient" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Seulement les comptes inactifs/suspendus
curl -X GET "http://localhost:8000/api/v1/admin/users?is_active=false" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Médecins non approuvés et actifs
curl -X GET "http://localhost:8000/api/v1/admin/users?role=doctor&admin_approved=false&is_active=true" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Pagination
curl -X GET "http://localhost:8000/api/v1/admin/users?skip=0&limit=50" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Réponse** :
```json
[
  {
    "id": 1,
    "email": "patient@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "role": "patient",
    "is_active": true,
    "is_verified": false,
    "admin_approved": true,
    ...
  }
]
```

---

### 2. Détails d'un Utilisateur
**Endpoint** : `GET /api/v1/admin/users/{user_id}`

Obtenir les détails complets d'un utilisateur spécifique.

**Authentification** : Requiert le rôle ADMIN

**Exemple** :
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users/5" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Réponse** :
```json
{
  "id": 5,
  "email": "dr.smith@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "role": "doctor",
  "specialization": "Cardiologie",
  "is_active": true,
  "is_verified": true,
  "admin_approved": true,
  "consultation_fee": 5000,
  ...
}
```

---

### 3. Suspendre un Utilisateur
**Endpoint** : `POST /api/v1/admin/users/{user_id}/suspend`

Suspendre un compte utilisateur (patient ou docteur).

**Authentification** : Requiert le rôle ADMIN

**Restrictions** :
- ❌ Ne peut pas suspendre un compte admin
- ❌ Ne peut pas se suspendre soi-même

**Body** :
```json
{
  "reason": "Raison de la suspension"
}
```

**Actions automatiques** :
- ✅ `is_active` passe à `false`
- ✅ `suspension_reason` est définie
- ✅ Tous les tokens actifs sont révoqués
- ✅ Email de notification envoyé à l'utilisateur

**Exemple** :
```bash
curl -X POST "http://localhost:8000/api/v1/admin/users/5/suspend" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Comportement inapproprié"
  }'
```

**Réponse** :
```json
{
  "message": "Le compte de John Smith a été suspendu",
  "success": true
}
```

**Email envoyé** :
```
Objet: Suspension de votre compte - Santé

Bonjour John Smith,

Nous vous informons que votre compte médecin a été suspendu.

Raison : Comportement inapproprié

Si vous pensez qu'il s'agit d'une erreur ou si vous souhaitez obtenir 
plus d'informations, veuillez contacter notre équipe de support.

Cordialement,
L'équipe Santé
```

---

### 4. Réactiver un Utilisateur
**Endpoint** : `POST /api/v1/admin/users/{user_id}/activate`

Réactiver un compte utilisateur suspendu.

**Authentification** : Requiert le rôle ADMIN

**Actions automatiques** :
- ✅ `is_active` passe à `true`
- ✅ `suspension_reason` est effacée
- ✅ Email de notification envoyé à l'utilisateur

**Exemple** :
```bash
curl -X POST "http://localhost:8000/api/v1/admin/users/5/activate" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Réponse** :
```json
{
  "message": "Le compte de John Smith a été réactivé",
  "success": true
}
```

**Email envoyé** :
```
Objet: Réactivation de votre compte - Santé

Bonjour John Smith,

Nous vous informons que votre compte médecin a été réactivé.

Vous pouvez maintenant vous reconnecter à notre plateforme.

[Se connecter]

Bienvenue de nouveau sur Santé !
```

---

### 5. Supprimer un Utilisateur (PERMANENT)
**Endpoint** : `DELETE /api/v1/admin/users/{user_id}`

**⚠️ ATTENTION : Suppression permanente et irréversible !**

Supprime définitivement un compte utilisateur et toutes ses données associées.

**Authentification** : Requiert le rôle ADMIN

**Restrictions** :
- ❌ Ne peut pas supprimer un compte admin
- ❌ Ne peut pas se supprimer soi-même

**Actions automatiques** :
- ✅ Suppression de tous les tokens de vérification
- ✅ Suppression de tous les refresh tokens
- ✅ Suppression du compte utilisateur
- ✅ Email de confirmation envoyé

**Exemple** :
```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/users/5" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Réponse** :
```json
{
  "message": "Le compte de John Smith a été supprimé définitivement",
  "success": true
}
```

**Email envoyé** :
```
Objet: Suppression de votre compte - Santé

Bonjour John Smith,

Nous vous confirmons que votre compte médecin a été supprimé de notre plateforme.

Toutes vos données personnelles ont été supprimées conformément à notre 
politique de confidentialité.

Si vous n'êtes pas à l'origine de cette action ou si vous avez des questions, 
veuillez contacter notre équipe de support.

Cordialement,
L'équipe Santé
```

**Note GDPR** :
Pour la conformité GDPR, il est recommandé d'utiliser une suppression douce (soft delete) 
ou l'anonymisation des données plutôt qu'une suppression définitive.

---

### 6. Lister Tous les Patients
**Endpoint** : `GET /api/v1/admin/patients`

Liste tous les patients avec filtres optionnels.

**Authentification** : Requiert le rôle ADMIN

**Query Parameters** :
- `is_active` (optionnel) : Filtrer par statut actif
- `is_verified` (optionnel) : Filtrer par vérification email
- `skip` (optionnel) : Pagination
- `limit` (optionnel) : Pagination (max: 500)

**Exemple** :
```bash
curl -X GET "http://localhost:8000/api/v1/admin/patients" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Codes de Statut HTTP

| Code | Signification | Cas d'utilisation |
|------|--------------|-------------------|
| 200 | OK | Opération réussie |
| 400 | Bad Request | Paramètres invalides (ex: rôle inconnu) |
| 401 | Unauthorized | Token manquant ou invalide |
| 403 | Forbidden | Non-admin ou tentative d'action interdite |
| 404 | Not Found | Utilisateur non trouvé |
| 500 | Internal Server Error | Erreur serveur |

---

## Sécurité

### Protections Implémentées

1. **Authentification requise** : Tous les endpoints nécessitent un token JWT valide
2. **Autorisation** : Seuls les admins peuvent accéder à ces endpoints
3. **Restrictions** :
   - Les admins ne peuvent pas être suspendus ou supprimés
   - Un admin ne peut pas se suspendre/supprimer lui-même
4. **Logging** : Toutes les actions sont loggées avec :
   - L'email de l'admin qui effectue l'action
   - L'utilisateur ciblé
   - La raison (pour les suspensions)
   - L'horodatage

### Logs d'Audit

Chaque action produit des logs détaillés :

```python
# Suspension
logger.info(f"User suspended: user_id={user_id}, email={user.email}, reason={reason}, suspended_by={current_admin.email}")

# Réactivation
logger.info(f"User reactivated: user_id={user_id}, email={user.email}, activated_by={current_admin.email}")

# Suppression
logger.info(f"User deleted: user_id={user_id}, email={user_email}, role={user_role}, deleted_by={current_admin.email}")
```

---

## Notifications Email

Toutes les actions qui modifient l'état d'un compte déclenchent un email :

| Action | Email envoyé |
|--------|--------------|
| Suspension | ✅ Oui - Notification avec raison |
| Réactivation | ✅ Oui - Confirmation + lien de connexion |
| Suppression | ✅ Oui - Confirmation de suppression |

---

## Exemples de Flux de Travail

### Flux 1 : Suspendre un utilisateur problématique

```bash
# 1. Lister les utilisateurs actifs
ADMIN_TOKEN="your_token"
curl -X GET "http://localhost:8000/api/v1/admin/users?is_active=true&role=doctor" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 2. Obtenir les détails du docteur #5
curl -X GET "http://localhost:8000/api/v1/admin/users/5" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. Suspendre le compte
curl -X POST "http://localhost:8000/api/v1/admin/users/5/suspend" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason":"Multiples plaintes de patients"}'

# 4. Vérifier la suspension
curl -X GET "http://localhost:8000/api/v1/admin/users?is_active=false" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Flux 2 : Gérer une demande de réactivation

```bash
# 1. Voir les comptes suspendus
curl -X GET "http://localhost:8000/api/v1/admin/users?is_active=false" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 2. Examiner le compte
curl -X GET "http://localhost:8000/api/v1/admin/users/5" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. Réactiver le compte
curl -X POST "http://localhost:8000/api/v1/admin/users/5/activate" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Flux 3 : Supprimer un compte frauduleux

```bash
# 1. Identifier le compte
curl -X GET "http://localhost:8000/api/v1/admin/users?role=doctor" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 2. Vérifier les détails
curl -X GET "http://localhost:8000/api/v1/admin/users/5" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. Supprimer le compte (DÉFINITIF)
curl -X DELETE "http://localhost:8000/api/v1/admin/users/5" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Tests

### Tests Réussis ✅

1. **Lister tous les utilisateurs** : ✅
2. **Filtrer par rôle (patient)** : ✅
3. **Filtrer par statut actif (false)** : ✅
4. **Suspendre un patient** : ✅
5. **Suspendre un médecin** : ✅
6. **Réactiver un compte** : ✅
7. **Supprimer un compte** : ✅
8. **Lister les patients** : ✅
9. **Obtenir les détails d'un utilisateur** : ✅

---

## Notes Importantes

### 1. GDPR et Conformité

Pour la conformité GDPR, considérez :
- **Soft Delete** : Marquer comme supprimé au lieu de supprimer réellement
- **Anonymisation** : Remplacer les données personnelles par des valeurs anonymes
- **Rétention des données** : Conserver certaines données pour audit légal

### 2. Récupération de Compte

Actuellement, il n'y a pas de mécanisme de récupération après suppression.  
Recommandations :
- Implémenter une période de grâce (ex: 30 jours) avant suppression définitive
- Permettre aux utilisateurs de demander la réactivation
- Créer un processus d'appel pour les suspensions

### 3. Notifications

Les emails sont envoyés de manière asynchrone. En cas d'échec :
- L'action est quand même effectuée
- L'erreur est loggée
- L'admin reçoit un message de confirmation

---

## Statistiques d'Utilisation

```bash
# Nombre total d'utilisateurs par rôle
GET /api/v1/admin/users?role=patient&limit=1  # Voir total dans la réponse
GET /api/v1/admin/users?role=doctor&limit=1

# Comptes suspendus
GET /api/v1/admin/users?is_active=false

# Médecins en attente d'approbation
GET /api/v1/admin/doctors/pending

# Comptes non vérifiés
GET /api/v1/admin/users?is_verified=false
```

---

## Support et Contact

Pour toute question ou problème :
1. Consultez les logs de l'application
2. Vérifiez la documentation API : `/docs`
3. Contactez l'équipe technique

---

**Version** : 1.0  
**Dernière mise à jour** : 5 novembre 2025  
**Auteur** : Équipe de développement Santé
