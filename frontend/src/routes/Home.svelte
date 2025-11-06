<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from '../lib/router';
  import { getStatistics } from '../lib/api';
  import type { StatisticsResponse } from '../lib/api';
  import '../styles/home.css';

  let statistics: StatisticsResponse | null = null;
  let loading = true;
  let error: string | null = null;

  onMount(async () => {
    try {
      statistics = await getStatistics();
    } catch (err: any) {
      error = err.response?.data?.detail || 'Erreur lors du chargement des statistiques';
    } finally {
      loading = false;
    }
  });
</script>

<div class="min-h-screen" style="background: linear-gradient(135deg, #faf7f2 0%, #fdfbf7 50%, #e8f4f2 100%);">
  <!-- Hero Section -->
  <header class="py-24 px-4">
    <div class="max-w-6xl mx-auto text-center">
      <div class="inline-block mb-6 animate-bounce">
        <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto shadow-lg" style="background: linear-gradient(135deg, #67b7b5 0%, #5dabb7 100%);">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </div>
      </div>
      <h1 class="text-5xl md:text-7xl font-bold mb-6" style="background: linear-gradient(135deg, #67b7b5 0%, #88b4a4 50%, #5dabb7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
        Plateforme Médicale
      </h1>
      <p class="text-xl md:text-2xl mb-12" style="color: #6b6863;">
        Connectez-vous avec des professionnels de santé qualifiés
      </p>

      <!-- Call to Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
        <button on:click={() => navigate('/register/patient')} class="btn-primary text-lg px-8 py-3">
          S'inscrire comme Patient
        </button>
        <button on:click={() => navigate('/register/doctor')} class="btn-outline text-lg px-8 py-3">
          S'inscrire comme Médecin
        </button>
      </div>

      <div class="mt-6">
        <button on:click={() => navigate('/login')} class="text-primary-600 hover:text-primary-700 font-medium">
          Déjà inscrit ? Connexion →
        </button>
      </div>
    </div>
  </header>

  <!-- Statistics Section -->
  <section class="py-20 px-4">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-4xl md:text-5xl font-bold text-center mb-4" style="color: #4a8b8d;">
        Notre Communauté
      </h2>
      <p class="text-center text-lg mb-12" style="color: #6b6863;">
        Rejoignez des milliers d'utilisateurs qui nous font confiance
      </p>

      {#if loading}
        <div class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      {:else if error}
        <div class="card bg-red-50 border border-red-200 text-center">
          <p class="text-red-600">{error}</p>
        </div>
      {:else if statistics}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <!-- Total Users -->
          <div class="stat-card">
            <div class="flex items-center justify-between mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <p class="text-3xl font-bold mb-2">{statistics.total_users}</p>
            <p class="text-sm opacity-90">Utilisateurs Totaux</p>
          </div>

          <!-- Total Doctors -->
          <div class="stat-card" style="background: linear-gradient(135deg, #50b48f 0%, #3d9975 100%);">
            <div class="flex items-center justify-between mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <p class="text-4xl font-bold mb-2">{statistics.total_doctors}</p>
            <p class="text-sm opacity-90">Médecins Disponibles</p>
          </div>

          <!-- Total Patients -->
          <div class="stat-card" style="background: linear-gradient(135deg, #b4a7d6 0%, #9d8ec4 100%);">
            <div class="flex items-center justify-between mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <p class="text-4xl font-bold mb-2">{statistics.total_patients}</p>
            <p class="text-sm opacity-90">Patients Inscrits</p>
          </div>

          <!-- Active Users -->
          <div class="stat-card" style="background: linear-gradient(135deg, #f4a599 0%, #e88b7c 100%);">
            <div class="flex items-center justify-between mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p class="text-4xl font-bold mb-2">{statistics.active_users}</p>
            <p class="text-sm opacity-90">Utilisateurs Actifs</p>
          </div>
        </div>
      {/if}
    </div>
  </section>

  <!-- Features Section -->
  <section class="py-20 px-4" style="background: linear-gradient(135deg, rgba(253, 251, 247, 0.95) 0%, rgba(250, 247, 242, 0.95) 100%);">
    <div class="max-w-6xl mx-auto">
      <h2 class="text-4xl md:text-5xl font-bold text-center mb-4" style="color: #4a8b8d;">
        Pourquoi Nous Choisir ?
      </h2>
      <p class="text-center text-lg mb-12" style="color: #6b6863;">
        Une plateforme moderne conçue pour votre bien-être
      </p>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="card text-center hover-lift">
          <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg" style="background: linear-gradient(135deg, #67b7b5 0%, #5dabb7 100%);">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold mb-3" style="color: #4a8b8d;">Disponibilité 24/7</h3>
          <p style="color: #6b6863;">Accédez aux services médicaux à tout moment, où que vous soyez.</p>
        </div>

        <div class="card text-center hover-lift">
          <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg" style="background: linear-gradient(135deg, #50b48f 0%, #3d9975 100%);">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold mb-3" style="color: #4a8b8d;">Sécurisé & Confidentiel</h3>
          <p style="color: #6b6863;">Vos données médicales sont protégées avec les normes les plus élevées.</p>
        </div>

        <div class="card text-center hover-lift">
          <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg" style="background: linear-gradient(135deg, #b4a7d6 0%, #9d8ec4 100%);">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold mb-3" style="color: #4a8b8d;">Médecins Qualifiés</h3>
          <p style="color: #6b6863;">Tous nos médecins sont vérifiés et approuvés par notre équipe.</p>
        </div>
      </div>
    </div>
  </section>
</div>
