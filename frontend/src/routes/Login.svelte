<script lang="ts">
  import type { AxiosError } from 'axios';
  import { navigate } from '../lib/router';
  import { authStore } from '../lib/stores/auth';
  import { login } from '../lib/api';
  import type { LoginCredentials } from '../lib/api';
  import '../styles/login.css';

  let credentials: LoginCredentials = {
    email: '',
    password: '',
  };

  let error: string | null = null;
  let loading = false;
  let showPassword = false;
  let emailTouched = false;
  let passwordTouched = false;

  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  interface ApiErrorData {
    detail?: string;
  }

  const clearError = () => {
    if (error) {
      error = null;
    }
  };

  // Map API error responses to contextual messages for the user.
  const getLoginErrorMessage = (err: unknown): string => {
    const apiError = err as AxiosError<ApiErrorData> | undefined;
    const status = apiError?.response?.status;
    const detailText = typeof apiError?.response?.data?.detail === 'string'
      ? apiError.response?.data?.detail
      : '';
    const detailLower = detailText.toLowerCase();

    if (status === 400) {
      if (detailLower.includes('email')) {
        return 'Email invalide. Veuillez vérifier votre adresse email.';
      }
      if (detailLower.includes('password')) {
        return 'Mot de passe requis.';
      }
      return 'Données invalides. Veuillez vérifier vos informations.';
    }

    if (status === 401) {
      if (detailLower.includes('not found') || detailLower.includes('does not exist')) {
        return 'Aucun compte trouvé avec cet email. Veuillez vérifier votre email ou créer un compte.';
      }
      if (detailLower.includes('password') || detailLower.includes('incorrect') || detailLower.includes('invalid credentials')) {
        return 'Mot de passe incorrect. Veuillez réessayer.';
      }
      if (detailLower.includes('not verified')) {
        return 'Votre email n\'est pas encore vérifié. Veuillez consulter votre boîte email.';
      }
      return 'Email ou mot de passe incorrect. Veuillez réessayer.';
    }

    if (status === 403) {
      if (detailLower.includes('suspend')) {
        return 'Votre compte a été suspendu. Veuillez contacter l\'administrateur.';
      }
      if (detailLower.includes('block') || detailLower.includes('blacklist')) {
        return 'Votre compte a été bloqué. Veuillez contacter le support.';
      }
      if (detailLower.includes('not approved') || detailLower.includes('pending')) {
        return 'Votre compte est en attente d\'approbation par un administrateur.';
      }
      return `Accès refusé. ${detailText || 'Veuillez contacter l\'administrateur.'}`;
    }

    if (status === 422) {
      return 'Données de connexion invalides. Vérifiez votre email et mot de passe.';
    }

    if (status === 429) {
      return 'Trop de tentatives de connexion. Veuillez réessayer dans quelques minutes.';
    }

    if (typeof status === 'number' && status >= 500) {
      return 'Erreur serveur. Veuillez réessayer plus tard.';
    }

    if (apiError?.code === 'ECONNABORTED' || apiError?.code === 'ERR_NETWORK') {
      return 'Erreur de connexion réseau. Vérifiez votre connexion internet.';
    }

    return detailText || 'Erreur de connexion. Veuillez réessayer.';
  };

  // Real-time validation
  $: trimmedEmail = credentials.email.trim();
  $: emailIsValid = EMAIL_REGEX.test(trimmedEmail);
  $: showEmailError = emailTouched && trimmedEmail.length > 0 && !emailIsValid;
  $: passwordIsBlank = credentials.password.trim().length === 0;
  $: showPasswordError = passwordTouched && passwordIsBlank;
  $: canSubmit = emailIsValid && !passwordIsBlank && !loading;

  const handleSubmit = async () => {
    if (loading) return;
    error = null;

    // Mark fields as touched
    emailTouched = true;
    passwordTouched = true;

    // Validation côté client
    if (!trimmedEmail) {
      error = 'Veuillez entrer votre adresse email.';
      return;
    }

    if (passwordIsBlank) {
      error = 'Veuillez entrer votre mot de passe.';
      return;
    }

    // Validation basique du format email
    if (!emailIsValid) {
      error = 'Format d\'email invalide. Exemple: utilisateur@exemple.com';
      return;
    }

    credentials = { ...credentials, email: trimmedEmail };
    loading = true;

    try {
      const response = await login(credentials);
      
      // Store tokens and user in auth store
      authStore.login(response.access_token, response.refresh_token, response.user);

      // Redirect based on role (case-insensitive comparison)
      const userRole = response.user.role.toUpperCase();
      if (userRole === 'ADMIN') {
        navigate('/admin/dashboard');
      } else if (userRole === 'DOCTOR') {
        if (response.user.admin_approved) {
          navigate('/doctors/dashboard');
        } else {
          // Doctor not yet approved
          navigate('/doctors/pending');
        }
      } else {
        navigate('/patient/dashboard');
      }
    } catch (err) {
      console.error('Login error:', err);
      error = getLoginErrorMessage(err);
    } finally {
      loading = false;
    }
  };
