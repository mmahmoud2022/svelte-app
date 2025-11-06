# Implémentation de la Validation Admin pour les Médecins

## Date : 5 novembre 2025

## Résumé des Changements

L'authentification des médecins a été modifiée pour nécessiter une validation par un administrateur avant de pouvoir se connecter à la plateforme.

## Modifications Apportées

### 1. Modèle de Données (`app/models/user.py`)
- ✅ Ajout du champ `admin_approved` (Boolean) au modèle User
- Les patients et admins ont `admin_approved = True` par défaut
- Les médecins ont `admin_approved = False` par défaut

### 2. Migration de Base de Données
- ✅ Création de la migration `c5d7e8f9a1b2_add_admin_approved_field_to_users.py`
- ✅ Ajout de la colonne `admin_approved` à la table `users`
- ✅ Mise à jour automatique des utilisateurs existants (patients et admins approuvés)

### 3. Service d'Authentification (`app/services/auth_service.py`)
- ✅ Modification de `authenticate_user()` pour vérifier `admin_approved` pour les médecins
- Les médecins non approuvés ne peuvent pas s'authentifier

### 4. Endpoints d'Authentification (`app/api/v1/endpoints/auth.py`)

#### Inscription Patient
- ✅ `admin_approved = True` automatiquement

#### Inscription Admin
- ✅ `admin_approved = True` automatiquement

#### Inscription Médecin
- ✅ `admin_approved = False` par défaut
- ✅ Email de vérification mis à jour avec message d'attente de validation admin

#### Connexion
- ✅ Vérification préalable du statut `admin_approved` pour les médecins
- ✅ Message d'erreur spécifique (HTTP 403) : "Votre compte médecin est en attente de validation par un administrateur. Vous recevrez un email une fois votre compte approuvé."

### 5. Nouveaux Endpoints Admin (`app/api/v1/endpoints/admin.py`)

#### GET `/api/v1/admin/doctors/pending`
- Liste tous les médecins en attente d'approbation
- Nécessite le rôle ADMIN

#### POST `/api/v1/admin/doctors/{doctor_id}/approve`
- Approuve un médecin
- Envoie un email de confirmation au médecin
- Nécessite le rôle ADMIN

#### POST `/api/v1/admin/doctors/{doctor_id}/reject`
- Rejette un médecin
- Désactive le compte du médecin
- Envoie un email de notification
- Nécessite le rôle ADMIN

#### GET `/api/v1/admin/doctors/all`
- Liste tous les médecins (approuvés et en attente)
- Nécessite le rôle ADMIN

### 6. Schémas (`app/schemas/auth.py`)
- ✅ Ajout du champ `admin_approved` à `UserResponse`

## Flux de Travail

### Pour un Médecin :
1. **Inscription** : Le médecin s'inscrit via `/api/v1/auth/register/doctor`
   - Reçoit un email de vérification
   - L'email indique qu'une validation admin est requise

2. **Vérification Email** : Le médecin clique sur le lien de vérification
   - `is_verified` passe à `True`
   - `admin_approved` reste à `False`

3. **Tentative de Connexion** : Le médecin essaie de se connecter
   - Reçoit le message : "Votre compte médecin est en attente de validation par un administrateur..."
   - HTTP 403 Forbidden

4. **Approbation Admin** : Un administrateur approuve le compte
   - `admin_approved` passe à `True`
   - Le médecin reçoit un email de confirmation

5. **Connexion Réussie** : Le médecin peut maintenant se connecter normalement

### Pour un Administrateur :
1. Consulter les médecins en attente : `GET /api/v1/admin/doctors/pending`
2. Examiner le profil du médecin
3. Approuver : `POST /api/v1/admin/doctors/{doctor_id}/approve`
   - OU -
   Rejeter : `POST /api/v1/admin/doctors/{doctor_id}/reject`

## Messages Utilisateur

### Email d'Inscription Médecin
```
Bienvenue sur Santé !

Bonjour Dr. [NOM],

Merci de vous être inscrit en tant que praticien. Pour activer votre compte, 
veuillez cliquer sur le lien ci-dessous :

[Vérifier mon email]

Ce lien est valable pendant 24 heures.

Note importante : Après la vérification de votre email, votre profil devra 
être validé par un administrateur avant que vous puissiez vous connecter. 
Vous recevrez un email de confirmation une fois votre compte approuvé.

Cette étape de validation nous permet de garantir la qualité et la sécurité 
de notre plateforme.
```

### Email d'Approbation
```
Félicitations !

Bonjour Dr. [NOM],

Nous avons le plaisir de vous informer que votre compte médecin a été 
approuvé par notre équipe.

Vous pouvez maintenant vous connecter à votre compte et commencer à 
utiliser notre plateforme.

[Se connecter]

Bienvenue sur Santé !
```

### Message de Connexion Refusée
```json
{
  "detail": "Votre compte médecin est en attente de validation par un administrateur. Vous recevrez un email une fois votre compte approuvé."
}
```

## Sécurité

- ✅ Vérification du rôle admin pour tous les endpoints admin
- ✅ Logging de toutes les tentatives de connexion
- ✅ Logging de toutes les actions admin (approbation/rejet)
- ✅ Les médecins non approuvés ne peuvent pas s'authentifier
- ✅ Les patients et admins ne sont pas affectés par cette validation

## Tests Recommandés

1. **Test Inscription Médecin**
   - Vérifier que `admin_approved = False` après inscription
   - Vérifier que l'email contient le bon message

2. **Test Connexion Médecin Non Approuvé**
   - Vérifier le code HTTP 403
   - Vérifier le message d'erreur

3. **Test Approbation Admin**
   - Vérifier que `admin_approved` passe à `True`
   - Vérifier l'envoi de l'email

4. **Test Connexion Médecin Approuvé**
   - Vérifier la connexion réussie

5. **Test Endpoints Admin**
   - Vérifier l'accès réservé aux admins
   - Vérifier la liste des médecins en attente
   - Vérifier l'approbation et le rejet

## Commandes Utiles

```bash
# Appliquer la migration
alembic upgrade head

# Créer un admin (si nécessaire)
curl -X POST "http://localhost:8000/api/v1/auth/register/admin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "AdminPass123!",
    "first_name": "Admin",
    "last_name": "User",
    "phone": "+33123456789",
    "admin_secret": "your_admin_secret"
  }'

# Lister les médecins en attente (nécessite token admin)
curl -X GET "http://localhost:8000/api/v1/admin/doctors/pending" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Approuver un médecin
curl -X POST "http://localhost:8000/api/v1/admin/doctors/1/approve" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Notes Importantes

- Les utilisateurs existants de type PATIENT et ADMIN ont été automatiquement approuvés lors de la migration
- Les médecins existants (s'il y en a) ont `admin_approved = False` et doivent être approuvés manuellement
- Cette fonctionnalité n'affecte que les médecins, pas les patients ni les admins

## Prochaines Étapes Possibles

1. Interface admin dans le frontend pour gérer les approbations
2. Notifications en temps réel pour les admins lors de nouvelles inscriptions de médecins
3. Système de commentaires pour les rejets (raison du rejet)
4. Dashboard admin avec statistiques sur les approbations
