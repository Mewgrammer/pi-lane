<script setup lang="ts">
import { computed } from 'vue';
import { type TileDefinition } from '../../types/track.types';

const props = defineProps<{
  tile: TileDefinition;
  connectedSides?: string[];
}>();

const connectedSides = computed(() => props.connectedSides ?? []);
const isCorner = computed(() => props.tile.type === 'corner');
const isStart = computed(() => props.tile.type === 'start-finish');
</script>

<style scoped>
.tile-svg {
  width: 100%;
  height: 100%;
}
</style>
<template>
  <svg viewBox="0 0 60 60" class="tile-svg">
    <!-- Background -->
    <rect x="1" y="1" width="58" height="58" fill="#2a2a35" rx="4" />

    <!-- Track surface -->
    <path
      v-if="isCorner"
      d="M 40 -50 A 10 10 90 0 0 50 -40 L 50 -10 A 40 40 90 0 1 10 -50 Z"
      fill="#222228"
    />
    <rect v-else x="0" y="15" width="60" height="30" fill="#222228" />

    <!-- Type indicator -->
    <text v-if="isStart" x="30" y="35" text-anchor="middle" fill="#888" font-size="14">S/F</text>
    <text v-else-if="isCorner" x="35" y="45" text-anchor="middle" fill="#666" font-size="16">
      {{ tile.curveAngle ?? '?' }}°
    </text>

    <!-- Connectors (right entry) -->
    <circle cx="58" cy="30" r="5" :fill="connectedSides.includes('right') ? '#0f8' : '#666'" />

    <!-- Left/Top exit depending on type -->
    <circle
      v-if="isCorner"
      cx="30"
      cy="2"
      r="5"
      :fill="connectedSides.includes('top') ? '#0f8' : '#666'"
    />
    <circle v-else cx="2" cy="30" r="5" :fill="connectedSides.includes('left') ? '#0f8' : '#666'" />
  </svg>
</template>
