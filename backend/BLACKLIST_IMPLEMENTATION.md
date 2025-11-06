# Système de Blacklist d'Emails - Documentation d'Implémentation

## Vue d'ensemble

Un système complet de blacklist des emails a été implémenté pour empêcher les comptes supprimés ou suspendus de se réinscrire ou de se connecter. Le système inclut également des logs améliorés et structurés pour une meilleure traçabilité.

## Composants créés/modifiés

### 1. Nouveau Modèle : `EmailBlacklist`
**Fichier**: `app/models/blacklist.py`

```python
class BlacklistReason(str, Enum):
    DELETED = "deleted"      # Compte supprimé par admin
    SUSPENDED = "suspended"  # Compte suspendu
    BANNED = "banned"        # Banni pour violation
    FRAUD = "fraud"          # Activité frauduleuse
```

**Champs du modèle**:
- `email` (unique, indexed) - Email blacklisté
- `reason` (BlacklistReason enum) - Raison du blacklist
- `details` (Text, nullable) - Détails supplémentaires
- `original_user_id`, `original_user_name`, `original_user_role` - Info de l'utilisateur original
- `blacklisted_by_admin_id`, `blacklisted_by_admin_email` - Admin qui a ajouté à la blacklist
- `created_at` - Date de création
- `expires_at` (nullable) - Date d'expiration optionnelle

**Propriété calculée**: `is_expired` - Vérifie si l'entrée est expirée

### 2. Nouveau Service : `BlacklistService`
**Fichier**: `app/services/blacklist_service.py`

#### Méthodes principales:

**`add_to_blacklist(...)`**
- Ajoute un email à la blacklist
- Gère les entrées existantes (met à jour si déjà présent)
- Log l'action avec format structuré

**`is_blacklisted(email, db) -> tuple[bool, Optional[EmailBlacklist]]`**
- Vérifie si un email est blacklisté
- Retourne (True, entry) si blacklisté, (False, None) sinon
- Vérifie automatiquement l'expiration

**`remove_from_blacklist(email, db)`**
- Retire un email de la blacklist
- Utilisé lors de la réactivation d'un compte

**`get_blacklist_message(entry) -> str`**
- Génère un message utilisateur approprié selon la raison
- Messages personnalisés pour DELETED, SUSPENDED, BANNED, FRAUD

### 3. Migration Base de Données
**Fichier**: `alembic/versions/d6e8f9g0a2b3_add_email_blacklist_table.py`

Crée:
- Type ENUM `blacklistreason` avec valeurs: deleted, suspended, banned, fraud
- Table `email_blacklist` avec tous les champs
- Index sur `email` pour performance

**État**: Migration créée, à appliquer avec `alembic upgrade head`

### 4. Modifications des Endpoints d'Authentification
**Fichier**: `app/api/v1/endpoints/auth.py`

#### Inscription Patient (`/register/patient`)
```python
# Vérifie la blacklist AVANT création du compte
is_blacklisted, blacklist_entry = blacklist_service.is_blacklisted(email, db)
if is_blacklisted:
    raise HTTPException(
        status_code=403,
        detail=blacklist_service.get_blacklist_message(blacklist_entry)
    )
```

**Logs améliorés**:
```
[PATIENT REGISTRATION] Attempt started | email=... | ip=... | name=...
[PATIENT REGISTRATION] Blacklisted email attempt | email=... | reason=... | ip=...
[PATIENT REGISTRATION] Success | user_id=... | email=... | ip=...
```

#### Inscription Médecin (`/register/practitioner`)
- Même vérification de blacklist que pour les patients
- Format de logs similaire avec préfixe `[DOCTOR REGISTRATION]`

#### Connexion (`/login`)
- Vérifie la blacklist AVANT l'authentification
- Retourne message spécifique si email blacklisté
- Log l'attempt avec raison

