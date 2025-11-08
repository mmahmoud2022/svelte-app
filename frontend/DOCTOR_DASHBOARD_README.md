# 🩺 Dashboard Doctor - Documentation

## Vue d'ensemble

Le dashboard doctor est une interface complète pour les médecins permettant de gérer leurs rendez-vous, profils, patients, et bien plus encore. Il utilise les 20 endpoints API REST du module Doctor backend.

## 📁 Structure des fichiers

```
frontend/src/
├── lib/
│   ├── api-doctor.ts          # API client pour le module doctor (20 endpoints)
│   └── api.ts                 # API client général
├── routes/
│   └── doctors/
│       ├── DoctorDashboard.svelte        # Dashboard principal
│       ├── DoctorProfileCreate.svelte    # Création de profil
│       ├── DoctorRegister.svelte         # Inscription médecin
│       └── DoctorAppointments.svelte     # Gestion des rendez-vous
└── App.svelte                 # Router principal
```

## 🎯 Fonctionnalités implémentées

### 1. **Dashboard Principal** (`/doctors/dashboard`)
- Vue d'ensemble avec statistiques clés:
  - Nombre total de rendez-vous
  - Total de patients
  - Note moyenne et avis
  - Revenus totaux et mensuels
- Rendez-vous à venir
- Performance du mois
- Barre de progression du profil

### 2. **Gestion du Profil** (`/doctors/profile/create`)
- Création du profil médecin
- Champs:
  - Spécialité (sélection parmi 10 spécialités)
  - Numéro de licence
  - Années d'expérience
  - Tarif de consultation
  - Formation et diplômes
  - Langues parlées
  - Biographie professionnelle

### 3. **Gestion des Rendez-vous** (Onglet Appointments)
- Liste complète des rendez-vous
- Filtrage par statut:
  - En attente
  - Confirmés
  - Terminés
  - Annulés
  - Absents
- Actions sur chaque rendez-vous:
  - Voir détails complets
  - Mettre à jour le statut
  - Ajouter notes, diagnostic, prescription
- Modal de détails avec toutes les informations
- Modal de mise à jour avec formulaire complet

### 4. **Navigation par onglets**
- Vue d'ensemble
- Rendez-vous
- Disponibilités (à venir)
- Patients (à venir)
- Avis (à venir)
- Messages (à venir)
- Paiements (à venir)
- Paramètres (à venir)

## 🔌 Endpoints API utilisés

Le dashboard utilise les endpoints suivants du backend:

### Profile Management
```typescript
POST   /api/v1/doctors/              # Créer profil
GET    /api/v1/doctors/me            # Obtenir profil actuel
PUT    /api/v1/doctors/me            # Mettre à jour profil
GET    /api/v1/doctors/{id}          # Obtenir profil par ID
```

### Appointments
```typescript
GET    /api/v1/doctors/appointments                    # Liste rendez-vous
GET    /api/v1/doctors/appointments/{id}              # Détails rendez-vous
PATCH  /api/v1/doctors/appointments/{id}/status       # Mettre à jour statut
POST   /api/v1/doctors/appointments                   # Créer rendez-vous
GET    /api/v1/doctors/patients/{id}/appointments     # Rendez-vous patient
```

### Statistics
```typescript
GET    /api/v1/doctors/me/statistics  # Statistiques du médecin
```

### Availability (à implémenter)
```typescript
POST   /api/v1/doctors/availability                # Créer disponibilité
GET    /api/v1/doctors/availability                # Mes disponibilités
GET    /api/v1/doctors/{id}/availability           # Disponibilités par ID
DELETE /api/v1/doctors/availability/{id}           # Supprimer disponibilité
```

### Reviews (à implémenter)
```typescript
GET    /api/v1/doctors/{id}/reviews   # Obtenir avis
POST   /api/v1/doctors/reviews         # Créer avis
```

### Messages (à implémenter)
```typescript
GET    /api/v1/doctors/messages        # Obtenir messages
POST   /api/v1/doctors/messages        # Envoyer message
```

### Payments (à implémenter)
```typescript
GET    /api/v1/doctors/payments        # Historique paiements
```

### Documents (à implémenter)
```typescript
GET    /api/v1/doctors/documents/{id}  # Obtenir document
```

## 🎨 Types TypeScript

Tous les types sont définis dans `api-doctor.ts`:

```typescript
// Enums
type Specialty = 'general_practitioner' | 'cardiologist' | 'dermatologist' | ...
type ConsultationType = 'in_person' | 'teleconsultation' | 'home_visit' | 'emergency'
type AppointmentStatus = 'pending' | 'confirmed' | 'cancelled' | 'completed' | 'no_show'
type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded'

// Interfaces
interface DoctorProfile { ... }
interface Appointment { ... }
interface DoctorStatistics { ... }
interface DoctorAvailability { ... }
interface DoctorReview { ... }
interface DoctorMessage { ... }
interface Payment { ... }
interface PatientDocument { ... }
```

