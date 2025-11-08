<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from '../../lib/router';
  import { 
    getCurrentDoctorProfile,
    getDoctorStatistics, 
    getDoctorAppointments,
    type DoctorProfile,
    type DoctorStatistics,
    type Appointment
  } from '../../lib/api-doctor';
  import { getCurrentUser } from '../../lib/api';
  import DoctorAppointments from './DoctorAppointments.svelte';
  import DoctorAvailability from './DoctorAvailability.svelte';
  import DoctorPatients from './DoctorPatients.svelte';
  import DoctorReviews from './DoctorReviews.svelte';
  import DoctorMessages from './DoctorMessages.svelte';
  import DoctorPayments from './DoctorPayments.svelte';
  import DoctorSettings from './DoctorSettings.svelte';
  
  let profile: DoctorProfile | null = null;
  let statistics: DoctorStatistics | null = null;
  let upcomingAppointments: Appointment[] = [];
  let loading = true;
  let activeTab: 'overview' | 'appointments' | 'availability' | 'patients' | 'reviews' | 'messages' | 'payments' | 'settings' = 'overview';

  onMount(async () => {
    try {
      const user = await getCurrentUser();
      if (user.role !== 'doctor' && user.role !== 'DOCTOR') {
        navigate('/');
        return;
      }

      await loadDashboardData();
    } catch (err: any) {
      console.error('Error loading dashboard:', err);
      // Dashboard is accessible even if some data fails to load
    } finally {
      loading = false;
    }
  });

  const loadDashboardData = async () => {
    // Try to load profile (optional, don't block dashboard access)
    try {
      profile = await getCurrentDoctorProfile();
    } catch (err: any) {
      console.warn('Profile not loaded, user can complete it later:', err);
      // Profile is optional, user can complete it later via Settings
    }

    // Load statistics (optional, don't fail if error)
    try {
      statistics = await getDoctorStatistics();
    } catch (err: any) {
      console.error('Error loading statistics:', err);
      // Continue without statistics
    }

    // Load appointments (optional, don't fail if error)
    try {
      const appointmentsData = await getDoctorAppointments(1, 5, 'pending');
      upcomingAppointments = appointmentsData.items || [];
    } catch (err: any) {
      console.error('Error loading appointments:', err);
      // Continue without appointments
    }
  };

  const handleProfileUpdated = async () => {
    // Reload profile data when updated from Settings
    console.log('Profile updated, reloading dashboard data...');
    await loadDashboardData();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount / 100);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'pending': return 'badge-warning';
      case 'confirmed': return 'badge-info';
      case 'completed': return 'badge-success';
      case 'cancelled': return 'badge-error';
      case 'no_show': return 'badge-secondary';
      default: return 'badge-neutral';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending': return 'En attente';
      case 'confirmed': return 'Confirmé';
      case 'completed': return 'Terminé';
      case 'cancelled': return 'Annulé';
      case 'no_show': return 'Absent';
      default: return status;
    }
  };
</script>

