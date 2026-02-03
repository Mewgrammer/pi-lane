<script setup lang="ts">
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useTrackEditorStore } from '../../stores/track-editor-store';
import { CELL_SIZE } from './track.utils';
import TileRenderer from './TileRenderer.vue';
import type { PlacedTile } from 'src/types/track.types';

const $q = useQuasar();
const store = useTrackEditorStore();
const canvasRef = ref<HTMLElement | null>(null);

function getTileStyle(placed: PlacedTile) {
  const tileDef = store.getTileById(placed.tileId);
  const gw = tileDef?.gridWidth ?? 1;
  const gh = tileDef?.gridHeight ?? 1;
  return {
    left: `${placed.gridX * CELL_SIZE}px`,
    top: `${placed.gridY * CELL_SIZE}px`,
    width: `${gw * CELL_SIZE}px`,
    height: `${gh * CELL_SIZE}px`,
  };
}

const dragPreviewStyle = computed(() => {
  const tileDef = store.dragTileId ? store.getTileById(store.dragTileId) : null;
  const gw = tileDef?.gridWidth ?? 1;
  const gh = tileDef?.gridHeight ?? 1;
  return {
    left: `${store.dragGridX * CELL_SIZE}px`,
    top: `${store.dragGridY * CELL_SIZE}px`,
    width: `${gw * CELL_SIZE}px`,
    height: `${gh * CELL_SIZE}px`,
  };
});

function onPaletteDrag(event: DragEvent, tileId: string) {
  if (!event.dataTransfer) return;
  event.dataTransfer.effectAllowed = 'copy';
  event.dataTransfer.setData('text/plain', tileId);
  store.startDragFromPalette(tileId);
}

function onTileDrag(event: DragEvent, placedId: string) {
  if (!event.dataTransfer) return;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', placedId);
  store.startDragPlaced(placedId);
}

function onCanvasDragOver(event: DragEvent) {
  if (!canvasRef.value) return;
  const rect = canvasRef.value.getBoundingClientRect();
  const px = event.clientX - rect.left + canvasRef.value.scrollLeft;
  const py = event.clientY - rect.top + canvasRef.value.scrollTop;
  store.updateDragPosition(px, py);
}

function onCanvasDrop() {
  const result = store.endDrag();
  if (result.placed && result.id) {
    store.selectTile(result.id);
    $q.notify({ type: 'positive', message: 'Placed!', timeout: 500 });
  }
}

function rotateSelected() {
  if (store.selectedTileId) store.rotateTile(store.selectedTileId);
}

function deleteSelected() {
  if (store.selectedTileId) store.removeTile(store.selectedTileId);
}

function confirmClear() {
  $q.dialog({ title: 'Clear?', message: 'Remove all tiles?', cancel: true }).onOk(() =>
    store.clearTrack(),
  );
}

function saveTrack() {
  console.log(store.exportTrack());
  $q.notify({ type: 'positive', message: 'Saved!', icon: 'save' });
}
</script>

