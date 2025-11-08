<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    getDoctorAppointments, 
    updateAppointmentStatus,
    type Appointment,
    type AppointmentStatus 
  } from '../../lib/api-doctor';
  
  let appointments: Appointment[] = [];
  let loading = true;
  let error: string | null = null;
  let filterStatus: AppointmentStatus | 'all' = 'all';
  let selectedAppointment: Appointment | null = null;
  let showDetailsModal = false;
  
  let updateStatusModal = false;
  let newStatus: AppointmentStatus = 'confirmed';
  let statusNotes = '';
  let statusPrescription = '';
  let statusDiagnosis = '';
  let updatingStatus = false;

  onMount(async () => {
    await loadAppointments();
  });

  const loadAppointments = async () => {
    loading = true;
    error = null;
    try {
      const status = filterStatus === 'all' ? undefined : filterStatus;
      const response = await getDoctorAppointments(1, 100, status);
      appointments = response.items || [];
    } catch (err: any) {
      console.error('Error loading appointments:', err);
      error = 'Erreur lors du chargement des rendez-vous';
    } finally {
      loading = false;
    }
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
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'no_show': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-600';
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

  const getConsultationTypeLabel = (type: string) => {
    switch (type) {
      case 'in_person': return 'En personne';
      case 'teleconsultation': return 'Téléconsultation';
      case 'home_visit': return 'Visite à domicile';
      case 'emergency': return 'Urgence';
      default: return type;
    }
  };

  const openDetailsModal = (appointment: Appointment) => {
    selectedAppointment = appointment;
    showDetailsModal = true;
  };

  const closeDetailsModal = () => {
    showDetailsModal = false;
    selectedAppointment = null;
  };

  const openUpdateStatusModal = (appointment: Appointment) => {
    selectedAppointment = appointment;
    newStatus = appointment.status;
    statusNotes = appointment.notes || '';
    statusPrescription = appointment.prescription || '';
    statusDiagnosis = appointment.diagnosis || '';
    updateStatusModal = true;
  };

  const closeUpdateStatusModal = () => {
    updateStatusModal = false;
    selectedAppointment = null;
    statusNotes = '';
    statusPrescription = '';
    statusDiagnosis = '';
  };

  const handleUpdateStatus = async () => {
    if (!selectedAppointment) return;
    
    updatingStatus = true;
    try {
      await updateAppointmentStatus(selectedAppointment.id, {
        status: newStatus,
        notes: statusNotes || undefined,
        prescription: statusPrescription || undefined,
        diagnosis: statusDiagnosis || undefined,
      });
      
      closeUpdateStatusModal();
      await loadAppointments();
    } catch (err: any) {
      console.error('Error updating status:', err);
      alert('Erreur lors de la mise à jour du statut');
    } finally {
      updatingStatus = false;
    }
  };

  $: filteredAppointments = appointments;
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <h2 class="text-2xl font-bold text-gray-900">Mes Rendez-vous</h2>
    <select
      bind:value={filterStatus}
      on:change={loadAppointments}
      class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
    >
      <option value="all">Tous</option>
      <option value="pending">En attente</option>
      <option value="confirmed">Confirmés</option>
      <option value="completed">Terminés</option>
      <option value="cancelled">Annulés</option>
      <option value="no_show">Absents</option>
    </select>
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
  {:else if filteredAppointments.length === 0}
    <div class="text-center py-12">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-gray-600">Aucun rendez-vous trouvé</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-4">
      {#each filteredAppointments as appointment}
        <div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <h3 class="font-semibold text-gray-900 text-lg">
                    {appointment.patient?.full_name || 'Patient inconnu'}
                  </h3>
                  <p class="text-sm text-gray-500">{appointment.patient?.email || ''}</p>
                </div>
                <span class="px-3 py-1 rounded-full text-sm font-medium {getStatusBadgeClass(appointment.status)}">
                  {getStatusLabel(appointment.status)}
                </span>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                <div class="flex items-center gap-2 text-gray-600">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span class="text-sm">{formatDate(appointment.appointment_date)}</span>
                </div>
                <div class="flex items-center gap-2 text-gray-600">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <span class="text-sm">{getConsultationTypeLabel(appointment.consultation_type)}</span>
                </div>
              </div>

              {#if appointment.reason}
                <div class="bg-gray-50 rounded-lg p-3 mb-3">
                  <p class="text-sm text-gray-700"><strong>Motif:</strong> {appointment.reason}</p>
                </div>
              {/if}

              {#if appointment.notes || appointment.diagnosis || appointment.prescription}
                <div class="bg-blue-50 rounded-lg p-3 mb-3">
                  {#if appointment.notes}
                    <p class="text-sm text-gray-700 mb-1"><strong>Notes:</strong> {appointment.notes}</p>
                  {/if}
                  {#if appointment.diagnosis}
                    <p class="text-sm text-gray-700 mb-1"><strong>Diagnostic:</strong> {appointment.diagnosis}</p>
                  {/if}
                  {#if appointment.prescription}
                    <p class="text-sm text-gray-700"><strong>Prescription:</strong> {appointment.prescription}</p>
                  {/if}
                </div>
              {/if}
            </div>
          </div>

          <div class="flex gap-3 mt-4 pt-4 border-t border-gray-200">
            <button
              on:click={() => openDetailsModal(appointment)}
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Détails
            </button>
            <button
              on:click={() => openUpdateStatusModal(appointment)}
              class="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
            >
              Mettre à jour
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Details Modal -->
{#if showDetailsModal && selectedAppointment}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900">Détails du rendez-vous</h3>
          <button on:click={closeDetailsModal} class="text-gray-400 hover:text-gray-600" title="Fermer">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span class="sr-only">Fermer</span>
          </button>
        </div>
      </div>
      <div class="p-6 space-y-4">
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Patient</h4>
          <p class="text-gray-700">{selectedAppointment.patient?.full_name}</p>
          <p class="text-sm text-gray-500">{selectedAppointment.patient?.email}</p>
        </div>
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Date et heure</h4>
          <p class="text-gray-700">{formatDate(selectedAppointment.appointment_date)}</p>
        </div>
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Type de consultation</h4>
          <p class="text-gray-700">{getConsultationTypeLabel(selectedAppointment.consultation_type)}</p>
        </div>
        <div>
          <h4 class="font-semibold text-gray-900 mb-2">Statut</h4>
          <span class="px-3 py-1 rounded-full text-sm font-medium {getStatusBadgeClass(selectedAppointment.status)}">
            {getStatusLabel(selectedAppointment.status)}
          </span>
        </div>
        {#if selectedAppointment.reason}
          <div>
            <h4 class="font-semibold text-gray-900 mb-2">Motif</h4>
            <p class="text-gray-700">{selectedAppointment.reason}</p>
          </div>
        {/if}
        {#if selectedAppointment.notes}
          <div>
            <h4 class="font-semibold text-gray-900 mb-2">Notes</h4>
            <p class="text-gray-700">{selectedAppointment.notes}</p>
          </div>
        {/if}
        {#if selectedAppointment.diagnosis}
          <div>
            <h4 class="font-semibold text-gray-900 mb-2">Diagnostic</h4>
            <p class="text-gray-700">{selectedAppointment.diagnosis}</p>
          </div>
        {/if}
        {#if selectedAppointment.prescription}
          <div>
            <h4 class="font-semibold text-gray-900 mb-2">Prescription</h4>
            <p class="text-gray-700">{selectedAppointment.prescription}</p>
          </div>
        {/if}
      </div>
      <div class="p-6 border-t border-gray-200">
        <button
          on:click={closeDetailsModal}
          class="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          Fermer
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Update Status Modal -->
{#if updateStatusModal && selectedAppointment}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900">Mettre à jour le rendez-vous</h3>
          <button on:click={closeUpdateStatusModal} class="text-gray-400 hover:text-gray-600" title="Fermer">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span class="sr-only">Fermer</span>
          </button>
        </div>
      </div>
      <div class="p-6 space-y-4">
        <div>
          <label for="status-select" class="block text-sm font-medium text-gray-700 mb-2">Statut</label>
          <select
            id="status-select"
            bind:value={newStatus}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
          >
            <option value="pending">En attente</option>
            <option value="confirmed">Confirmé</option>
            <option value="completed">Terminé</option>
            <option value="cancelled">Annulé</option>
            <option value="no_show">Absent</option>
          </select>
        </div>
        <div>
          <label for="status-notes" class="block text-sm font-medium text-gray-700 mb-2">Notes</label>
          <textarea
            id="status-notes"
            bind:value={statusNotes}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            rows="3"
            placeholder="Notes supplémentaires..."
          ></textarea>
        </div>
        <div>
          <label for="status-diagnosis" class="block text-sm font-medium text-gray-700 mb-2">Diagnostic</label>
          <textarea
            id="status-diagnosis"
            bind:value={statusDiagnosis}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            rows="3"
            placeholder="Diagnostic médical..."
          ></textarea>
        </div>
        <div>
          <label for="status-prescription" class="block text-sm font-medium text-gray-700 mb-2">Prescription</label>
          <textarea
            id="status-prescription"
            bind:value={statusPrescription}
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
            rows="3"
            placeholder="Médicaments prescrits..."
          ></textarea>
        </div>
      </div>
      <div class="p-6 border-t border-gray-200 flex gap-3">
        <button
          on:click={closeUpdateStatusModal}
          class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          disabled={updatingStatus}
        >
          Annuler
        </button>
        <button
          on:click={handleUpdateStatus}
          class="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50"
          disabled={updatingStatus}
        >
          {updatingStatus ? 'Mise à jour...' : 'Enregistrer'}
        </button>
      </div>
    </div>
  </div>
{/if}