**Logs améliorés**:
```
[LOGIN] Attempt started | email=... | ip=... | user_agent=...
[LOGIN] Blacklisted email attempt | email=... | reason=... | ip=...
[LOGIN] Rate limited | email=... | ip=...
[LOGIN] Success | user_id=... | email=... | role=... | ip=...
```

### 5. Modifications des Endpoints Admin
**Fichier**: `app/api/v1/endpoints/admin.py`

#### Suspension d'utilisateur (`POST /admin/users/{id}/suspend`)
```python
# Ajoute l'email à la blacklist avec raison SUSPENDED
blacklist_service.add_to_blacklist(
    email=user.email,
    reason=BlacklistReason.SUSPENDED,
    details=suspend_data.reason,
    original_user_id=user.id,
    original_user_name=f"{user.first_name} {user.last_name}",
    original_user_role=user.role.value,
    admin_id=current_admin.id,
    admin_email=current_admin.email,
    db=db
)
```

**Logs améliorés**:
```
[ADMIN ACTION] User suspended | user_id=... | email=... | role=... | reason=... | admin_email=...
```

#### Réactivation d'utilisateur (`POST /admin/users/{id}/activate`)
```python
# Retire l'email de la blacklist
blacklist_service.remove_from_blacklist(user.email, db)
```

**Logs améliorés**:
```
[ADMIN ACTION] User reactivated | user_id=... | email=... | role=... | admin_email=...
```

#### Suppression d'utilisateur (`DELETE /admin/users/{id}`)
```python
# Ajoute l'email à la blacklist AVANT de supprimer l'utilisateur
blacklist_service.add_to_blacklist(
    email=user.email,
    reason=BlacklistReason.DELETED,
    details="Account permanently deleted by admin",
    ...
)
```

**Logs améliorés**:
```
[ADMIN ACTION] User deleted | user_id=... | email=... | role=... | admin_email=...
```

## Format des Logs Structurés

Tous les logs suivent maintenant un format cohérent:
```
[ACTION] Message | key1=value1 | key2=value2 | key3=value3
```

**Avantages**:
- Plus facile à parser pour les outils de monitoring
- Recherche rapide par action spécifique
- Contexte complet en une ligne
- Traçabilité améliorée pour audit et debugging

## Messages Utilisateur par Raison de Blacklist

### DELETED
```
Ce compte a été définitivement supprimé. Veuillez contacter l'administrateur si vous pensez qu'il s'agit d'une erreur.
```

### SUSPENDED
```
Ce compte est actuellement suspendu. Raison: [details]. Veuillez contacter l'administrateur pour plus d'informations.
```

### BANNED
```
Cet email a été banni de la plateforme. Pour toute question, contactez notre support.
```

### FRAUD
```
Ce compte a été signalé pour activité frauduleuse et ne peut pas être utilisé.
```

## Workflow Complet

### Scénario 1: Suspension d'un compte
1. Admin suspend le compte via `POST /admin/users/{id}/suspend`
2. Email ajouté à la blacklist avec `reason=SUSPENDED`
3. User tente de se connecter
4. Blacklist vérifié avant authentification
5. HTTP 403 avec message "Ce compte est actuellement suspendu..."

### Scénario 2: Suppression d'un compte
1. Admin supprime le compte via `DELETE /admin/users/{id}`
2. Email ajouté à la blacklist avec `reason=DELETED`
3. Tokens et utilisateur supprimés de la DB
4. User tente de créer un nouveau compte
5. Blacklist vérifié avant création
6. HTTP 403 avec message "Ce compte a été définitivement supprimé..."

### Scénario 3: Réactivation
1. Admin réactive via `POST /admin/users/{id}/activate`
2. Email RETIRÉ de la blacklist
3. User peut maintenant se connecter normalement

## Tests à Effectuer

