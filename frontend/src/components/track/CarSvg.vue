<script setup lang="ts">
defineProps<{
  color?: string;
  number?: number;
}>();

const width = 24;
const height = 20;
</script>
<template>
  <svg :width="width" :height="height" :viewBox="`0 0 ${width} ${height}`" class="car-svg">
    <!-- Car body -->
    <rect x="2" y="4" :width="width - 4" height="12" :fill="color" rx="3" />

    <!-- Cockpit -->
    <rect x="8" y="6" width="8" height="8" fill="#222" rx="2" />

    <!-- Front wheel wells -->
    <ellipse :cx="width - 6" cy="4" rx="3" ry="2" fill="#111" />
    <ellipse :cx="width - 6" cy="16" rx="3" ry="2" fill="#111" />

    <!-- Rear wheel wells -->
    <ellipse cx="6" cy="4" rx="3" ry="2" fill="#111" />
    <ellipse cx="6" cy="16" rx="3" ry="2" fill="#111" />

    <!-- Racing stripe -->
    <rect x="2" y="9" :width="width - 4" height="2" fill="#fff" opacity="0.3" />

    <!-- Number circle -->
    <circle :cx="width / 2 + 6" cy="10" r="4" fill="#fff" />
    <text
      :x="width / 2 + 6"
      y="13"
      text-anchor="middle"
      font-size="6"
      font-weight="bold"
      fill="#000"
    >
      {{ number }}
    </text>
  </svg>
</template>

<style scoped>
.car-svg {
  filter: drop-shadow(1px 1px 2px rgba(0, 0, 0, 0.5));
}
</style>
