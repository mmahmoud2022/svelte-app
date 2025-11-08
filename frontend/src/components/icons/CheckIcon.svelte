<script lang="ts">
  export let size: string = '24';
  export let color: string = 'currentColor';
  export let className: string = '';
  export let ariaLabel: string = 'Check icon';
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  class={className}
  width={size}
  height={size}
  fill="none"
  viewBox="0 0 24 24"
  stroke={color}
  aria-label={ariaLabel}
  role="img"
>
  <path
    stroke-linecap="round"
    stroke-linejoin="round"
    stroke-width="2"
    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
  />
</svg>
