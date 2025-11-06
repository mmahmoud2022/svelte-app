<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from '../lib/router';
  import { resetPassword } from '../lib/api';

  let token = '';
  let newPassword = '';
  let confirmPassword = '';
  let loading = false;
  let success = false;
  let error = '';

  onMount(() => {
    // Get token from URL query parameter
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    
    if (!urlToken) {
      error = 'Token de réinitialisation manquant. Veuillez utiliser le lien fourni dans votre email.';
    } else {
      token = urlToken;
    }
  });

  async function handleSubmit() {
    error = '';

    if (!token) {
      error = 'Token de réinitialisation manquant.';
      return;
    }

    if (newPassword.length < 8) {
      error = 'Le mot de passe doit contenir au moins 8 caractères.';
      return;
    }

    if (newPassword !== confirmPassword) {
      error = 'Les mots de passe ne correspondent pas.';
      return;
    }

    loading = true;

    try {
      const response = await resetPassword(token, newPassword);
      success = true;
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err: any) {
      error = err.response?.data?.detail || 'Une erreur est survenue lors de la réinitialisation du mot de passe.';
      success = false;
    } finally {
      loading = false;
    }
  }

  function validatePassword(password: string): boolean {
    return password.length >= 8;
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50 flex items-center justify-center px-4">
  <div class="max-w-md w-full">
    <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
      <!-- Logo -->
      <div class="flex justify-center mb-6">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
        </div>
      </div>

      <h1 class="text-2xl font-bold text-gray-900 text-center mb-2">
        Réinitialiser le mot de passe
      </h1>
      <p class="text-gray-600 text-center mb-6">
        Choisissez un nouveau mot de passe sécurisé
      </p>

      {#if success}
        <div class="text-center py-8">
          <div class="mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-green-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-lg text-gray-800 font-medium mb-2">Mot de passe réinitialisé !</p>
          <p class="text-gray-600">Votre mot de passe a été modifié avec succès.</p>
          <p class="text-sm text-gray-500 mt-4">Redirection vers la page de connexion...</p>
        </div>
      {:else}
        <form on:submit|preventDefault={handleSubmit} class="space-y-6">
          {#if error}
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
              <p class="text-sm text-red-800">{error}</p>
            </div>
          {/if}

          <div>
            <label for="newPassword" class="block text-sm font-medium text-gray-700 mb-2">
              Nouveau mot de passe
            </label>
            <input
              type="password"
              id="newPassword"
              bind:value={newPassword}
              required
              minlength="8"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-shadow"
              placeholder="••••••••"
              disabled={loading || !token}
            />
            <p class="text-xs text-gray-500 mt-1">Minimum 8 caractères</p>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
              Confirmer le mot de passe
            </label>
            <input
              type="password"
              id="confirmPassword"
              bind:value={confirmPassword}
              required
              minlength="8"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-shadow"
              placeholder="••••••••"
              disabled={loading || !token}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !token}
            class="w-full py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {#if loading}
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Réinitialisation...
            {:else}
              Réinitialiser le mot de passe
            {/if}
          </button>
        </form>

        <div class="mt-6 text-center">
          <button
            on:click={() => navigate('/login')}
            class="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
          >
            ← Retour à la connexion
          </button>
        </div>
      {/if}
    </div>
  </div>
</div>