</script>

<div class="min-h-screen flex items-center justify-center py-12 px-4" style="background: linear-gradient(135deg, #faf7f2 0%, #fdfbf7 50%, #e8f4f2 100%);">
  <div class="max-w-md w-full">
    <!-- Logo/Title -->
    <div class="text-center mb-8">
      <div class="inline-block mb-4">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto shadow-lg" style="background: linear-gradient(135deg, #67b7b5 0%, #5dabb7 100%);">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
      </div>
      <h1 class="text-4xl font-bold mb-2" style="color: #4a8b8d;">Connexion</h1>
      <p style="color: #6b6863;">Accédez à votre compte</p>
    </div>

    <!-- Login Form -->
    <div class="card">
      <form on:submit|preventDefault={handleSubmit} class="space-y-6" novalidate>
        <!-- Error Message -->
        {#if error}
          <div class="alert alert-error animate-scale-in animate-shake" role="alert" aria-live="assertive">
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-br from-error to-error-dark shadow-lg">
                  <svg class="h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <div class="flex-1 pt-1">
                <h4 class="font-semibold text-red-900 mb-1">Erreur de connexion</h4>
                <p class="text-sm text-red-700 leading-relaxed">{error}</p>
              </div>
            </div>
          </div>
        {/if}

        <!-- Email Field -->
        <div>
          <label for="email" class="form-label">Email</label>
          <div class="relative">
            <input
              id="email"
              type="email"
              bind:value={credentials.email}
              on:blur={() => emailTouched = true}
              on:input={clearError}
              class="input-field {showEmailError ? 'border-error focus:ring-error' : ''}"
              placeholder="votre@email.com"
              required
              disabled={loading}
              autocomplete="email"
              aria-invalid={showEmailError}
              aria-describedby={showEmailError ? 'login-email-error' : undefined}
            />
            {#if credentials.email && emailIsValid}
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-success" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </div>
            {/if}
          </div>
          {#if showEmailError}
            <p id="login-email-error" class="mt-2 text-sm text-error flex items-center gap-1">
              <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              Format d'email invalide
            </p>
          {/if}
        </div>

        <!-- Password Field -->
        <div>
          <label for="password" class="form-label">Mot de passe</label>
          <div class="relative">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              bind:value={credentials.password}
              on:blur={() => passwordTouched = true}
              on:input={() => error = null}
              class="input-field pr-12 {showPasswordError ? 'border-error focus:ring-error' : ''}"
              placeholder="••••••••"
              required
              disabled={loading}
              autocomplete="current-password"
              aria-invalid={showPasswordError}
              aria-describedby={showPasswordError ? 'login-password-error' : undefined}
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
              on:click={() => showPassword = !showPassword}
              aria-label="Toggle password visibility"
              aria-pressed={showPassword}
              tabindex="-1"
            >
              {#if showPassword}
                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              {:else}
                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              {/if}
            </button>
          </div>
          {#if showPasswordError}
            <p id="login-password-error" class="mt-2 text-sm text-error flex items-center gap-1">
              <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              Le mot de passe est requis.
            </p>
          {/if}
        </div>

        <!-- Forgot Password Link -->
        <div class="text-right">
          <button type="button" on:click={() => navigate('/forgot-password')} class="text-sm text-primary-600 hover:text-primary-700 font-medium underline decoration-1 underline-offset-2 transition-colors">
            Mot de passe oublié ?
          </button>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          class="btn-primary w-full {loading ? 'animate-pulse' : ''} transition-all hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed"
          disabled={!canSubmit}
          aria-busy={loading}
        >
          {#if loading}
            <span class="flex items-center justify-center gap-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Connexion en cours...
            </span>
          {:else}
            <span class="flex items-center justify-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              Se connecter
            </span>
          {/if}
        </button>
      </form>

      <!-- Registration Links -->
      <div class="mt-6 pt-6 border-t border-gray-200">
        <p class="text-center text-sm text-gray-600 mb-4">Pas encore de compte ?</p>
        <div class="space-y-3">
          <button type="button" on:click={() => navigate('/register/patient')} class="block text-center text-sm text-primary-600 hover:text-primary-700 font-semibold w-full py-2 px-4 rounded-lg hover:bg-primary-50 transition-all">
            S'inscrire comme Patient →
          </button>
          <button type="button" on:click={() => navigate('/register/doctor')} class="block text-center text-sm text-success hover:text-success-dark font-semibold w-full py-2 px-4 rounded-lg hover:bg-success-light transition-all">
            S'inscrire comme Médecin →
          </button>
        </div>
      </div>
    </div>

    <!-- Back to Home -->
    <div class="text-center mt-6">
      <button type="button" on:click={() => navigate('/')} class="inline-flex items-center gap-2 text-gray-700 hover:text-primary-700 font-medium transition-all hover:gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Retour à l'accueil
      </button>
    </div>
  </div>
</div>