<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <header class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Dashboard Médecin</h1>
            {#if profile}
              <p class="text-sm text-gray-600">Dr. {profile.user?.full_name}</p>
            {/if}
          </div>
        </div>
        <button 
          on:click={() => navigate('/')}
          class="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium transition-colors"
        >
          Déconnexion
        </button>
      </div>
    </div>
  </header>

  {#if loading}
    <div class="flex items-center justify-center h-96">
      <div class="text-center">
        <svg class="animate-spin h-12 w-12 text-emerald-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-600">Chargement du dashboard...</p>
      </div>
    </div>
  {:else}
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Profile completion reminder (non-blocking) -->
      {#if !profile}
        <div class="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div class="flex items-start gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="flex-1">
              <p class="text-sm text-blue-800">
                <span class="font-medium">Conseil :</span> Complétez votre profil professionnel pour améliorer votre visibilité auprès des patients.
                <button 
                  on:click={() => activeTab = 'settings'}
                  class="ml-2 text-blue-700 hover:text-blue-900 underline font-medium"
                >
                  Aller aux paramètres
                </button>
              </p>
            </div>
            <button 
              on:click={() => {/* Dismiss banner - could add localStorage to remember */}}
              class="text-blue-400 hover:text-blue-600"
              aria-label="Fermer le message"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      {/if}

      <!-- Statistics Cards -->
      {#if statistics}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <!-- Total Appointments -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-gray-600">Rendez-vous totaux</h3>
              <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <p class="text-3xl font-bold text-gray-900">{statistics.total_appointments}</p>
            <p class="text-sm text-gray-500 mt-1">Ce mois: {statistics.appointments_this_month}</p>
          </div>

          <!-- Total Patients -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-gray-600">Patients</h3>
              <div class="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
            <p class="text-3xl font-bold text-gray-900">{statistics.total_patients}</p>
            <p class="text-sm text-gray-500 mt-1">Total unique</p>
          </div>

          <!-- Rating -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-gray-600">Note moyenne</h3>
              <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                </svg>
              </div>
            </div>
            <p class="text-3xl font-bold text-gray-900">{statistics.average_rating.toFixed(1)}</p>
            <p class="text-sm text-gray-500 mt-1">{statistics.total_reviews} avis</p>
          </div>

          <!-- Revenue -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-sm font-medium text-gray-600">Revenus</h3>
              <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <p class="text-3xl font-bold text-gray-900">{formatCurrency(statistics.total_revenue)}</p>
            <p class="text-sm text-gray-500 mt-1">Ce mois: {formatCurrency(statistics.revenue_this_month)}</p>
          </div>
        </div>
      {/if}

      <!-- Navigation Tabs -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px overflow-x-auto">
            <button
              on:click={() => activeTab = 'overview'}
              class="px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap {activeTab === 'overview' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
            >
              Vue d'ensemble
            </button>
            <button
              on:click={() => activeTab = 'appointments'}
              class="px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap {activeTab === 'appointments' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
            >
              Rendez-vous
            </button>
            <button
              on:click={() => activeTab = 'availability'}
              class="px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap {activeTab === 'availability' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
            >
              Disponibilités
            </button>
            <button
              on:click={() => activeTab = 'patients'}
              class="px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap {activeTab === 'patients' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
            >
              Patients
            </button>
            <button
              on:click={() => activeTab = 'reviews'}
              class="px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap {activeTab === 'reviews' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
            >
              Avis
            </button>
            <button
              on:click={() => activeTab = 'messages'}
              class="px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap {activeTab === 'messages' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
            >
              Messages
            </button>
            <button
              on:click={() => activeTab = 'payments'}
              class="px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap {activeTab === 'payments' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
            >
              Paiements
            </button>
            <button
              on:click={() => activeTab = 'settings'}
              class="px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap {activeTab === 'settings' ? 'border-emerald-500 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
            >
              Paramètres
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="p-6">
          {#if activeTab === 'overview'}
            <!-- Overview Tab -->
            <div class="space-y-6">
              <div>
                <h2 class="text-lg font-semibold text-gray-900 mb-4">Rendez-vous à venir</h2>
                {#if upcomingAppointments.length > 0}
                  <div class="space-y-3">
                    {#each upcomingAppointments as appointment}
                      <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <div class="flex items-center justify-between">
                          <div class="flex-1">
                            <div class="flex items-center gap-3 mb-2">
                              <h3 class="font-medium text-gray-900">
                                {appointment.patient?.full_name || 'Patient inconnu'}
                              </h3>
                              <span class="badge {getStatusBadgeClass(appointment.status)}">
                                {getStatusLabel(appointment.status)}
                              </span>
                            </div>
                            <p class="text-sm text-gray-600">
                              📅 {formatDate(appointment.appointment_date)}
                            </p>
                            {#if appointment.reason}
                              <p class="text-sm text-gray-500 mt-1">Motif: {appointment.reason}</p>
                            {/if}
                          </div>
                          <button
                            on:click={() => navigate(`/doctors/appointments/${appointment.id}`)}
                            class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                          >
                            Voir détails
                          </button>
                        </div>
                      </div>
                    {/each}
                  </div>
                {:else}
                  <p class="text-gray-500 text-center py-8">Aucun rendez-vous à venir</p>
                {/if}
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-lg p-6 border border-emerald-200">
                  <h3 class="font-semibold text-gray-900 mb-2">Profil complété</h3>
                  <div class="flex items-center gap-4">
                    <div class="flex-1">
                      <div class="bg-white rounded-full h-3 overflow-hidden">
                        <div class="bg-gradient-to-r from-emerald-500 to-teal-600 h-full" style="width: {profile ? '85' : '20'}%"></div>
                      </div>
                    </div>
                    <span class="text-2xl font-bold text-emerald-600">{profile ? '85' : '20'}%</span>
                  </div>
                  <p class="text-sm text-gray-600 mt-3">Complétez votre profil pour attirer plus de patients</p>
                </div>

                <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
                  <h3 class="font-semibold text-gray-900 mb-2">Performance ce mois</h3>
                  {#if statistics}
                    <div class="space-y-2">
                      <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">Confirmés:</span>
                        <span class="font-semibold text-gray-900">{statistics.completed_appointments}</span>
                      </div>
                      <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">Annulés:</span>
                        <span class="font-semibold text-gray-900">{statistics.cancelled_appointments}</span>
                      </div>
                      <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-600">Taux de présence:</span>
                        <span class="font-semibold text-emerald-600">
                          {((statistics.completed_appointments / statistics.total_appointments) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  {:else}
                    <p class="text-sm text-gray-500">Aucune donnée disponible</p>
                  {/if}
                </div>
              </div>
            </div>
          {:else if activeTab === 'settings'}
            <!-- Settings is always accessible -->
            <DoctorSettings on:profileUpdated={handleProfileUpdated} />
          {:else if !profile}
            <!-- Profile required message for other tabs -->
            <div class="text-center py-12">
              <div class="max-w-md mx-auto">
                <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Profil professionnel requis</h3>
                <p class="text-gray-600 mb-6">
                  Veuillez compléter votre profil professionnel pour accéder à cette section et commencer à gérer vos {activeTab === 'appointments' ? 'rendez-vous' : activeTab === 'availability' ? 'disponibilités' : activeTab === 'patients' ? 'patients' : activeTab === 'reviews' ? 'avis' : activeTab === 'messages' ? 'messages' : 'paiements'}.
                </p>
                <button 
                  on:click={() => activeTab = 'settings'}
                  class="inline-flex items-center px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium"
                >
                  Compléter mon profil
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </button>
              </div>
            </div>
          {:else if activeTab === 'appointments'}
            <DoctorAppointments />
          {:else if activeTab === 'availability'}
            <DoctorAvailability />
          {:else if activeTab === 'patients'}
            <DoctorPatients />
          {:else if activeTab === 'reviews'}
            <DoctorReviews />
          {:else if activeTab === 'messages'}
            <DoctorMessages />
          {:else if activeTab === 'payments'}
            <DoctorPayments />
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>

<style lang="postcss">
  .badge {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
  }

  .badge-warning {
    @apply bg-yellow-100 text-yellow-800;
  }

  .badge-info {
    @apply bg-blue-100 text-blue-800;
  }

  .badge-success {
    @apply bg-green-100 text-green-800;
  }

  .badge-error {
    @apply bg-red-100 text-red-800;
  }

  .badge-secondary {
    @apply bg-gray-100 text-gray-800;
  }

  .badge-neutral {
    @apply bg-gray-100 text-gray-600;
  }
</style>