<template>
  <div class="track-editor">
    <!-- Toolbar -->
    <div class="toolbar q-pa-sm bg-grey-9 row items-center q-gutter-sm">
      <q-btn flat round icon="add" size="sm" @click="store.newTrack()">
        <q-tooltip>New Track</q-tooltip>
      </q-btn>
      <q-btn flat round icon="save" size="sm" @click="saveTrack">
        <q-tooltip>Save</q-tooltip>
      </q-btn>
      <q-btn flat round icon="delete_sweep" size="sm" color="negative" @click="confirmClear">
        <q-tooltip>Clear</q-tooltip>
      </q-btn>

      <q-separator vertical dark class="q-mx-xs" />

      <q-btn
        flat
        round
        icon="rotate_right"
        size="sm"
        :disable="!store.selectedTileId"
        @click="rotateSelected"
      >
        <q-tooltip>Rotate 90°</q-tooltip>
      </q-btn>
      <q-btn
        flat
        round
        icon="delete"
        size="sm"
        color="negative"
        :disable="!store.selectedTileId"
        @click="deleteSelected"
      >
        <q-tooltip>Delete</q-tooltip>
      </q-btn>

      <q-separator vertical dark class="q-mx-xs" />

      <q-toggle v-model="store.showGrid" label="Grid" dark dense size="sm" />

      <q-space />

      <q-input
        v-model="store.currentTrack.name"
        dense
        filled
        dark
        label="Track"
        style="width: 150px"
      />
    </div>

    <div class="editor-body row">
      <!-- Palette -->
      <div class="palette q-pa-xs bg-grey-10">
        <div class="text-caption text-grey-6 q-mb-xs">Tiles</div>
        <div
          v-for="tile in store.availableTiles"
          :key="tile.id"
          class="palette-tile q-mb-xs"
          draggable="true"
          @dragstart="onPaletteDrag($event, tile.id)"
          @dragend="store.cancelDrag()"
        >
          <div class="tile-icon" :class="tile.type">
            <span v-if="tile.type === 'corner'">↱</span>
            <span v-else-if="tile.type === 'start-finish'">S</span>
            <span v-else>—</span>
          </div>
          <div class="tile-name">{{ tile.name }}</div>
        </div>
      </div>

      <!-- Canvas -->
      <div
        ref="canvasRef"
        class="canvas"
        :class="{ 'show-grid': store.showGrid }"
        @dragover.prevent="onCanvasDragOver"
        @drop="onCanvasDrop"
        @click="store.selectTile(null)"
      >
        <!-- Placed tiles -->
        <div
          v-for="placed in store.currentTrack.tiles"
          :key="placed.id"
          class="placed-tile"
          :class="{
            selected: placed.id === store.selectedTileId,
            disconnected: !store.isPlacedConnected(placed.id),
          }"
          :style="getTileStyle(placed)"
          draggable="true"
          @dragstart="onTileDrag($event, placed.id)"
          @dragend="store.cancelDrag()"
          @click.stop="store.selectTile(placed.id)"
        >
          <q-tooltip>
            {{ store.getTileById(placed.tileId)?.name }}
            <span v-if="!store.isPlacedConnected(placed.id)" class="text-negative">
              - Disconnected
            </span>
          </q-tooltip>

          <div class="tile-inner" :style="{ transform: `rotate(${placed.rotation}deg)` }">
            <TileRenderer
              v-if="store.getTileById(placed.tileId)"
              :tile="store.getTileById(placed.tileId)!"
            />
          </div>
        </div>

        <!-- Drag preview -->
        <div
          v-if="store.isDragging && store.dragTileId"
          class="drag-preview"
          :class="{ invalid: !store.dragValid }"
          :style="dragPreviewStyle"
        >
          <div class="tile-inner" :style="{ transform: `rotate(${store.dragRotation}deg)` }">
            <TileRenderer
              v-if="store.getTileById(store.dragTileId)"
              :tile="store.getTileById(store.dragTileId)!"
            />
          </div>
        </div>

        <!-- Empty state -->
        <div
          v-if="store.currentTrack.tiles.length === 0 && !store.isDragging"
          class="empty-state text-grey-6"
        >
          <q-icon name="edit_road" size="40px" />
          <div class="q-mt-sm text-caption">Drag tiles here</div>
        </div>
      </div>
    </div>

    <!-- Status -->
    <div class="status-bar q-pa-xs bg-grey-9 row items-center q-gutter-xs">
      <q-chip
        :color="store.hasStartFinish ? 'positive' : 'warning'"
        text-color="white"
        size="sm"
        dense
      >
        {{ store.hasStartFinish ? 'Start ✓' : 'Need Start' }}
      </q-chip>
      <q-chip
        v-if="store.disconnectedCount > 0"
        color="negative"
        text-color="white"
        size="sm"
        dense
      >
        {{ store.disconnectedCount }} disconnected
      </q-chip>
      <q-chip color="grey-7" text-color="grey-3" size="sm" dense>
        {{ store.currentTrack.tiles.length }} tiles
      </q-chip>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.track-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #0a0a0f;
}

.toolbar {
  border-bottom: 1px solid #333;
}

.editor-body {
  flex: 1;
  overflow: hidden;
}

.palette {
  width: 100px;
  overflow-y: auto;
  border-right: 1px solid #333;
}

.palette-tile {
  background: #1a1a24;
  border: 1px solid #333;
  border-radius: 4px;
  padding: 4px;
  cursor: grab;
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    border-color: #0f8;
  }
}

.tile-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #222228;
  border-radius: 3px;
  font-size: 14px;
  color: #888;

  &.corner {
    color: #4af;
  }
  &.start-finish {
    color: #fa4;
  }
}

.tile-name {
  font-size: 10px;
  color: #aaa;
  flex: 1;
}

.canvas {
  flex: 1;
  position: relative;
  overflow: auto;
  background: #060608;
  min-height: 400px;

  &.show-grid {
    background-image:
      repeating-linear-gradient(
        0deg,
        transparent,
        transparent 59px,
        rgba(255, 255, 255, 0.08) 59px,
        rgba(255, 255, 255, 0.08) 60px
      ),
      repeating-linear-gradient(
        90deg,
        transparent,
        transparent 59px,
        rgba(255, 255, 255, 0.08) 59px,
        rgba(255, 255, 255, 0.08) 60px
      );
  }
}

.placed-tile {
  position: absolute;
  cursor: grab;

  &.selected .tile-inner {
    box-shadow: 0 0 0 2px #0f8;
  }

  &.disconnected .tile-inner {
    box-shadow: 0 0 8px 2px rgba(255, 60, 60, 0.8);
  }
}

.tile-inner {
  width: 100%;
  height: 100%;
  transform-origin: center center;
  border-radius: 4px;
  overflow: hidden;
}

.drag-preview {
  position: absolute;
  pointer-events: none;
  z-index: 100;
  opacity: 0.7;
  border: 2px dashed #0f8;
  border-radius: 4px;

  &.invalid {
    border-color: #f44;
    opacity: 0.4;
  }
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.status-bar {
  border-top: 1px solid #333;
}
</style>
