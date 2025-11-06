<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    getDoctorPayments,
    type Payment,
    type PaymentStatus
  } from '../../lib/api-doctor';
  
  let payments: Payment[] = [];
  let loading = true;
  let error: string | null = null;
  let filterStatus: PaymentStatus | 'all' = 'all';
  
  // Statistics
  let totalRevenue = 0;
  let pendingRevenue = 0;
  let completedRevenue = 0;
  let refundedAmount = 0;
  
  // Monthly revenue (last 6 months)
  let monthlyRevenue: { month: string; amount: number }[] = [];

  onMount(async () => {
    await loadPayments();
  });

  const loadPayments = async () => {
    loading = true;
    error = null;
    try {
      const status = filterStatus === 'all' ? undefined : filterStatus;
      const response = await getDoctorPayments(1, 100, status);
      payments = response.items || [];
      
      calculateStatistics();
    } catch (err: any) {
      console.error('Error loading payments:', err);
      error = 'Erreur lors du chargement des paiements';
    } finally {
      loading = false;
    }
  };

  const calculateStatistics = () => {
    totalRevenue = 0;
    pendingRevenue = 0;
    completedRevenue = 0;
    refundedAmount = 0;
    
    const monthlyData: Record<string, number> = {};
    
    payments.forEach(payment => {
      if (payment.status === 'completed') {
        totalRevenue += payment.amount;
        completedRevenue += payment.amount;
        
        const date = new Date(payment.paid_at || payment.created_at);
        const monthKey = date.toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' });
        monthlyData[monthKey] = (monthlyData[monthKey] || 0) + payment.amount;
      } else if (payment.status === 'pending') {
        pendingRevenue += payment.amount;
      } else if (payment.status === 'refunded') {
        refundedAmount += payment.amount;
      }
    });
    
    monthlyRevenue = Object.entries(monthlyData)
      .map(([month, amount]) => ({ month, amount }))
      .slice(-6);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount / 100);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'refunded': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending': return 'En attente';
      case 'completed': return 'Complété';
      case 'failed': return 'Échoué';
      case 'refunded': return 'Remboursé';
      default: return status;
    }
  };

  const getPaymentIcon = (method: string) => {
    switch (method?.toLowerCase()) {
      case 'card':
      case 'credit_card':
        return '💳';
      case 'cash':
        return '💵';
      case 'check':
        return '📝';
      case 'transfer':
        return '🏦';
      default:
        return '💰';
    }
  };

  $: filteredPayments = payments;
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <h2 class="text-2xl font-bold text-gray-900">Paiements et Revenus</h2>
    <select
      bind:value={filterStatus}
      on:change={loadPayments}
      class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
    >
      <option value="all">Tous</option>
      <option value="completed">Complétés</option>
      <option value="pending">En attente</option>
      <option value="failed">Échoués</option>
      <option value="refunded">Remboursés</option>
    </select>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-emerald-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-800">{error}</p>
    </div>
  {:else}
    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-6 border border-emerald-200">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-gray-700">Revenus totaux</h3>
          <div class="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">💰</span>
          </div>
        </div>
        <p class="text-3xl font-bold text-gray-900">{formatCurrency(totalRevenue)}</p>
        <p class="text-sm text-emerald-600 mt-1">{payments.filter(p => p.status === 'completed').length} paiements</p>
      </div>

      <div class="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border border-yellow-200">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-gray-700">En attente</h3>
          <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">⏳</span>
          </div>
        </div>
        <p class="text-3xl font-bold text-gray-900">{formatCurrency(pendingRevenue)}</p>
        <p class="text-sm text-yellow-600 mt-1">{payments.filter(p => p.status === 'pending').length} en attente</p>
      </div>

      <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-gray-700">Ce mois</h3>
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">📅</span>
          </div>
        </div>
        <p class="text-3xl font-bold text-gray-900">
          {formatCurrency(
            payments
              .filter(p => {
                const date = new Date(p.created_at);
                const now = new Date();
                return date.getMonth() === now.getMonth() && 
                       date.getFullYear() === now.getFullYear() &&
                       p.status === 'completed';
              })
              .reduce((sum, p) => sum + p.amount, 0)
          )}
        </p>
        <p class="text-sm text-blue-600 mt-1">Mois en cours</p>
      </div>

      <div class="bg-gradient-to-br from-red-50 to-pink-50 rounded-xl p-6 border border-red-200">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-gray-700">Remboursements</h3>
          <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">↩️</span>
          </div>
        </div>
        <p class="text-3xl font-bold text-gray-900">{formatCurrency(refundedAmount)}</p>
        <p class="text-sm text-red-600 mt-1">{payments.filter(p => p.status === 'refunded').length} remboursements</p>
      </div>
    </div>

    <!-- Revenue Chart (Simple Bar Chart) -->
    {#if monthlyRevenue.length > 0}
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-6">Revenus des 6 derniers mois</h3>
        <div class="space-y-4">
          {#each monthlyRevenue as data}
            {@const maxAmount = Math.max(...monthlyRevenue.map(m => m.amount))}
            {@const percentage = (data.amount / maxAmount) * 100}
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">{data.month}</span>
                <span class="text-sm font-semibold text-gray-900">{formatCurrency(data.amount)}</span>
              </div>
              <div class="bg-gray-200 rounded-full h-3 overflow-hidden">
                <div 
                  class="bg-gradient-to-r from-emerald-500 to-teal-600 h-full transition-all duration-500"
                  style="width: {percentage}%"
                ></div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Payments List -->
    {#if filteredPayments.length === 0}
      <div class="text-center py-12 bg-white rounded-lg border border-gray-200">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="text-gray-600">Aucun paiement trouvé</p>
      </div>
    {:else}
      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Patient</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Méthode</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Montant</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Transaction</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              {#each filteredPayments as payment}
                <tr class="hover:bg-gray-50 transition-colors">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(payment.created_at)}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">Patient #{payment.patient_id}</div>
                    {#if payment.appointment_id}
                      <div class="text-xs text-gray-500">RDV #{payment.appointment_id}</div>
                    {/if}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {getPaymentIcon(payment.payment_method || '')}
                    {payment.payment_method || 'N/A'}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-semibold text-gray-900">
                      {formatCurrency(payment.amount)}
                    </div>
                    <div class="text-xs text-gray-500">{payment.currency}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 rounded-full text-xs font-medium {getStatusBadgeClass(payment.status)}">
                      {getStatusLabel(payment.status)}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                    {payment.transaction_id || '-'}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}
  {/if}
</div>
