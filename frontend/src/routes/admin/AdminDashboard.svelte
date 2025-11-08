<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from '../../lib/router';
  import { authStore } from '../../lib/stores/auth';
  import {
    getAllUsers,
    getPendingDoctors,
    approveDoctor,
    rejectDoctor,
    suspendUser,
    activateUser,
    deleteUser,
    getStatistics,
    logout,
  } from '../../lib/api';
  import type { User, AdminActionResponse, StatisticsResponse } from '../../lib/api';
  import '../../styles/admin.css';

  let currentUser: User | null = null;
  let allUsers: User[] = [];
  let pendingDoctors: User[] = [];
  let statistics: StatisticsResponse | null = null;
  let loading = true;
  let activeTab: 'pending' | 'all-users' | 'patients' | 'doctors' = 'pending';
  let searchQuery = '';
  let showModal = false;
  let modalAction: 'suspend' | 'delete' | 'approve' | 'reject' | null = null;
  let selectedUser: User | null = null;
  let actionReason = '';
  let actionLoading = false;
  let successMessage = '';
  let errorMessage = '';

  // Subscribe to auth store
  authStore.subscribe((state) => {
    currentUser = state.user;
  });

  onMount(async () => {
    // Check if user is admin (case-insensitive comparison)
    if (!currentUser || currentUser.role.toUpperCase() !== 'ADMIN') {
      navigate('/login');
      return;
    }

    await loadData();
  });

  async function loadData() {
    loading = true;
    errorMessage = '';
    try {
      const [stats, users, pending] = await Promise.all([
        getStatistics(),
        getAllUsers(),
        getPendingDoctors(),
      ]);
      statistics = stats;
      allUsers = users;
      // Filter to ensure only doctors (not admins) are in pending list
      pendingDoctors = pending.filter((u) => u.role.toUpperCase() === 'DOCTOR');
    } catch (error: any) {
      errorMessage = error.response?.data?.detail || 'Erreur lors du chargement des données';
      console.error('Error loading admin data:', error);
    } finally {
      loading = false;
    }
  }

  function openModal(action: typeof modalAction, user: User) {
    modalAction = action;
    selectedUser = user;
    actionReason = '';
    showModal = true;
  }

  function closeModal() {
    showModal = false;
    modalAction = null;
    selectedUser = null;
    actionReason = '';
  }

  async function confirmAction() {
    if (!selectedUser || !modalAction) return;

    actionLoading = true;
    errorMessage = '';
    successMessage = '';

    try {
      let response: AdminActionResponse;

      switch (modalAction) {
        case 'approve':
          response = await approveDoctor(selectedUser.id);
          break;
        case 'reject':
          response = await rejectDoctor(selectedUser.id, actionReason || 'Rejected by admin');
          break;
        case 'suspend':
          response = await suspendUser(selectedUser.id, actionReason || 'Suspended by admin');
          break;
        case 'delete':
          response = await deleteUser(selectedUser.id);
          break;
      }

      successMessage = response!.message;
      closeModal();
      await loadData();

      // Clear success message after 5 seconds
      setTimeout(() => {
        successMessage = '';
      }, 5000);
    } catch (error: any) {
      errorMessage = error.response?.data?.detail || 'Une erreur est survenue';
    } finally {
      actionLoading = false;
    }
  }

  async function handleActivateUser(user: User) {
    actionLoading = true;
    errorMessage = '';
    successMessage = '';

    try {
      const response = await activateUser(user.id);
      successMessage = response.message;
      await loadData();

      setTimeout(() => {
        successMessage = '';
      }, 5000);
    } catch (error: any) {
      errorMessage = error.response?.data?.detail || 'Une erreur est survenue';
    } finally {
      actionLoading = false;
    }
  }

  async function handleLogout() {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/login');
    }
  }

  // Filter users based on active tab and search query
  $: filteredUsers = (() => {
    let users: User[] = [];

    switch (activeTab) {
      case 'pending':
        users = pendingDoctors;
        break;
      case 'all-users':
        users = allUsers;
        break;
      case 'patients':
        users = allUsers.filter((u) => u.role.toUpperCase() === 'PATIENT');
        break;
      case 'doctors':
        users = allUsers.filter((u) => u.role.toUpperCase() === 'DOCTOR');
        break;
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      users = users.filter(
        (u) =>
          u.email.toLowerCase().includes(query) ||
          u.full_name.toLowerCase().includes(query)
      );
    }

    return users;
  })();
</script>

