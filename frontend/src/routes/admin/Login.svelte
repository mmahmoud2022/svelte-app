<script lang="ts">
  import { navigate } from '../../lib/router';
  import { authStore } from '../../lib/stores/auth';
  import { login } from '../../lib/api';
  import type { LoginCredentials } from '../../lib/api';

  let credentials: LoginCredentials = { email: '', password: '' };
  let error: string | null = null;
  let loading = false;
  let showPassword = false;

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    error = null;

    // Validation basique
    if (!credentials.email.trim()) {
      error = 'Veuillez entrer votre adresse email administrateur.';
      return;
    }
    if (!credentials.password.trim()) {
      error = 'Veuillez entrer votre mot de passe.';
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(credentials.email)) {
      error = 'Format d\'email invalide. Exemple : admin@exemple.com';
      return;
    }

    loading = true;
    try {
      const response = await login(credentials);
      if (response.user.role.toUpperCase() !== 'ADMIN') {
        error = 'Accès refusé : réservé aux administrateurs.';
        loading = false;
        return;
      }

      authStore.login(response.access_token, response.refresh_token, response.user);
      navigate('/admin/dashboard');
    } catch (err: any) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail?.toLowerCase?.() || '';

      if (status === 401) {
        error = detail.includes('password')
          ? 'Mot de passe incorrect.'
          : 'Email ou mot de passe incorrect.';
      } else if (status === 403) {
        error = 'Votre compte administrateur est suspendu ou bloqué.';
      } else if (status === 422) {
        error = 'Données invalides. Vérifiez votre email et mot de passe.';
      } else if (status === 429) {
        error = 'Trop de tentatives. Réessayez dans quelques minutes.';
      } else if (status >= 500) {
        error = 'Erreur serveur. Veuillez réessayer plus tard.';
      } else {
        error = err.response?.data?.detail || 'Erreur de connexion. Veuillez vérifier vos informations.';
      }
      
      console.error('Login error:', err);
    } finally {
      loading = false;
    }
  };
</script>

<div class="login-page">
  <div class="card animate-fadeIn">
    <div class="logo">
      <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 24 24" stroke="white" fill="none">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    </div>

    <h1>Connexion administrateur</h1>
    <p class="subtitle">Accès réservé au personnel autorisé.</p>

    {#if error}
      <div class="alert error animate-shake">
        <svg xmlns="http://www.w3.org/2000/svg" class="alert-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <div>
          <strong>Erreur</strong>
          <p>{error}</p>
        </div>
      </div>
    {/if}

    <form on:submit={handleSubmit} class="form">
      <div class="form-group">
        <label for="email">Email</label>
        <input
          id="email"
          type="email"
          bind:value={credentials.email}
          placeholder="admin@exemple.com"
          disabled={loading}
          autocomplete="email"
          required
        />
      </div>

      <div class="form-group">
        <label for="password">Mot de passe</label>
        <div class="password-wrapper">
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            bind:value={credentials.password}
            placeholder="••••••••"
            disabled={loading}
            autocomplete="current-password"
            required
          />
          <button
            type="button"
            on:click={() => (showPassword = !showPassword)}
            class="eye-btn"
            aria-label="Afficher ou masquer le mot de passe"
            disabled={loading}
          >
            {showPassword ? '🙈' : '👁️'}
          </button>
        </div>
      </div>

      <button type="submit" class="submit-btn" disabled={loading}>
        {#if loading}
          <span class="loader"></span> Connexion en cours...
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
          </svg>
          Se connecter
        {/if}
      </button>
    </form>

    <div class="links">
      <p class="register-link">Pas encore de compte ? 
        <button type="button" on:click={() => navigate('/admin/register')} class="link">
          Créer un compte administrateur
        </button>
      </p>
      <button type="button" on:click={() => navigate('/')} class="link back">
        ← Retour à l'accueil
      </button>
    </div>
  </div>
</div>

<style>
  .login-page {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 3rem 1rem;
    background: #f9fafb;
    min-height: 100vh;
  }

  .card {
    background: white;
    border-radius: 1rem;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    padding: 2.5rem;
    max-width: 420px;
    width: 100%;
    transition: transform 0.3s ease;
  }

  .card:hover {
    transform: translateY(-3px);
  }

  .logo {
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, #f59e0b, #d97706);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.25rem;
  }

  .icon {
    width: 32px;
    height: 32px;
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
    border-radius: 0.5rem;
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .alert.error {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
  }

  .alert-icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .alert strong {
    display: block;
    margin-bottom: 0.25rem;
  }

  .alert p {
    margin: 0;
  }

  .form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  label {
    font-weight: 500;
    color: #374151;
  }

  input {
    padding: 0.65rem 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    font-size: 0.95rem;
    transition: all 0.2s ease;
  }

  input:focus {
    border-color: #f59e0b;
    box-shadow: 0 0 0 3px #fef3c7;
    outline: none;
  }

  input:disabled {
    background-color: #f3f4f6;
    cursor: not-allowed;
  }

  .password-wrapper {
    position: relative;
  }

  .eye-btn {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    font-size: 1.1rem;
    cursor: pointer;
    color: #f59e0b;
    padding: 0.25rem;
    transition: transform 0.2s ease;
  }

  .eye-btn:hover:not(:disabled) {
    transform: translateY(-50%) scale(1.1);
  }

  .eye-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .submit-btn {
    margin-top: 0.5rem;
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
    font-weight: 600;
    padding: 0.8rem;
    border: none;
    border-radius: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .submit-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #fbbf24, #d97706);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
  }

  .submit-btn:active:not(:disabled) {
    transform: translateY(0);
  }

  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-icon {
    width: 20px;
    height: 20px;
  }

  .loader {
    border: 3px solid white;
    border-top-color: transparent;
    border-radius: 50%;
    width: 1em;
    height: 1em;
    animation: spin 1s linear infinite;
  }

  .links {
    text-align: center;
    margin-top: 2rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .register-link {
    color: #6b7280;
    margin: 0;
  }

  .link {
    background: none;
    border: none;
    color: #f59e0b;
    cursor: pointer;
    font-weight: 500;
    text-decoration: none;
    transition: color 0.2s ease;
  }

  .link:hover {
    color: #d97706;
    text-decoration: underline;
  }

  .link.back {
    color: #374151;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
  }

  .link.back:hover {
    color: #111827;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .animate-fadeIn {
    animation: fadeIn 0.4s ease forwards;
  }

  .animate-shake {
    animation: shake 0.35s ease;
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-6px); }
    75% { transform: translateX(6px); }
  }
</style>
