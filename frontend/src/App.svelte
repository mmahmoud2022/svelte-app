<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore } from './lib/stores/auth';
  import { router } from './lib/router';

  // Import routes
  import Home from './routes/Home.svelte';
  import Login from './routes/Login.svelte';
  import PatientRegister from './routes/patients/PatientRegister.svelte';
  import DoctorRegister from './routes/doctors/DoctorRegister.svelte';
  import DoctorDashboard from './routes/doctors/DoctorDashboard.svelte';
  import AdminLogin from './routes/admin/Login.svelte';
  import AdminRegister from './routes/admin/Register.svelte';
  import AdminDashboard from './routes/admin/AdminDashboard.svelte';

  let currentPath = '/';

  // Subscribe to route changes
  router.subscribe(path => {
    currentPath = path;
  });

  // Initialize auth store on app load
  onMount(() => {
    authStore.init();
  });

  // Simple route matching
  $: component = (() => {
    if (currentPath === '/') return Home;
    if (currentPath === '/login') return Login;
    if (currentPath === '/register/patient') return PatientRegister;
    if (currentPath === '/register/doctor') return DoctorRegister;
    if (currentPath === '/doctors/dashboard') return DoctorDashboard;
    if (currentPath === '/admin/login') return AdminLogin;
    if (currentPath === '/admin/register') return AdminRegister;
    if (currentPath === '/admin' || currentPath === '/admin/dashboard') return AdminDashboard;
    return Home; // Default fallback
  })();
</script>

<svelte:component this={component} />
