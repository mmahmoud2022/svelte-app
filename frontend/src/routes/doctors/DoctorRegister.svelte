<script lang="ts">
  import { navigate } from '../../lib/router';
  import { registerDoctor } from '../../lib/api';
  import type { DoctorRegistrationData, RegistrationResponse } from '../../lib/api';
  import '../../styles/doctor-register.css';

  let formData: DoctorRegistrationData = {
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone: '',
    gender: '',
    specialization: '',
    consultation_fee: undefined,
    bio: '',
    languages_spoken: '',
  };

  let confirmPassword = '';
  let error: string | null = null;
  let loading = false;
  let success = false;
  let registrationResult: RegistrationResponse | null = null;
  let currentStep = 1;
  let showPassword = false;
  let showConfirmPassword = false;

  // Password requirements tracking
  $: passwordReqs = {
    minLength: formData.password.length >= 8,
    hasUpper: /[A-Z]/.test(formData.password),
    hasLower: /[a-z]/.test(formData.password),
    hasNumber: /[0-9]/.test(formData.password),
  };

  $: allPasswordReqsMet = Object.values(passwordReqs).every(Boolean);
  $: passwordsMatch = confirmPassword === '' || formData.password === confirmPassword;

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    error = null;
    loading = true;

    if (!allPasswordReqsMet) {
      error = 'Le mot de passe ne respecte pas tous les critères requis';
      loading = false;
      return;
    }

    if (formData.password !== confirmPassword) {
      error = 'Les mots de passe ne correspondent pas';
      loading = false;
      return;
    }

    try {
      registrationResult = await registerDoctor(formData);
      success = true;

      setTimeout(() => {
        navigate('/login');
      }, 5000);
    } catch (err: any) {
      console.error('Registration error:', err);
      if (err.response?.status === 400) {
        error = err.response.data?.detail || 'Données invalides';
      } else if (err.response?.status === 422) {
        const validationErrors = err.response?.data?.detail;
        if (Array.isArray(validationErrors) && validationErrors.length > 0) {
          // Extract the most relevant error message
          const firstError = validationErrors[0];
          error = firstError.msg || 'Erreur de validation des données';
        } else if (typeof validationErrors === 'string') {
          error = validationErrors;
        } else {
          error = 'Erreur de validation des données';
        }
      } else if (err.response?.status === 409) {
        error = 'Un compte existe déjà avec cet email';
      } else if (err.response?.status === 403) {
        error = err.response.data?.detail || 'Email bloqué ou suspendu';
      } else {
        error = 'Erreur lors de l\'inscription. Veuillez réessayer.';
      }
    } finally {
      loading = false;
    }
  };

  const nextStep = () => {
    if (currentStep < 2) currentStep++;
  };

  const prevStep = () => {
    if (currentStep > 1) currentStep--;
  };

  const validateStep1 = () => {
    if (!formData.first_name || !formData.last_name || !formData.email || 
        !formData.password || !confirmPassword) {
      error = 'Veuillez remplir tous les champs obligatoires';
      return false;
    }
    if (!allPasswordReqsMet) {
      error = 'Le mot de passe ne respecte pas tous les critères requis';
      return false;
    }
    if (formData.password !== confirmPassword) {
      error = 'Les mots de passe ne correspondent pas';
      return false;
    }
    error = null;
    return true;
  };

  const handleNextStep = () => {
    if (validateStep1()) {
      nextStep();
    }
  };
</script>

