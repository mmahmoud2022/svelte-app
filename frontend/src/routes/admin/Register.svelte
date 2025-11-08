<script lang="ts">
  import { navigate } from '../../lib/router';
  import { registerAdmin } from '../../lib/api';
  import type { AdminRegistrationData } from '../../lib/api';
  import '../../styles/login.css';

  let formData: AdminRegistrationData = {
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone: '',
    admin_secret: '',
  };

  let confirmPassword = '';
  let error: string | null = null;
  let success: string | null = null;
  let loading = false;
  let showPassword = false;
  let showConfirmPassword = false;
  let showAdminSecret = false;
  let passwordStrength = 0;

  // Password requirements tracking
  $: passwordReqs = {
    minLength: formData.password.length >= 8,
    hasUpper: /[A-Z]/.test(formData.password),
    hasLower: /[a-z]/.test(formData.password),
    hasNumber: /[0-9]/.test(formData.password),
  };

  $: allPasswordReqsMet = Object.values(passwordReqs).every(Boolean);

  const handlePasswordInput = () => {
    const value = formData.password;
    const score = [/.{8,}/, /[A-Z]/, /[a-z]/, /[0-9]/].reduce(
      (acc, regex) => acc + Number(regex.test(value)),
      0
    );
    passwordStrength = score;
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    error = null;
    success = null;

    // Validate password requirements
    if (!allPasswordReqsMet) {
      error = 'Le mot de passe ne respecte pas tous les critères requis.';
      return;
    }

    if (formData.password !== confirmPassword) {
      error = 'Les mots de passe ne correspondent pas.';
      return;
    }
    if (!formData.admin_secret) {
      error = 'Le secret administrateur est requis.';
      return;
    }

    loading = true;
    try {
      await registerAdmin(formData);
      success = 'Compte administrateur créé avec succès ! Redirection...';
      setTimeout(() => navigate('/admin/login'), 2000);
    } catch (err: any) {
      if (err.response?.status === 403) error = 'Secret administrateur invalide.';
      else if (err.response?.status === 422) {
        // Better handling of validation errors
        const details = err.response?.data?.detail;
        if (Array.isArray(details) && details.length > 0) {
          error = details[0].msg || 'Erreur de validation du formulaire.';
        } else {
          error = 'Erreur de validation. Vérifiez tous les champs.';
        }
      }
      else if (err.response?.status === 400)
        error = err.response.data?.detail || 'Email déjà enregistré.';
      else error = 'Erreur lors de la création du compte.';
    } finally {
      loading = false;
    }
  };
</script>

