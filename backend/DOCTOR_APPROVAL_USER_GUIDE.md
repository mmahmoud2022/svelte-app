# Guide d'Utilisation - Système de Validation des Médecins

## Pour les Médecins

### 1. Inscription
Rendez-vous sur la page d'inscription médecin et remplissez le formulaire :
- Email
- Mot de passe (minimum 8 caractères, avec majuscule, minuscule et chiffre)
- Nom et prénom
- Téléphone
- Genre
- Spécialisation
- Tarif de consultation (optionnel)
- Langues parlées (optionnel)
- Biographie (optionnel)

### 2. Vérification de l'Email
Après l'inscription, vous recevrez un email contenant :
- Un lien de vérification valable 24h
- Une note vous informant qu'une validation admin est requise

**Important** : Cliquez sur le lien pour vérifier votre email.

### 3. Validation Admin
Une fois votre email vérifié, votre profil sera examiné par notre équipe.
- Vous ne pouvez pas encore vous connecter
- Vous recevrez un email lorsque votre compte sera approuvé
- Ce processus peut prendre de quelques heures à quelques jours

### 4. Tentative de Connexion Prématurée
Si vous essayez de vous connecter avant l'approbation, vous verrez le message :
> "Votre compte médecin est en attente de validation par un administrateur. Vous recevrez un email une fois votre compte approuvé."

### 5. Approbation
Une fois approuvé, vous recevrez un email de confirmation avec :
- La confirmation de l'approbation
- Un lien pour vous connecter

Vous pouvez maintenant utiliser la plateforme normalement !

### 6. En Cas de Rejet
Si votre compte est rejeté, vous recevrez un email vous informant de la décision. Contactez le support pour plus d'informations.

---

## Pour les Administrateurs

### 1. Connexion Admin
Connectez-vous avec vos identifiants administrateur.

### 2. Voir les Médecins en Attente

**Endpoint** : `GET /api/v1/admin/doctors/pending`

**Headers** :
```
Authorization: Bearer {votre_token_admin}
```

**Réponse** :
```json
[
  {
    "id": 6,
    "email": "dr.sophie@example.com",
    "first_name": "Sophie",
    "last_name": "Bernard",
    "role": "doctor",
    "specialization": "Pédiatrie",
    "admin_approved": false,
    "is_verified": true
  }
]
```

### 3. Examiner le Profil du Médecin
Examinez les informations du médecin :
- Nom et prénom
- Email
- Spécialisation
- Biographie
- Tarif de consultation
- Langues parlées

### 4. Approuver un Médecin

**Endpoint** : `POST /api/v1/admin/doctors/{doctor_id}/approve`

**Headers** :
```
Authorization: Bearer {votre_token_admin}
```

**Exemple avec cURL** :
```bash
curl -X POST "http://localhost:8000/api/v1/admin/doctors/6/approve" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Réponse** :
```json
{
  "message": "Le compte du Dr. Bernard a été approuvé avec succès",
  "success": true
}
```

**Actions automatiques** :
- ✅ `admin_approved` passe à `true`
- ✅ Email de confirmation envoyé au médecin
- ✅ Log de l'action créé

### 5. Rejeter un Médecin

**Endpoint** : `POST /api/v1/admin/doctors/{doctor_id}/reject`

**Headers** :
```
Authorization: Bearer {votre_token_admin}
```

**Exemple avec cURL** :
```bash
curl -X POST "http://localhost:8000/api/v1/admin/doctors/6/reject" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Réponse** :
```json
{
  "message": "Le compte du Dr. Bernard a été rejeté",
  "success": true
}
```

**Actions automatiques** :
- ✅ `is_active` passe à `false`
- ✅ `suspension_reason` définie
- ✅ Email de notification envoyé au médecin
- ✅ Log de l'action créé

### 6. Voir Tous les Médecins

**Endpoint** : `GET /api/v1/admin/doctors/all`

**Headers** :
```
Authorization: Bearer {votre_token_admin}
```

Retourne tous les médecins (approuvés, en attente, rejetés).

---

## Exemples d'Intégration Frontend

### React - Liste des Médecins en Attente