### Test 1: Blacklist lors de l'inscription
```bash
# 1. Créer un compte patient
curl -X POST http://localhost:8000/api/v1/auth/register/patient \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", ...}'

# 2. Admin suspend le compte
curl -X POST http://localhost:8000/api/v1/admin/users/1/suspend \
  -H "Authorization: Bearer <admin_token>" \
  -d '{"reason": "Test suspension"}'

# 3. Tenter de créer un nouveau compte avec le même email
# Devrait retourner HTTP 403 avec message de suspension
curl -X POST http://localhost:8000/api/v1/auth/register/patient \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", ...}'
```

### Test 2: Blacklist lors de la connexion
```bash
# 1. Supprimer le compte
curl -X DELETE http://localhost:8000/api/v1/admin/users/1 \
  -H "Authorization: Bearer <admin_token>"

# 2. Tenter de se connecter
# Devrait retourner HTTP 403 avec message de suppression
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "..."}'
```

### Test 3: Réactivation
```bash
# 1. Réactiver le compte suspendu
curl -X POST http://localhost:8000/api/v1/admin/users/1/activate \
  -H "Authorization: Bearer <admin_token>"

# 2. Tenter de se connecter
# Devrait fonctionner normalement
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "..."}'
```

## Commandes de Déploiement

### 1. Appliquer la migration
```bash
cd /home/alpha/fastapi-frontend/backend
docker compose exec backend alembic upgrade head
```

### 2. Vérifier la table créée
```bash
docker compose exec postgres psql -U fastapi_user -d fastapi_db -c "\d email_blacklist"
```

### 3. Redémarrer les services
```bash
docker compose restart backend
```

## Endpoints Admin à Ajouter (Optionnel)

Pour une gestion complète de la blacklist:

### `GET /admin/blacklist` - Liste des emails blacklistés
### `DELETE /admin/blacklist/{email}` - Retirer manuellement un email
### `GET /admin/blacklist/{email}` - Détails d'une entrée

## Sécurité et Considérations

### RGPD
- Les informations de l'utilisateur original sont conservées dans la blacklist
- Considérer un système d'expiration automatique après X jours/mois
- Permettre aux utilisateurs de demander la suppression de leurs données

### Performance
- Index sur la colonne `email` pour recherche rapide
- Vérification de blacklist se fait AVANT les opérations coûteuses (hashage password, etc.)

### Audit
- Tous les ajouts/suppressions de blacklist sont loggés
- Informations sur l'admin qui a effectué l'action
- Horodatage précis de toutes les opérations

## Améliorations Futures

1. **Dashboard Admin** - Interface visuelle pour gérer la blacklist
2. **Alertes automatiques** - Notifier les admins lors de tentatives répétées d'accès blacklisté
3. **Expiration automatique** - Système de nettoyage des entrées expirées
4. **Raisons personnalisées** - Permettre aux admins d'ajouter des notes détaillées
5. **Historique** - Garder un historique des modifications de statut de blacklist
6. **API de vérification** - Endpoint pour vérifier si un email est blacklisté (pour intégrations externes)

## État Actuel

✅ Modèle `EmailBlacklist` créé
✅ Service `BlacklistService` créé avec toutes les méthodes
✅ Migration créée
✅ Vérification de blacklist ajoutée à l'inscription patient
✅ Vérification de blacklist ajoutée à l'inscription médecin
✅ Vérification de blacklist ajoutée à la connexion
✅ Ajout à blacklist lors de la suspension
✅ Retrait de blacklist lors de la réactivation
✅ Ajout à blacklist lors de la suppression
✅ Logs structurés améliorés partout

⏳ Migration à appliquer (nécessite Docker en cours d'exécution)
⏳ Tests end-to-end à effectuer

## Notes d'Implémentation

- Le service blacklist utilise un pattern singleton avec `get_blacklist_service()`
- Les vérifications de blacklist retournent HTTP 403 (Forbidden) pas 401 (Unauthorized)
- Les messages d'erreur sont en français pour correspondre au reste de l'application
- Les logs incluent toujours l'IP du client pour traçabilité
- La blacklist est vérifiée en premier dans le flow d'auth pour éviter les opérations inutiles
