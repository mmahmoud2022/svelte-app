<script lang="ts">
  import type { StatisticsResponse } from '../../lib/api';
  import UsersIcon from '../icons/UsersIcon.svelte';
  import HeartIcon from '../icons/HeartIcon.svelte';
  import UserIcon from '../icons/UserIcon.svelte';
  import CheckIcon from '../icons/CheckIcon.svelte';
  
  export let statistics: StatisticsResponse | null = null;
  export let loading: boolean = false;
  export let error: string | null = null;
</script>

<section class="statistics-section">
  <div class="max-w-6xl mx-auto">
    <div class="section-header">
      <h2 class="section-title">
        Notre Communauté
      </h2>
      <p class="section-subtitle">
        Rejoignez des milliers d'utilisateurs qui nous font confiance
      </p>
    </div>

    {#if loading}
      <div class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" role="status">
          <span class="sr-only">Chargement des statistiques...</span>
        </div>
      </div>
    {:else if error}
      <div class="card bg-red-50 border border-red-200 text-center" role="alert">
        <p class="text-red-600">{error}</p>
      </div>
    {:else if statistics}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Total Users -->
        <div class="stat-card" role="article" aria-label="Total users statistic">
          <div class="flex items-center justify-between mb-4">
            <UsersIcon size="40" color="white" className="stat-icon" ariaLabel="Total users icon" />
          </div>
          <p class="stat-number">{statistics.total_users}</p>
          <p class="stat-label">Utilisateurs Totaux</p>
        </div>

        <!-- Total Doctors -->
        <div class="stat-card stat-card-emerald" role="article" aria-label="Doctors available statistic">
          <div class="flex items-center justify-between mb-4">
            <HeartIcon size="40" color="white" className="stat-icon" ariaLabel="Doctors icon" />
          </div>
          <p class="stat-number">{statistics.total_doctors}</p>
          <p class="stat-label">Médecins Disponibles</p>
        </div>

        <!-- Total Patients -->
        <div class="stat-card stat-card-lavender" role="article" aria-label="Registered patients statistic">
          <div class="flex items-center justify-between mb-4">
            <UserIcon size="40" color="white" className="stat-icon" ariaLabel="Patients icon" />
          </div>
          <p class="stat-number">{statistics.total_patients}</p>
          <p class="stat-label">Patients Inscrits</p>
        </div>

        <!-- Active Users -->
        <div class="stat-card stat-card-peach" role="article" aria-label="Active users statistic">
          <div class="flex items-center justify-between mb-4">
            <CheckIcon size="40" color="white" className="stat-icon" ariaLabel="Active users icon" />
          </div>
          <p class="stat-number">{statistics.active_users}</p>
          <p class="stat-label">Utilisateurs Actifs</p>
        </div>
      </div>
    {/if}
  </div>
</section>
