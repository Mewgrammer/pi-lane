<script setup lang="ts">
import { type TileDefinition } from '../../types/track.types';
import { CELL_SIZE } from './track.utils';

const props = defineProps<{
  tile: TileDefinition;
}>();

// Size based on grid dimensions
const width = props.tile.gridWidth * CELL_SIZE;
const height = props.tile.gridHeight * CELL_SIZE;
</script>

<template>
  <img
    :src="tile.image"
    :alt="tile.name"
    :style="{ width: width + 'px', height: height + 'px' }"
    class="tile-image"
  />
</template>

<style scoped>
.tile-image {
  display: block;
  object-fit: contain;
}
</style>
