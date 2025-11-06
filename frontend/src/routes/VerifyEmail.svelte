<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from '../lib/router';
  import { verifyEmail } from '../lib/api';

  let loading = true;
  let success = false;
  let error = '';
  let message = '';

  onMount(async () => {
    // Get token from URL query parameter
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');

    if (!token) {
      error = 'Token de vérification manquant. Veuillez utiliser le lien fourni dans votre email.';
      loading = false;
      return;
    }

    try {
      const response = await verifyEmail(token);
      success = true;
      message = response.message || 'Votre email a été vérifié avec succès !';
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err: any) {
      error = err.response?.data?.detail || 'Une erreur est survenue lors de la vérification de votre email.';
      success = false;
    } finally {
      loading = false;
    }
  });
</script>

<div class="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50 flex items-center justify-center px-4">
  <div class="max-w-md w-full">
    <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
      <!-- Logo -->
      <div class="flex justify-center mb-6">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>

      <h1 class="text-2xl font-bold text-gray-900 text-center mb-2">
        Vérification Email
      </h1>

      {#if loading}
        <div class="text-center py-8">
          <svg class="animate-spin h-12 w-12 text-emerald-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-gray-600">Vérification en cours...</p>
        </div>
      {:else if success}
        <div class="text-center py-8">
          <div class="mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-green-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-lg text-gray-800 font-medium mb-2">Email vérifié !</p>
          <p class="text-gray-600">{message}</p>
          <p class="text-sm text-gray-500 mt-4">Redirection vers la page de connexion...</p>
        </div>
      {:else if error}
        <div class="text-center py-8">
          <div class="mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-red-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-lg text-gray-800 font-medium mb-2">Échec de la vérification</p>
          <p class="text-gray-600 mb-6">{error}</p>
          <button
            on:click={() => navigate('/login')}
            class="inline-flex items-center px-6 py-2 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors"
          >
            Aller à la connexion
          </button>
        </div>
      {/if}
    </div>
  </div>
</div>
