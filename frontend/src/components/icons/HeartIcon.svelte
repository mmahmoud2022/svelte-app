<script lang="ts">
  export let size: string = '24';
  export let color: string = 'currentColor';
  export let className: string = '';
  export let ariaLabel: string = 'Heart icon';
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
    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
  />
</svg>
