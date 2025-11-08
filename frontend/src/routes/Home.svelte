<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from '../lib/router';
  import { getStatistics } from '../lib/api';
  import type { StatisticsResponse } from '../lib/api';
  import HeroSection from '../components/sections/HeroSection.svelte';
  import StatisticsSection from '../components/sections/StatisticsSection.svelte';
  import FeaturesSection from '../components/sections/FeaturesSection.svelte';
  import '../styles/home.css';

  let statistics: StatisticsResponse | null = null;
  let loading = true;
  let error: string | null = null;

  onMount(async () => {
    try {
      statistics = await getStatistics();
    } catch (err: any) {
      error = err.response?.data?.detail || 'Erreur lors du chargement des statistiques';
    } finally {
      loading = false;
    }
  });

  const handlePatientRegister = () => navigate('/register/patient');
  const handleDoctorRegister = () => navigate('/register/doctor');
  const handleLogin = () => navigate('/login');
</script>

<div class="min-h-screen hero-section" style="background: var(--gradient-hero-bg);">
  <HeroSection 
    onPatientRegister={handlePatientRegister}
    onDoctorRegister={handleDoctorRegister}
    onLogin={handleLogin}
  />

  <StatisticsSection 
    {statistics}
    {loading}
    {error}
  />

  <FeaturesSection />
</div>
