<script lang="ts">
  import HeartIcon from '../icons/HeartIcon.svelte';
  
  export let title: string = 'Plateforme Médicale';
  export let subtitle: string = 'Connectez-vous avec des professionnels de santé qualifiés';
  export let onPatientRegister: () => void;
  export let onDoctorRegister: () => void;
  export let onLogin: () => void;
</script>

<header class="hero-section">
  <div class="max-w-6xl mx-auto text-center">
    <div class="hero-icon">
      <HeartIcon size="48" color="white" ariaLabel="Medical platform heart icon" />
    </div>
    
    <h1 class="hero-title-gradient">
      {title}
    </h1>
    
    <p class="hero-subtitle">
      {subtitle}
    </p>

    <!-- Call to Action Buttons -->
    <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
      <button 
        on:click={onPatientRegister} 
        class="btn-primary text-lg px-8 py-3"
        aria-label="S'inscrire comme patient"
      >
        S'inscrire comme Patient
      </button>
      <button 
        on:click={onDoctorRegister} 
        class="btn-outline text-lg px-8 py-3"
        aria-label="S'inscrire comme médecin"
      >
        S'inscrire comme Médecin
      </button>
    </div>

    <div class="mt-6">
      <button 
        on:click={onLogin} 
        class="text-primary-600 hover:text-primary-700 font-medium"
        aria-label="Se connecter à votre compte"
      >
        Déjà inscrit ? Connexion →
      </button>
    </div>
  </div>
</header>
