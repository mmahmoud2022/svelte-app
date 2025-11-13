<script lang="ts">
  import { navigate } from '../lib/router';
  import { requestPasswordReset } from '../lib/api';

  let email = '';
  let loading = false;
  let success = false;
  let error = '';

  async function handleSubmit() {
    if (!email) {
      error = 'Veuillez entrer votre adresse email.';
      return;
    }

    loading = true;
    error = '';

    try {
      const response = await requestPasswordReset(email);
      success = true;
      error = '';
    } catch (err: any) {
      error = err.response?.data?.detail || 'Une erreur est survenue. Veuillez réessayer.';
      success = false;
    } finally {
      loading = false;
    }
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
        Mot de passe oublié
      </h1>
      <p class="text-gray-600 text-center mb-6">
        Entrez votre email pour recevoir un lien de réinitialisation
      </p>

      {#if success}
        <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <div class="flex items-start gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p class="text-sm text-green-800">
                Un email de réinitialisation a été envoyé à <strong>{email}</strong>.
              </p>
              <p class="text-sm text-green-700 mt-2">
                Vérifiez votre boîte de réception et suivez les instructions pour réinitialiser votre mot de passe.
              </p>
            </div>
          </div>
        </div>

        <button
          on:click={() => navigate('/login')}
          class="w-full py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors"
        >
          Retour à la connexion
        </button>
      {:else}
        <form on:submit|preventDefault={handleSubmit} class="space-y-6">
          {#if error}
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
              <p class="text-sm text-red-800">{error}</p>
            </div>
          {/if}

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Adresse email
            </label>
            <input
              type="email"
              id="email"
              bind:value={email}
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-shadow"
              placeholder="votre.email@exemple.com"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            class="w-full py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {#if loading}
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Envoi en cours...
            {:else}
              Envoyer le lien de réinitialisation
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
