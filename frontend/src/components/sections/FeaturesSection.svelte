<script lang="ts">
  import ClockIcon from '../icons/ClockIcon.svelte';
  import ShieldIcon from '../icons/ShieldIcon.svelte';
  import TeamIcon from '../icons/TeamIcon.svelte';
  
  export let title: string = 'Pourquoi Nous Choisir ?';
  export let subtitle: string = 'Une plateforme moderne conçue pour votre bien-être';
  
  interface Feature {
    iconType: 'clock' | 'shield' | 'team';
    iconClass: string;
    title: string;
    description: string;
  }
  
  export let features: Feature[] = [
    {
      iconType: 'clock',
      iconClass: 'feature-icon-primary',
      title: 'Disponibilité 24/7',
      description: 'Accédez aux services médicaux à tout moment, où que vous soyez.'
    },
    {
      iconType: 'shield',
      iconClass: 'feature-icon-emerald',
      title: 'Sécurisé & Confidentiel',
      description: 'Vos données médicales sont protégées avec les normes les plus élevées.'
    },
    {
      iconType: 'team',
      iconClass: 'feature-icon-lavender',
      title: 'Médecins Qualifiés',
      description: 'Tous nos médecins sont vérifiés et approuvés par notre équipe.'
    }
  ];
</script>

<section class="features-section">
  <div class="max-w-6xl mx-auto">
    <div class="section-header">
      <h2 class="section-title">
        {title}
      </h2>
      <p class="section-subtitle">
        {subtitle}
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      {#each features as feature}
        <article class="feature-card hover-lift">
          <div class="feature-icon {feature.iconClass}">
            {#if feature.iconType === 'clock'}
              <ClockIcon size="40" color="white" ariaLabel={`${feature.title} icon`} />
            {:else if feature.iconType === 'shield'}
              <ShieldIcon size="40" color="white" ariaLabel={`${feature.title} icon`} />
            {:else if feature.iconType === 'team'}
              <TeamIcon size="40" color="white" ariaLabel={`${feature.title} icon`} />
            {/if}
          </div>
          <h3 class="feature-title">{feature.title}</h3>
          <p class="feature-description">{feature.description}</p>
        </article>
      {/each}
    </div>
  </div>
</section>
