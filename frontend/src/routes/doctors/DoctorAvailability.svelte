<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    getDoctorAvailability,
    getCurrentDoctorProfile,
    createAvailability, 
    deleteAvailability,
    type DoctorAvailability,
    type AvailabilityCreate,
    type ConsultationType
  } from '../../lib/api-doctor';
  
  let availabilities: DoctorAvailability[] = [];
  let loading = true;
  let error: string | null = null;
  let showCreateModal = false;
  let creating = false;
  let doctorId: number | null = null;
  
  let newAvailability: AvailabilityCreate = {
    day_of_week: 1,
    start_time: '09:00',
    end_time: '17:00',
    consultation_type: 'in_person',
    is_available: true
  };

  const daysOfWeek = [
    { value: 1, label: 'Lundi' },
    { value: 2, label: 'Mardi' },
    { value: 3, label: 'Mercredi' },
    { value: 4, label: 'Jeudi' },
    { value: 5, label: 'Vendredi' },
    { value: 6, label: 'Samedi' },
    { value: 0, label: 'Dimanche' }
  ];

  const consultationTypes: { value: ConsultationType; label: string }[] = [
    { value: 'in_person', label: 'En personne' },
    { value: 'teleconsultation', label: 'Téléconsultation' },
    { value: 'both', label: 'Les deux' }
  ];

  onMount(async () => {
    await loadAvailabilities();
  });

  const loadAvailabilities = async () => {
    loading = true;
    error = null;
    try {
      // Get doctor ID first if not already loaded
      if (!doctorId) {
        const profile = await getCurrentDoctorProfile();
        doctorId = profile.id;
      }
      
      availabilities = await getDoctorAvailability(doctorId);
      // Sort by day and time
      availabilities.sort((a, b) => {
        if (a.day_of_week !== b.day_of_week) {
          return a.day_of_week - b.day_of_week;
        }
        return a.start_time.localeCompare(b.start_time);
      });
    } catch (err: any) {
      console.error('Error loading availabilities:', err);
      error = 'Erreur lors du chargement des disponibilités';
    } finally {
      loading = false;
    }
  };

  const getDayLabel = (day: number) => {
    return daysOfWeek.find(d => d.value === day)?.label || '';
  };

  const getConsultationTypeLabel = (type: string) => {
    return consultationTypes.find(t => t.value === type)?.label || type;
  };

  const getConsultationTypeIcon = (type: string) => {
    switch (type) {
      case 'in_person':
        return '🏥';
      case 'teleconsultation':
        return '💻';
      case 'both':
        return '🏥�';
      default:
        return '📅';
    }
  };

  const handleCreate = async () => {
    creating = true;
    try {
      await createAvailability(newAvailability);
      showCreateModal = false;
      resetForm();
      await loadAvailabilities();
    } catch (err: any) {
      console.error('Error creating availability:', err);
      alert('Erreur lors de la création de la disponibilité');
    } finally {
      creating = false;
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette disponibilité ?')) return;
    
    try {
      await deleteAvailability(id);
      await loadAvailabilities();
    } catch (err: any) {
      console.error('Error deleting availability:', err);
      alert('Erreur lors de la suppression');
    }
  };

  const resetForm = () => {
    newAvailability = {
      day_of_week: 1,
      start_time: '09:00',
      end_time: '17:00',
      consultation_type: 'in_person',
      is_available: true
    };
  };

  const openCreateModal = () => {
    resetForm();
    showCreateModal = true;
  };

  // Group availabilities by day
  $: availabilitiesByDay = availabilities.reduce((acc, av) => {
    if (!acc[av.day_of_week]) {
      acc[av.day_of_week] = [];
    }
    acc[av.day_of_week].push(av);
    return acc;
  }, {} as Record<number, DoctorAvailability[]>);
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <h2 class="text-2xl font-bold text-gray-900">Mes Disponibilités</h2>
    <button
      on:click={openCreateModal}
      class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors flex items-center gap-2"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
      Ajouter un créneau
    </button>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-emerald-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-800">{error}</p>
    </div>
  {:else if availabilities.length === 0}
    <div class="text-center py-12 bg-white rounded-lg border border-gray-200">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-gray-600 mb-4">Aucune disponibilité configurée</p>
      <button
        on:click={openCreateModal}
        class="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
      >
        Ajouter votre première disponibilité
      </button>
    </div>
  {:else}
    <!-- Calendar View -->
    <div class="grid grid-cols-1 gap-6">
      {#each daysOfWeek as day}
        {#if availabilitiesByDay[day.value]}
          <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div class="bg-gradient-to-r from-emerald-50 to-teal-50 px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900">{day.label}</h3>
            </div>
            <div class="p-6">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {#each availabilitiesByDay[day.value] as availability}
                  <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow {availability.is_available ? 'bg-white' : 'bg-gray-50'}">
                    <div class="flex items-start justify-between mb-3">
                      <div class="flex items-center gap-2">
                        <span class="text-2xl">{getConsultationTypeIcon(availability.consultation_type)}</span>
                        <div>
                          <p class="font-medium text-gray-900">
                            {availability.start_time} - {availability.end_time}
                          </p>
                          <p class="text-sm text-gray-600">
                            {getConsultationTypeLabel(availability.consultation_type)}
                          </p>
                        </div>
                      </div>
                      {#if availability.is_available}
                        <span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">Disponible</span>
                      {:else}
                        <span class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">Indisponible</span>
                      {/if}
                    </div>
                    <button
                      on:click={() => handleDelete(availability.id)}
                      class="w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      Supprimer
                    </button>
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</div>

<!-- Create Modal -->
{#if showCreateModal}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl max-w-lg w-full">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900">Ajouter une disponibilité</h3>
          <button on:click={() => showCreateModal = false} class="text-gray-400 hover:text-gray-600" title="Fermer">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span class="sr-only">Fermer</span>
          </button>
        </div>
      </div>
      <div class="p-6 space-y-4">
        <div>
          <label for="day-select" class="block text-sm font-medium text-gray-700 mb-2">Jour de la semaine</label>
          <select
            id="day-select"
            bind:value={newAvailability.day_of_week}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
          >
            {#each daysOfWeek as day}
              <option value={day.value}>{day.label}</option>
            {/each}
          </select>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="start-time" class="block text-sm font-medium text-gray-700 mb-2">Heure de début</label>
            <input
              id="start-time"
              type="time"
              bind:value={newAvailability.start_time}
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label for="end-time" class="block text-sm font-medium text-gray-700 mb-2">Heure de fin</label>
            <input
              id="end-time"
              type="time"
              bind:value={newAvailability.end_time}
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>
        <div>
          <label for="consultation-type" class="block text-sm font-medium text-gray-700 mb-2">Type de consultation</label>
          <select
            id="consultation-type"
            bind:value={newAvailability.consultation_type}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
          >
            {#each consultationTypes as type}
              <option value={type.value}>{getConsultationTypeIcon(type.value)} {type.label}</option>
            {/each}
          </select>
        </div>
        <div class="flex items-center gap-3">
          <input
            type="checkbox"
            id="is_available"
            bind:checked={newAvailability.is_available}
            class="w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500"
          />
          <label for="is_available" class="text-sm font-medium text-gray-700">
            Créneau disponible pour les réservations
          </label>
        </div>
      </div>
      <div class="p-6 border-t border-gray-200 flex gap-3">
        <button
          on:click={() => showCreateModal = false}
          class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          disabled={creating}
        >
          Annuler
        </button>
        <button
          on:click={handleCreate}
          class="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50"
          disabled={creating}
        >
          {creating ? 'Création...' : 'Créer'}
        </button>
      </div>
    </div>
  </div>
{/if}