## 🚀 Routes frontend

Ajoutées dans `App.svelte`:

```typescript
'/doctors/dashboard'           → DoctorDashboard
'/doctors/profile/create'      → DoctorProfileCreate
'/register/doctor'             → DoctorRegister
```

## 🔐 Sécurité

- Authentification JWT requise
- Vérification du rôle `DOCTOR` au chargement
- Redirection automatique si non autorisé
- Token refresh automatique via intercepteur Axios

## 🎯 Prochaines étapes

### Fonctionnalités à implémenter:

1. **Disponibilités**
   - Composant de gestion des créneaux
   - Calendrier interactif
   - CRUD complet des disponibilités

2. **Patients**
   - Liste des patients
   - Historique médical
   - Documents partagés

3. **Avis et évaluations**
   - Affichage des avis patients
   - Statistiques de satisfaction
   - Réponses aux avis

4. **Messagerie**
   - Chat en temps réel avec patients
   - Notifications de nouveaux messages
   - Historique des conversations

5. **Paiements**
   - Historique détaillé
   - Graphiques de revenus
   - Export des données

6. **Paramètres**
   - Notifications (email, SMS)
   - Préférences de rendez-vous
   - Configuration du compte

## 💡 Exemples d'utilisation

### Créer un profil doctor

```typescript
import { createDoctorProfile } from '../../lib/api-doctor';

const profile = await createDoctorProfile({
  specialty: 'cardiologist',
  license_number: '12345',
  consultation_fee: 5000, // 50€ en centimes
  bio: 'Cardiologue expérimenté...',
  years_of_experience: 15,
  education: 'Doctorat en médecine, CHU Paris',
  languages_spoken: 'Français, Anglais, Arabe'
});
```

### Obtenir les statistiques

```typescript
import { getDoctorStatistics } from '../../lib/api-doctor';

const stats = await getDoctorStatistics();
console.log(stats.total_appointments);
console.log(stats.average_rating);
console.log(stats.total_revenue);
```

### Mettre à jour un rendez-vous

```typescript
import { updateAppointmentStatus } from '../../lib/api-doctor';

await updateAppointmentStatus(appointmentId, {
  status: 'completed',
  notes: 'Consultation terminée',
  diagnosis: 'Hypertension artérielle',
  prescription: 'Amlodipine 5mg, 1x/jour'
});
```

## 🐛 Gestion d'erreurs

Toutes les fonctions API gèrent les erreurs:

```typescript
try {
  const profile = await getCurrentDoctorProfile();
} catch (err) {
  if (err.response?.status === 404) {
    // Profil non trouvé, rediriger vers création
    navigate('/doctors/profile/create');
  } else {
    // Autre erreur
    console.error('Erreur:', err);
  }
}
```

## 📱 Responsive Design

- Design adaptatif mobile-first
- Grille responsive avec Tailwind CSS
- Navigation par onglets scrollable sur mobile
- Modals optimisés pour petits écrans

## 🎨 Design System

### Couleurs principales
- Emerald: `#10b981` - Actions principales
- Teal: `#14b8a6` - Accents
- Blue: `#3b82f6` - Informations
- Yellow: `#f59e0b` - Avertissements
- Red: `#ef4444` - Erreurs
- Green: `#22c55e` - Succès

### Badges de statut
- Pending: Jaune
- Confirmed: Bleu
- Completed: Vert
- Cancelled: Rouge
- No Show: Gris

## 📊 Statistiques affichées

- **Total appointments**: Nombre total de rendez-vous
- **Total patients**: Nombre de patients uniques
- **Average rating**: Note moyenne sur 5
- **Total reviews**: Nombre d'avis reçus
- **Total revenue**: Revenu total en €
- **Revenue this month**: Revenu du mois en cours
- **Appointments this month**: Rendez-vous ce mois
- **Completed/Cancelled**: Compteurs par statut

## 🔄 Refresh automatique

Les données sont rechargées:
- Au chargement de la page
- Après mise à jour d'un rendez-vous
- Après changement de filtre
- Après création/modification de profil

## 🌐 Internationalisation

Toutes les chaînes sont en français:
- Labels de formulaires
- Messages d'erreur
- Badges de statut
- Navigation
- Tooltips

## 📝 Notes techniques

1. **State Management**: Utilise les stores Svelte natifs
2. **API Client**: Axios avec intercepteurs pour auth
3. **Routing**: Client-side routing avec history API
4. **Styling**: Tailwind CSS
5. **Icons**: Heroicons (SVG inline)
6. **Date Formatting**: Intl.DateTimeFormat (fr-FR)
7. **Currency Formatting**: Intl.NumberFormat (€)

---

**Statut**: ✅ Dashboard de base opérationnel
**Version**: 1.0.0
**Dernière mise à jour**: 6 novembre 2025