<div class="admin-container">
  <!-- Header -->
  <header class="admin-header">
    <div class="admin-header-content">
      <div>
        <h1 class="admin-title">👨‍⚕️ Administration</h1>
        <p class="admin-subtitle">
          Bienvenue, {currentUser?.full_name || 'Admin'}
        </p>
      </div>
      <div class="admin-header-actions">
        <button class="btn btn-outline" on:click={() => navigate('/dashboard')}>
          Dashboard
        </button>
        <button class="btn btn-danger" on:click={handleLogout}>
          Déconnexion
        </button>
      </div>
    </div>
  </header>

  <main class="admin-main">
    <!-- Success/Error Messages -->
    {#if successMessage}
      <div class="alert alert-success animate-scale-in" style="margin-bottom: 1.5rem;">
        <span class="alert-icon">✓</span>
        <div>
          <strong>Succès</strong>
          <p>{successMessage}</p>
        </div>
      </div>
    {/if}

    {#if errorMessage}
      <div class="alert alert-error animate-scale-in" style="margin-bottom: 1.5rem;">
        <span class="alert-icon">✕</span>
        <div>
          <strong>Erreur</strong>
          <p>{errorMessage}</p>
        </div>
      </div>
    {/if}

    <!-- Statistics Cards -->
    {#if statistics}
      <div class="dashboard-stats">
        <div class="stat-card-admin primary">
          <div class="stat-icon primary">
            <span>👥</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">Total Utilisateurs</div>
            <div class="stat-value">{statistics.total_users}</div>
          </div>
        </div>

        <div class="stat-card-admin success">
          <div class="stat-icon success">
            <span>👨‍⚕️</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">Médecins</div>
            <div class="stat-value">{statistics.total_doctors}</div>
          </div>
        </div>

        <div class="stat-card-admin info">
          <div class="stat-icon info">
            <span>🏥</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">Patients</div>
            <div class="stat-value">{statistics.total_patients}</div>
          </div>
        </div>

        <div class="stat-card-admin warning">
          <div class="stat-icon warning">
            <span>⏳</span>
          </div>
          <div class="stat-content">
            <div class="stat-label">En Attente</div>
            <div class="stat-value">{statistics.pending_doctors}</div>
          </div>
        </div>
      </div>
    {/if}

    <!-- Tabs -->
    <div class="admin-tabs">
      <button
        class="admin-tab"
        class:active={activeTab === 'pending'}
        on:click={() => (activeTab = 'pending')}
      >
        ⏳ Médecins en attente ({pendingDoctors.length})
      </button>
      <button
        class="admin-tab"
        class:active={activeTab === 'all-users'}
        on:click={() => (activeTab = 'all-users')}
      >
        👥 Tous les utilisateurs ({allUsers.length})
      </button>
      <button
        class="admin-tab"
        class:active={activeTab === 'patients'}
        on:click={() => (activeTab = 'patients')}
      >
        🏥 Patients ({allUsers.filter((u) => u.role.toUpperCase() === 'PATIENT').length})
      </button>
      <button
        class="admin-tab"
        class:active={activeTab === 'doctors'}
        on:click={() => (activeTab = 'doctors')}
      >
        👨‍⚕️ Médecins ({allUsers.filter((u) => u.role.toUpperCase() === 'DOCTOR').length})
      </button>
    </div>

    <!-- Users Table -->
    <div class="users-table-container">
      <div class="users-table-header">
        <h2 class="users-table-title">
          {#if activeTab === 'pending'}
            Médecins en attente d'approbation
          {:else if activeTab === 'all-users'}
            Tous les utilisateurs
          {:else if activeTab === 'patients'}
            Patients
          {:else}
            Médecins
          {/if}
        </h2>
        <div class="users-table-actions">
          <input
            type="text"
            class="search-input"
            placeholder="Rechercher par email ou nom..."
            bind:value={searchQuery}
          />
          <button class="btn btn-primary" on:click={loadData}>
            🔄 Actualiser
          </button>
        </div>
      </div>

      <div class="users-table">
        {#if loading}
          <div class="loading-spinner">
            <div class="spinner"></div>
          </div>
        {:else if filteredUsers.length === 0}
          <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <h3 class="empty-state-title">Aucun utilisateur trouvé</h3>
            <p class="empty-state-text">
              {searchQuery
                ? 'Aucun résultat pour votre recherche'
                : 'Aucun utilisateur dans cette catégorie'}
            </p>
          </div>
        {:else}
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nom</th>
                <th>Email</th>
                <th>Rôle</th>
                <th>Statut</th>
                <th>Vérifié</th>
                <th>Créé le</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each filteredUsers as user (user.id)}
                <tr>
                  <td>{user.id}</td>
                  <td>{user.full_name}</td>
                  <td>{user.email}</td>
                  <td>
                    <span class="role-badge {user.role.toLowerCase()}">
                      {user.role}
                    </span>
                  </td>
                  <td>
                    <span class="badge {user.is_active ? 'success' : 'danger'}">
                      {user.is_active ? 'Actif' : 'Suspendu'}
                    </span>
                  </td>
                  <td>
                    <span class="badge {user.email_verified ? 'success' : 'warning'}">
                      {user.email_verified ? 'Oui' : 'Non'}
                    </span>
                  </td>
                  <td>{new Date(user.created_at).toLocaleDateString('fr-FR')}</td>
                  <td>
                    <div class="action-buttons">
                      {#if activeTab === 'pending' && user.role.toUpperCase() === 'DOCTOR' && !user.admin_approved}
                        <button
                          class="action-btn approve"
                          on:click={() => openModal('approve', user)}
                        >
                          ✓ Approuver
                        </button>
                        <button
                          class="action-btn reject"
                          on:click={() => openModal('reject', user)}
                        >
                          ✕ Rejeter
                        </button>
                      {:else}
                        {#if user.is_active && user.role.toUpperCase() !== 'ADMIN'}
                          <button
                            class="action-btn suspend"
                            on:click={() => openModal('suspend', user)}
                          >
                            ⏸ Suspendre
                          </button>
                        {/if}
                        {#if !user.is_active}
                          <button
                            class="action-btn activate"
                            on:click={() => handleActivateUser(user)}
                            disabled={actionLoading}
                          >
                            ▶ Activer
                          </button>
                        {/if}
                        {#if user.role.toUpperCase() !== 'ADMIN'}
                          <button
                            class="action-btn delete"
                            on:click={() => openModal('delete', user)}
                          >
                            🗑 Supprimer
                          </button>
                        {/if}
                      {/if}
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        {/if}
      </div>
    </div>
  </main>
</div>

<!-- Modal -->
{#if showModal && selectedUser}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="modal-overlay" on:click={closeModal}>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h3 class="modal-title">
          {#if modalAction === 'approve'}
            Approuver le médecin
          {:else if modalAction === 'reject'}
            Rejeter le médecin
          {:else if modalAction === 'suspend'}
            Suspendre l'utilisateur
          {:else if modalAction === 'delete'}
            Supprimer l'utilisateur
          {/if}
        </h3>
      </div>

      <div class="modal-body">
        <div class="user-detail-row">
          <span class="user-detail-label">Nom:</span>
          <span class="user-detail-value">{selectedUser.full_name}</span>
        </div>
        <div class="user-detail-row">
          <span class="user-detail-label">Email:</span>
          <span class="user-detail-value">{selectedUser.email}</span>
        </div>
        <div class="user-detail-row">
          <span class="user-detail-label">Rôle:</span>
          <span class="user-detail-value">{selectedUser.role}</span>
        </div>

        {#if modalAction === 'reject' || modalAction === 'suspend'}
          <div style="margin-top: 1.5rem;">
            <label class="form-label" for="actionReason">
              {modalAction === 'reject' ? 'Raison du rejet' : 'Raison de la suspension'}
              {modalAction === 'suspend' ? '(requis)' : '(optionnel)'}
            </label>
            <textarea
              id="actionReason"
              class="form-input"
              rows="3"
              bind:value={actionReason}
              placeholder="Entrez la raison..."
            ></textarea>
          </div>
        {/if}

        {#if modalAction === 'approve'}
          <p style="margin-top: 1rem; color: #065f46;">
            ✓ Ce médecin sera approuvé et pourra se connecter à la plateforme.
          </p>
        {:else if modalAction === 'delete'}
          <p style="margin-top: 1rem; color: #991b1b; font-weight: 600;">
            ⚠️ Attention : Cette action est irréversible. L'utilisateur sera définitivement
            supprimé de la base de données.
          </p>
        {/if}

        {#if errorMessage}
          <div class="alert alert-error" style="margin-top: 1rem;">
            <span class="alert-icon">✕</span>
            <p>{errorMessage}</p>
          </div>
        {/if}
      </div>

      <div class="modal-footer">
        <button class="btn btn-outline" on:click={closeModal} disabled={actionLoading}>
          Annuler
        </button>
        <button
          class="btn btn-{modalAction === 'approve' ? 'success' : 'danger'}"
          on:click={confirmAction}
          disabled={actionLoading || (modalAction === 'suspend' && !actionReason)}
        >
          {#if actionLoading}
            Traitement...
          {:else if modalAction === 'approve'}
            Approuver
          {:else if modalAction === 'reject'}
            Rejeter
          {:else if modalAction === 'suspend'}
            Suspendre
          {:else if modalAction === 'delete'}
            Supprimer
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}
