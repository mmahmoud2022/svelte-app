<script lang="ts">
  export let size: string = '24';
  export let color: string = 'currentColor';
  export let className: string = '';
  export let ariaLabel: string = 'Team icon';
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
    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
  />
</svg>