```javascript
import { useState, useEffect } from 'react';
import axios from 'axios';

function PendingDoctorsList() {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPendingDoctors();
  }, []);

  const fetchPendingDoctors = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await axios.get(
        'http://localhost:8000/api/v1/admin/doctors/pending',
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setDoctors(response.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const approveDoctor = async (doctorId) => {
    try {
      const token = localStorage.getItem('adminToken');
      await axios.post(
        `http://localhost:8000/api/v1/admin/doctors/${doctorId}/approve`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      alert('Médecin approuvé avec succès !');
      fetchPendingDoctors(); // Rafraîchir la liste
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors de l\'approbation');
    }
  };

  const rejectDoctor = async (doctorId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir rejeter ce médecin ?')) {
      return;
    }
    
    try {
      const token = localStorage.getItem('adminToken');
      await axios.post(
        `http://localhost:8000/api/v1/admin/doctors/${doctorId}/reject`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      alert('Médecin rejeté');
      fetchPendingDoctors(); // Rafraîchir la liste
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors du rejet');
    }
  };

  if (loading) return <div>Chargement...</div>;

  return (
    <div>
      <h2>Médecins en Attente d'Approbation</h2>
      {doctors.length === 0 ? (
        <p>Aucun médecin en attente</p>
      ) : (
        <ul>
          {doctors.map(doctor => (
            <li key={doctor.id}>
              <h3>Dr. {doctor.last_name} {doctor.first_name}</h3>
              <p>Email: {doctor.email}</p>
              <p>Spécialisation: {doctor.specialization}</p>
              <p>Téléphone: {doctor.phone}</p>
              <button onClick={() => approveDoctor(doctor.id)}>
                Approuver
              </button>
              <button onClick={() => rejectDoctor(doctor.id)}>
                Rejeter
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default PendingDoctorsList;
```

### Vue.js - Composant d'Approbation

```vue
<template>
  <div class="pending-doctors">
    <h2>Médecins en Attente</h2>
    
    <div v-if="loading" class="loading">
      Chargement...
    </div>
    
    <div v-else-if="doctors.length === 0" class="empty">
      Aucun médecin en attente d'approbation
    </div>
    
    <div v-else class="doctors-list">
      <div 
        v-for="doctor in doctors" 
        :key="doctor.id" 
        class="doctor-card"
      >
        <h3>Dr. {{ doctor.last_name }} {{ doctor.first_name }}</h3>
        <p><strong>Email:</strong> {{ doctor.email }}</p>
        <p><strong>Spécialisation:</strong> {{ doctor.specialization }}</p>
        <p><strong>Téléphone:</strong> {{ doctor.phone }}</p>
        <p v-if="doctor.bio"><strong>Bio:</strong> {{ doctor.bio }}</p>
        
        <div class="actions">
          <button 
            @click="approveDoctor(doctor.id)" 
            class="btn-approve"
          >
            Approuver
          </button>
          <button 
            @click="rejectDoctor(doctor.id)" 
            class="btn-reject"
          >
            Rejeter
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const doctors = ref([]);
const loading = ref(true);

const fetchPendingDoctors = async () => {
  try {
    const token = localStorage.getItem('adminToken');
    const response = await axios.get(
      'http://localhost:8000/api/v1/admin/doctors/pending',
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    doctors.value = response.data;
  } catch (error) {
    console.error('Erreur:', error);
    alert('Erreur lors du chargement des médecins');
  } finally {
    loading.value = false;
  }
};

const approveDoctor = async (doctorId) => {
  try {
    const token = localStorage.getItem('adminToken');
    await axios.post(
      `http://localhost:8000/api/v1/admin/doctors/${doctorId}/approve`,
      {},
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    alert('Médecin approuvé avec succès !');
    fetchPendingDoctors();
  } catch (error) {
    console.error('Erreur:', error);
    alert('Erreur lors de l\'approbation');
  }
};

const rejectDoctor = async (doctorId) => {
  if (!confirm('Êtes-vous sûr de vouloir rejeter ce médecin ?')) {
    return;
  }
  
  try {
    const token = localStorage.getItem('adminToken');
    await axios.post(
      `http://localhost:8000/api/v1/admin/doctors/${doctorId}/reject`,
      {},
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    alert('Médecin rejeté');
    fetchPendingDoctors();
  } catch (error) {
    console.error('Erreur:', error);
    alert('Erreur lors du rejet');
  }
};

onMounted(() => {
  fetchPendingDoctors();
});
</script>

<style scoped>
.doctor-card {
  border: 1px solid #ddd;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
}

.actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}

.btn-approve {
  background-color: #4caf50;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-reject {
  background-color: #f44336;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
```

---

## Tests avec cURL

### 1. Créer un Admin
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/admin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "AdminPass123!",
    "first_name": "Admin",
    "last_name": "Principal",
    "phone": "+33600000000",
    "admin_secret": "ADMIN_SECRET_2025_CHANGE_IN_PRODUCTION"
  }'
```

### 2. Se Connecter en tant qu'Admin
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "AdminPass123!"
  }' | jq -r '.access_token' > admin_token.txt
```

### 3. Lister les Médecins en Attente
```bash
curl -X GET "http://localhost:8000/api/v1/admin/doctors/pending" \
  -H "Authorization: Bearer $(cat admin_token.txt)" | jq
```

### 4. Approuver un Médecin
```bash
curl -X POST "http://localhost:8000/api/v1/admin/doctors/6/approve" \
  -H "Authorization: Bearer $(cat admin_token.txt)" | jq
```

### 5. Rejeter un Médecin
```bash
curl -X POST "http://localhost:8000/api/v1/admin/doctors/6/reject" \
  -H "Authorization: Bearer $(cat admin_token.txt)" | jq
```

---

## FAQ

### Q : Que se passe-t-il si un médecin essaie de se connecter avant approbation ?
**R :** Il reçoit un message HTTP 403 avec l'explication : "Votre compte médecin est en attente de validation par un administrateur..."

### Q : Les patients sont-ils affectés par cette validation ?
**R :** Non, les patients peuvent s'inscrire et se connecter immédiatement (après vérification email).

### Q : Un médecin peut-il être approuvé sans vérifier son email ?
**R :** Oui, actuellement. Si vous voulez exiger la vérification email d'abord, modifiez la logique.

### Q : Que se passe-t-il si je rejette un médecin par erreur ?
**R :** Le compte est désactivé. Vous devrez manuellement réactiver le compte dans la base de données ou créer un endpoint de réactivation.

### Q : Les actions admin sont-elles loggées ?
**R :** Oui, toutes les approbations et rejets sont loggués avec l'email de l'admin qui a effectué l'action.

### Q : Combien d'admins peuvent approuver les médecins ?
**R :** Tous les utilisateurs avec le rôle ADMIN peuvent approuver ou rejeter des médecins.

---

## Support

Pour toute question ou problème :
1. Consultez les logs de l'application
2. Vérifiez la documentation API : `/docs`
3. Contactez l'équipe technique

---

**Version** : 1.0  
**Dernière mise à jour** : 5 novembre 2025
