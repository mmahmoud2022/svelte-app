<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    getMyPatients,
    getPatientMedicalRecord,
    type PatientInfo,
    type MedicalRecord
  } from '../../lib/api-doctor';
  
  let patients: PatientInfo[] = [];
  let loading = true;
  let error: string | null = null;
  let selectedPatient: PatientInfo | null = null;
  let showDetailsModal = false;
  let medicalRecord: MedicalRecord | null = null;
  let loadingRecord = false;

  onMount(async () => {
    await loadPatients();
  });

  const loadPatients = async () => {
    loading = true;
    error = null;
    try {
      const response = await getMyPatients(1, 100);
      patients = response.items || [];
    } catch (err: any) {
      console.error('Error loading patients:', err);
      error = 'Erreur lors du chargement des patients';
    } finally {
      loading = false;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const openPatientDetails = async (patient: PatientInfo) => {
    selectedPatient = patient;
    showDetailsModal = true;
    loadingRecord = true;
    
    try {
      medicalRecord = await getPatientMedicalRecord(patient.id);
    } catch (err) {
      console.error('Error loading patient medical record:', err);
    } finally {
      loadingRecord = false;
    }
  };

  const closeDetailsModal = () => {
    showDetailsModal = false;
    selectedPatient = null;
    medicalRecord = null;
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

</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h2 class="text-2xl font-bold text-gray-900">Mes Patients</h2>
      <p class="text-gray-600 mt-1">{patients.length} patient{patients.length > 1 ? 's' : ''} au total</p>
    </div>
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
  {:else if patients.length === 0}
    <div class="text-center py-12 bg-white rounded-lg border border-gray-200">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
      <p class="text-gray-600">Aucun patient pour le moment</p>
    </div>
  {:else}
    <!-- Patients Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each patients as patient}
        <button 
          type="button"
          class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow text-left w-full"
          on:click={() => openPatientDetails(patient)}
        >
          <div class="flex items-start gap-4">
            <div class="w-14 h-14 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-full flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 truncate">{patient.first_name} {patient.last_name}</h3>
              <p class="text-sm text-gray-500 truncate">{patient.email}</p>
              {#if patient.phone}
                <p class="text-sm text-gray-500 mt-1">{patient.phone}</p>
              {/if}
            </div>
          </div>
          
          <div class="mt-4 pt-4 border-t border-gray-200 space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Rendez-vous:</span>
              <span class="font-semibold text-gray-900">{patient.total_appointments}</span>
            </div>
            {#if patient.last_appointment_date}
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">Dernier RDV:</span>
                <span class="font-medium text-gray-700">{formatDate(patient.last_appointment_date)}</span>
              </div>
            {/if}
          </div>
          
          <span class="mt-4 w-full block px-4 py-2 bg-emerald-50 text-emerald-700 rounded-lg hover:bg-emerald-100 transition-colors text-sm font-medium text-center">
            Voir l'historique
          </span>
        </button>
      {/each}
    </div>
  {/if}
</div>

<!-- Patient Details Modal -->
{#if showDetailsModal && selectedPatient}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-full flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <h3 class="text-2xl font-bold text-gray-900">{selectedPatient.first_name} {selectedPatient.last_name}</h3>
              <p class="text-gray-600">{selectedPatient.email}</p>
              {#if selectedPatient.phone}
                <p class="text-gray-600">{selectedPatient.phone}</p>
              {/if}
            </div>
          </div>
          <button on:click={closeDetailsModal} class="text-gray-400 hover:text-gray-600" title="Fermer">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span class="sr-only">Fermer</span>
          </button>
        </div>
      </div>
      
      <!-- Stats -->
      <div class="p-6 bg-gray-50 border-b border-gray-200">
        <div class="grid grid-cols-2 gap-4">
          <div class="text-center">
            <p class="text-3xl font-bold text-gray-900">{selectedPatient.total_appointments}</p>
            <p class="text-sm text-gray-600 mt-1">Total rendez-vous</p>
          </div>
          <div class="text-center">
            <p class="text-3xl font-bold text-emerald-600">
              {medicalRecord?.total_consultations || 0}
            </p>
            <p class="text-sm text-gray-600 mt-1">Consultations terminées</p>
          </div>
        </div>
      </div>
      
      <!-- Appointments History -->
      <div class="p-6">
        <h4 class="text-lg font-semibold text-gray-900 mb-4">Historique des consultations</h4>
        
        {#if loadingRecord}
          <div class="flex items-center justify-center py-8">
            <svg class="animate-spin h-6 w-6 text-emerald-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        {:else if !medicalRecord || medicalRecord.appointments.length === 0}
          <p class="text-gray-500 text-center py-8">Aucun rendez-vous trouvé</p>
        {:else}
          <div class="space-y-3 max-h-96 overflow-y-auto">
            {#each medicalRecord.appointments as appointment}
              <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div class="flex items-start justify-between mb-2">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <p class="font-medium text-gray-900">
                        {formatDate(appointment.appointment_date)}
                      </p>
                      <span class="px-2 py-1 rounded-full text-xs font-medium {getStatusBadgeClass(appointment.status)}">
                        {getStatusLabel(appointment.status)}
                      </span>
                    </div>
                    {#if appointment.reason}
                      <p class="text-sm text-gray-600">Motif: {appointment.reason}</p>
                    {/if}
                  </div>
                </div>
                {#if appointment.doctor_notes}
                  <div class="bg-gray-100 rounded p-3 mt-2">
                    <p class="text-sm font-medium text-gray-900 mb-1">Notes:</p>
                    <p class="text-sm text-gray-700">{appointment.doctor_notes}</p>
                  </div>
                {/if}
              </div>
            {/each}
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