<div class="min-h-screen py-12 px-4">
  <div class="max-w-4xl mx-auto">
    <!-- Header with animated icon -->
    <div class="text-center mb-10 animate-slide-down">
      <div class="inline-block mb-6 relative">
        <div class="w-20 h-20 rounded-3xl flex items-center justify-center mx-auto shadow-lg animate-bounce bg-gradient-to-br from-accent-emerald to-primary-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div class="absolute" style="top: -5px; right: -5px; width: 24px; height: 24px; background: linear-gradient(135deg, #6bcf9d 0%, #50b48f 100%); border-radius: 50%; box-shadow: 0 2px 10px rgba(107, 207, 157, 0.4);"></div>
      </div>
      <h1 class="text-4xl md:text-5xl font-bold mb-3 text-primary-700">Inscription Médecin</h1>
      <p class="text-lg text-neutral">Rejoignez notre réseau de professionnels de santé</p>
    </div>

    {#if success && registrationResult}
      <!-- Success Message -->
      <div class="card-elevated animate-slide-down">
        <div class="alert alert-success">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
              <div class="w-16 h-16 rounded-2xl flex items-center justify-center shadow-lg bg-gradient-to-br from-success to-success-dark">
                <svg class="h-8 w-8 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div class="flex-1">
              <h3 class="text-2xl font-bold mb-2 text-green-900">{registrationResult.message}</h3>
              
              {#if registrationResult.requires_admin_approval}
                <div class="alert alert-warning mt-4">
                  <svg class="h-6 w-6 text-warning flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div>
                    <h4 class="font-semibold mb-1 text-yellow-800">Approbation requise</h4>
                    <p class="text-yellow-700 leading-relaxed">
                      Votre compte doit être approuvé par un administrateur avant de pouvoir vous connecter.
                      Vous recevrez un email une fois votre compte validé.
                    </p>
                  </div>
                </div>
              {/if}

              {#if registrationResult.next_steps.length > 0}
                <div class="mt-5 p-4 rounded-xl bg-success-light">
                  <p class="font-semibold mb-3 text-green-800">📋 Prochaines étapes :</p>
                  <ul class="space-y-2">
                    {#each registrationResult.next_steps as step, index}
                      <li class="flex items-start gap-3 animate-slide-down">
                        <span class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold bg-gradient-to-br from-success to-success-dark text-white">{index + 1}</span>
                        <span class="text-green-900 leading-relaxed">{step}</span>
                      </li>
                    {/each}
                  </ul>
                </div>
              {/if}

              <div class="mt-5 flex items-center gap-2 text-green-800">
                <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p class="font-medium">Redirection vers la page de connexion...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    {:else}
      <!-- Registration Form -->
      <div class="card hover-lift">
        <!-- Step Indicator -->
        <div class="flex items-center justify-center gap-6 mb-10">
          <div class="flex flex-col items-center gap-2">
            <div class="flex items-center justify-center w-16 h-16 rounded-2xl font-bold text-xl transition-all duration-300 {currentStep === 1 ? 'bg-gradient-to-br from-success via-accent-emerald to-success-dark text-white shadow-xl scale-110 ring-4 ring-success-light' : currentStep > 1 ? 'bg-gradient-to-br from-primary-500 to-primary-600 text-white shadow-md' : 'bg-gray-200 text-gray-500'}">
              {#if currentStep > 1}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              {:else}
                1
              {/if}
            </div>
            <span class="text-sm font-semibold {currentStep === 1 ? 'text-success' : currentStep > 1 ? 'text-primary-600' : 'text-gray-400'}">Personnel</span>
          </div>
          
          <div class="w-24 h-2 rounded-full transition-all duration-500 {currentStep > 1 ? 'bg-gradient-to-r from-primary-500 to-primary-600 shadow-md' : 'bg-gray-200'}"></div>
          
          <div class="flex flex-col items-center gap-2">
            <div class="flex items-center justify-center w-16 h-16 rounded-2xl font-bold text-xl transition-all duration-300 {currentStep === 2 ? 'bg-gradient-to-br from-success via-accent-emerald to-success-dark text-white shadow-xl scale-110 ring-4 ring-success-light' : 'bg-gray-200 text-gray-500'}">
              2
            </div>
            <span class="text-sm font-semibold {currentStep === 2 ? 'text-success' : 'text-gray-400'}">Professionnel</span>
          </div>
        </div>

        <form on:submit={handleSubmit} class="space-y-6">
          <!-- Error Message -->
          {#if error}
            <div class="alert alert-error animate-scale-in animate-shake">
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0">
                  <div class="w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-br from-error to-error-dark shadow-lg animate-error-pulse">
                    <svg class="h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div class="flex-1 pt-1">
                  <h4 class="font-semibold text-red-900 mb-1">Erreur d'inscription</h4>
                  <p class="text-sm text-red-700 leading-relaxed">{error}</p>
                </div>
              </div>
            </div>
          {/if}

          {#if currentStep === 1}
            <!-- Step 1: Personal Information -->
            <div class="space-y-5 animate-fade-in">
              <div class="relative mb-6 p-4 rounded-2xl bg-gradient-to-r from-green-50 via-emerald-50 to-green-50 border-l-4 border-success">
                <div class="flex items-center gap-4">
                  <div class="w-14 h-14 rounded-xl flex items-center justify-center bg-gradient-to-br from-success to-success-dark shadow-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-2xl font-bold text-success-dark">Informations personnelles</h3>
                    <p class="text-sm text-success mt-1">Créez votre profil médecin</p>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label for="first_name" class="form-label">Prénom *</label>
                  <input
                    id="first_name"
                    type="text"
                    bind:value={formData.first_name}
                    class="input-field"
                    placeholder="Marie"
                    required
                    disabled={loading}
                  />
                </div>

                <div>
                  <label for="last_name" class="form-label">Nom *</label>
                  <input
                    id="last_name"
                    type="text"
                    bind:value={formData.last_name}
                    class="input-field"
                    placeholder="Martin"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <div>
                <label for="email" class="form-label">Email professionnel *</label>
                <input
                  id="email"
                  type="email"
                  bind:value={formData.email}
                  class="input-field"
                  placeholder="dr.martin@example.com"
                  required
                  disabled={loading}
                />
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label for="password" class="form-label">Mot de passe *</label>
                  <div class="relative">
                    <input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      bind:value={formData.password}
                      class="input-field pr-12"
                      placeholder="••••••••"
                      minlength="8"
                      required
                      disabled={loading}
                    />
                    <button
                      type="button"
                      class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-500 hover:text-success transition-colors"
                      on:click={() => showPassword = !showPassword}
                      tabindex="-1"
                      aria-label="Toggle password visibility"
                    >
                      {#if showPassword}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                        </svg>
                      {:else}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      {/if}
                    </button>
                  </div>
                  
                  <!-- Password requirements checklist -->
                  {#if formData.password.length > 0}
                    <div class="mt-3 space-y-1.5">
                      <div class="flex items-center gap-2 text-sm {passwordReqs.minLength ? 'text-success' : 'text-gray-500'}">
                        <svg class="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="{passwordReqs.minLength ? 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z' : 'M10 18a8 8 0 100-16 8 8 0 000 16z'}" clip-rule="evenodd" />
                        </svg>
                        <span class="{passwordReqs.minLength ? 'font-medium' : ''}">Au moins 8 caractères</span>
                      </div>
                      <div class="flex items-center gap-2 text-sm {passwordReqs.hasUpper ? 'text-success' : 'text-gray-500'}">
                        <svg class="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="{passwordReqs.hasUpper ? 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z' : 'M10 18a8 8 0 100-16 8 8 0 000 16z'}" clip-rule="evenodd" />
                        </svg>
                        <span class="{passwordReqs.hasUpper ? 'font-medium' : ''}">Une lettre majuscule</span>
                      </div>
                      <div class="flex items-center gap-2 text-sm {passwordReqs.hasLower ? 'text-success' : 'text-gray-500'}">
                        <svg class="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="{passwordReqs.hasLower ? 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z' : 'M10 18a8 8 0 100-16 8 8 0 000 16z'}" clip-rule="evenodd" />
                        </svg>
                        <span class="{passwordReqs.hasLower ? 'font-medium' : ''}">Une lettre minuscule</span>
                      </div>
                      <div class="flex items-center gap-2 text-sm {passwordReqs.hasNumber ? 'text-success' : 'text-gray-500'}">
                        <svg class="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="{passwordReqs.hasNumber ? 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z' : 'M10 18a8 8 0 100-16 8 8 0 000 16z'}" clip-rule="evenodd" />
                        </svg>
                        <span class="{passwordReqs.hasNumber ? 'font-medium' : ''}">Un chiffre</span>
                      </div>
                    </div>
                  {/if}
                </div>

                <div>
                  <label for="confirm_password" class="form-label">Confirmer mot de passe *</label>
                  <div class="relative">
                    <input
                      id="confirm_password"
                      type={showConfirmPassword ? 'text' : 'password'}
                      bind:value={confirmPassword}
                      class="input-field pr-12 {!passwordsMatch && confirmPassword ? 'border-error focus:ring-error' : ''}"
                      placeholder="••••••••"
                      minlength="8"
                      required
                      disabled={loading}
                    />
                    <button
                      type="button"
                      class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-500 hover:text-success transition-colors"
                      on:click={() => showConfirmPassword = !showConfirmPassword}
                      tabindex="-1"
                      aria-label="Toggle confirm password visibility"
                    >
                      {#if showConfirmPassword}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                        </svg>
                      {:else}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      {/if}
                    </button>
                  </div>
                  {#if !passwordsMatch && confirmPassword}
                    <p class="mt-2 text-sm text-error flex items-center gap-1">
                      <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                      </svg>
                      Les mots de passe ne correspondent pas
                    </p>
                  {:else if passwordsMatch && confirmPassword && formData.password}
                    <p class="mt-2 text-sm text-success flex items-center gap-1">
                      <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                      Les mots de passe correspondent
                    </p>
                  {/if}
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label for="phone" class="form-label">Téléphone</label>
                  <input
                    id="phone"
                    type="tel"
                    bind:value={formData.phone}
                    class="input-field"
                    placeholder="+33 6 12 34 56 78"
                    disabled={loading}
                  />
                </div>

                <div>
                  <label for="gender" class="form-label">Genre</label>
                  <select
                    id="gender"
                    bind:value={formData.gender}
                    class="input-field"
                    disabled={loading}
                  >
                    <option value="">Sélectionner...</option>
                    <option value="male">Homme</option>
                    <option value="female">Femme</option>
                    <option value="other">Autre</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="flex justify-end pt-4">
              <button type="button" on:click={handleNextStep} class="btn-success btn-lg animate-slide-in-right" disabled={loading}>
                <span class="flex items-center justify-center gap-2">
                  Suivant
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </button>
            </div>
          {/if}

          {#if currentStep === 2}
            <!-- Step 2: Professional Information -->
            <div class="space-y-5 animate-fade-in">
              <div class="relative mb-6 p-4 rounded-2xl bg-gradient-to-r from-teal-50 via-cyan-50 to-teal-50 border-l-4 border-accent-emerald">
                <div class="flex items-center gap-4">
                  <div class="w-14 h-14 rounded-xl flex items-center justify-center bg-gradient-to-br from-accent-emerald to-success-dark shadow-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-2xl font-bold text-success-dark">Informations professionnelles</h3>
                    <p class="text-sm text-success mt-1">Complétez votre profil médical</p>
                  </div>
                </div>
              </div>

              <div>
                <label for="specialization" class="form-label">Spécialisation *</label>
                <input
                  id="specialization"
                  type="text"
                  bind:value={formData.specialization}
                  class="input-field"
                  placeholder="Cardiologie, Pédiatrie, Médecine Générale..."
                  required
                  disabled={loading}
                />
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label for="consultation_fee" class="form-label">Tarif consultation</label>
                  <input
                    id="consultation_fee"
                    type="number"
                    bind:value={formData.consultation_fee}
                    class="input-field"
                    placeholder="5000"
                    min="0"
                    disabled={loading}
                  />
                  <p class="form-helper">💶 En centimes (ex: 5000 = 50€)</p>
                </div>

                <div>
                  <label for="languages_spoken" class="form-label">Langues parlées</label>
                  <input
                    id="languages_spoken"
                    type="text"
                    bind:value={formData.languages_spoken}
                    class="input-field"
                    placeholder="Français, Anglais, Espagnol"
                    disabled={loading}
                  />
                </div>
              </div>

              <div>
                <label for="bio" class="form-label">Biographie professionnelle</label>
                <textarea
                  id="bio"
                  bind:value={formData.bio}
                  class="input-field"
                  placeholder="Parlez-nous de votre parcours, vos qualifications, votre expérience..."
                  rows="5"
                  disabled={loading}
                ></textarea>
                <p class="form-helper">Maximum 2000 caractères</p>
              </div>
            </div>

            <div class="flex gap-4 pt-4">
              <button type="button" on:click={prevStep} class="btn-outline flex-1 animate-slide-in-left" disabled={loading}>
                <span class="flex items-center justify-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 17l-5-5m0 0l5-5m-5 5h12" />
                  </svg>
                  Précédent
                </span>
              </button>
              <button type="submit" class="btn-success flex-1 btn-lg {loading ? 'animate-pulse' : 'animate-slide-in-right'}" disabled={loading}>
                {#if loading}
                  <span class="flex items-center justify-center gap-2">
                    <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Inscription en cours...
                  </span>
                {:else}
                  <span class="flex items-center justify-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Créer mon compte
                  </span>
                {/if}
              </button>
            </div>
          {/if}
        </form>

        <!-- Login Link -->
        <div class="divider"></div>
        <div class="text-center">
          <p class="text-gray-600">
            Déjà inscrit ?
            <button type="button" on:click={() => navigate('/login')} class="font-semibold text-primary-600 hover:text-primary-700 underline decoration-2 underline-offset-2 transition-colors">
              Se connecter →
            </button>
          </p>
        </div>
      </div>
    {/if}

    <!-- Back to Home -->
    <div class="text-center mt-8">
      <button 
        type="button" 
        on:click={() => navigate('/')} 
        class="inline-flex items-center gap-2 text-gray-700 hover:text-primary-700 font-medium transition-all hover:gap-3"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Retour à l'accueil
      </button>
    </div>
  </div>
</div>