<div class="register-page">
  <div class="card">
    <div class="logo">
      <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" fill="none" stroke="white">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    </div>

    <h1>Création d’un compte administrateur</h1>
    <p class="subtitle">Veuillez remplir les informations ci-dessous.</p>

    {#if success}
      <div class="alert success">{success}</div>
    {/if}

    {#if error}
      <div class="alert error">{error}</div>
    {/if}

    <form on:submit={handleSubmit} class="form">
      <div class="grid">
        <div>
          <label for="email">Email *</label>
          <input id="email" type="email" bind:value={formData.email} required placeholder="admin@example.com" />
        </div>
        <div>
          <label for="first_name">Prénom *</label>
          <input id="first_name" type="text" bind:value={formData.first_name} required placeholder="Prénom" />
        </div>
        <div>
          <label for="last_name">Nom *</label>
          <input id="last_name" type="text" bind:value={formData.last_name} required placeholder="Nom" />
        </div>
        <div>
          <label for="phone">Téléphone</label>
          <input id="phone" type="tel" bind:value={formData.phone} placeholder="+33 6 12 34 56 78" />
        </div>
      </div>

      <div>
        <label for="password">Mot de passe *</label>
        <div class="password-wrapper">
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            bind:value={formData.password}
            on:input={handlePasswordInput}
            placeholder="Entrez un mot de passe sécurisé"
            required
          />
          <button type="button" on:click={() => (showPassword = !showPassword)} class="icon-btn" aria-label="Toggle password visibility">
            {showPassword ? '🙈' : '👁️'}
          </button>
        </div>

        <!-- Password requirements checklist -->
        {#if formData.password.length > 0}
          <div class="password-requirements">
            <div class="req-item" class:met={passwordReqs.minLength}>
              {passwordReqs.minLength ? '✓' : '○'} Au moins 8 caractères
            </div>
            <div class="req-item" class:met={passwordReqs.hasUpper}>
              {passwordReqs.hasUpper ? '✓' : '○'} Une lettre majuscule
            </div>
            <div class="req-item" class:met={passwordReqs.hasLower}>
              {passwordReqs.hasLower ? '✓' : '○'} Une lettre minuscule
            </div>
            <div class="req-item" class:met={passwordReqs.hasNumber}>
              {passwordReqs.hasNumber ? '✓' : '○'} Un chiffre
            </div>
          </div>
        {/if}

        <!-- indicateur de force -->
        <div class="strength-bar">
          <div class="bar" class:strong={passwordStrength === 4} style="width: {passwordStrength * 25}%;"></div>
        </div>
      </div>

      <div>
        <label for="confirm_password">Confirmer le mot de passe *</label>
        <div class="password-wrapper">
          <input
            id="confirm_password"
            type={showConfirmPassword ? 'text' : 'password'}
            bind:value={confirmPassword}
            placeholder="Répéter le mot de passe"
            required
          />
          <button type="button" on:click={() => (showConfirmPassword = !showConfirmPassword)} class="icon-btn" aria-label="Toggle confirm password visibility">
            {showConfirmPassword ? '🙈' : '👁️'}
          </button>
        </div>
        {#if confirmPassword && formData.password !== confirmPassword}
          <p class="error-hint">Les mots de passe ne correspondent pas</p>
        {/if}
      </div>

      <div class="admin-secret">
        <label for="admin_secret">Secret Administrateur *</label>
        <div class="password-wrapper">
          <input
            id="admin_secret"
            type={showAdminSecret ? 'text' : 'password'}
            bind:value={formData.admin_secret}
            placeholder="AdminSecret2025"
            required
          />
          <button type="button" on:click={() => (showAdminSecret = !showAdminSecret)} class="icon-btn" aria-label="Toggle admin secret visibility">
            {showAdminSecret ? '🙈' : '👁️'}
          </button>
        </div>
        <p class="helper">Ce secret est défini côté serveur (fichier .env): ADMIN_SECRET</p>
      </div>

      <button type="submit" class="submit-btn" disabled={loading}>
        {#if loading}
          <span class="loader"></span> Création en cours...
        {:else}
          🚀 Créer le compte
        {/if}
      </button>
    </form>

    <div class="back">
      <a href="/admin/login" on:click|preventDefault={() => navigate('/admin/login')}>
        ← Retour à la connexion
      </a>
    </div>
  </div>
</div>

<style>
  .register-page {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 3rem;
    background: #f9fafb;
  }

  .card {
    background: white;
    border-radius: 1rem;
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    padding: 2.5rem;
    width: 100%;
    max-width: 460px;
    animation: fadeIn 0.4s ease;
  }

  .logo {
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #f59e0b, #d97706);
    border-radius: 50%;
    width: 64px;
    height: 64px;
    margin: 0 auto 1rem;
  }

  h1 {
    text-align: center;
    color: #92400e;
    font-size: 1.5rem;
    margin-bottom: 0.25rem;
  }

  .subtitle {
    text-align: center;
    color: #6b7280;
    margin-bottom: 2rem;
  }

  .alert {
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }

  .alert.success {
    background: #ecfdf5;
    color: #065f46;
  }

  .alert.error {
    background: #fef2f2;
    color: #991b1b;
  }

  .form .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .form input {
    width: 100%;
    padding: 0.6rem 0.75rem;
    border-radius: 0.5rem;
    border: 1px solid #d1d5db;
    font-size: 0.95rem;
    transition: all 0.2s ease;
  }

  .form input:focus {
    border-color: #f59e0b;
    outline: none;
    box-shadow: 0 0 0 2px #fef3c7;
  }

  .password-wrapper {
    display: flex;
    align-items: center;
    position: relative;
  }

  .password-wrapper input {
    flex: 1;
  }

  .icon-btn {
    position: absolute;
    right: 8px;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.1rem;
  }

  .strength-bar {
    height: 4px;
    background: #e5e7eb;
    border-radius: 4px;
    margin-top: 0.4rem;
  }

  .strength-bar .bar {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #ef4444, #f59e0b, #10b981);
    transition: width 0.3s ease;
  }

  .strength-bar .bar.strong {
    background: #10b981;
  }

  .password-requirements {
    margin-top: 0.5rem;
    font-size: 0.85rem;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.25rem;
  }

  .req-item {
    color: #6b7280;
    transition: color 0.2s ease;
  }

  .req-item.met {
    color: #10b981;
    font-weight: 500;
  }

  .error-hint {
    color: #ef4444;
    font-size: 0.85rem;
    margin-top: 0.25rem;
  }

  .admin-secret {
    margin-top: 1rem;
  }

  .helper {
    font-size: 0.8rem;
    color: #92400e;
    margin-top: 0.25rem;
  }

  .submit-btn {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
    width: 100%;
    padding: 0.8rem;
    border: none;
    border-radius: 0.75rem;
    margin-top: 1.5rem;
    cursor: pointer;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: background 0.3s ease;
  }

  .submit-btn:hover {
    background: linear-gradient(135deg, #fbbf24, #d97706);
  }

  .loader {
    border: 3px solid #fff;
    border-top: 3px solid transparent;
    border-radius: 50%;
    width: 1em;
    height: 1em;
    animation: spin 1s linear infinite;
  }

  .back {
    text-align: center;
    margin-top: 1.25rem;
  }

  .back a {
    color: #92400e;
    font-weight: 500;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
