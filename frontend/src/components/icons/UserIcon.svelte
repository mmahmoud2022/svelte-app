<script lang="ts">
  export let size: string = '24';
  export let color: string = 'currentColor';
  export let className: string = '';
  export let ariaLabel: string = 'User icon';
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
    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
  />
</svg>
