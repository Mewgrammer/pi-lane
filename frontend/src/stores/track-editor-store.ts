import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import {
  TILES,
  getTileById,
  CELL_SIZE,
  isPositionOccupied,
  isTileConnected,
  getConnectedSides,
} from '../components/track/track.utils';
import type { PlacedTile, TrackLayout } from 'src/types/track.types';

export const useTrackEditorStore = defineStore('trackEditor', () => {
  const currentTrack = ref<TrackLayout>({
    id: null,
    name: 'New Track',
    tiles: [],
  });

  const selectedTileId = ref<string | null>(null);

  // Drag state
  const isDragging = ref(false);
  const dragTileId = ref<string | null>(null); // Tile definition ID
  const dragGridX = ref(0);
  const dragGridY = ref(0);
  const dragRotation = ref<0 | 90 | 180 | 270>(0);
  const dragValid = ref(true); // No collision
  const dragMovingId = ref<string | null>(null); // If moving existing tile

  const showGrid = ref(true);

  const availableTiles = computed(() => TILES);

  const selectedTile = computed(() =>
    selectedTileId.value
      ? (currentTrack.value.tiles.find((t) => t.id === selectedTileId.value) ?? null)
      : null,
  );

  function generateId(): string {
    return `t-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
  }

  function pixelToGrid(px: number): number {
    return Math.floor(px / CELL_SIZE);
  }

  function startDragFromPalette(tileId: string): void {
    isDragging.value = true;
    dragTileId.value = tileId;
    dragRotation.value = 0;
    dragMovingId.value = null;
    dragValid.value = true;
  }

  function startDragPlaced(placedId: string): void {
    const tile = currentTrack.value.tiles.find((t) => t.id === placedId);
    if (!tile) return;
    isDragging.value = true;
    dragTileId.value = tile.tileId;
    dragGridX.value = tile.gridX;
    dragGridY.value = tile.gridY;
    dragRotation.value = tile.rotation;
    dragMovingId.value = placedId;
    dragValid.value = true;
  }

  function updateDragPosition(pixelX: number, pixelY: number): void {
    if (!isDragging.value || !dragTileId.value) return;

    const gx = pixelToGrid(pixelX);
    const gy = pixelToGrid(pixelY);

    dragGridX.value = gx;
    dragGridY.value = gy;

    // Check collision with multi-cell awareness
    const tileDef = getTileById(dragTileId.value);
    if (tileDef) {
      dragValid.value = !isPositionOccupied(
        gx,
        gy,
        tileDef,
        dragRotation.value,
        currentTrack.value.tiles,
        dragMovingId.value ?? undefined,
      );
    } else {
      dragValid.value = false;
    }
  }

  function endDrag(): { placed: boolean; id?: string } {
    if (!isDragging.value || !dragTileId.value || !dragValid.value) {
      cancelDrag();
      return { placed: false };
    }

    let resultId: string;

    if (dragMovingId.value) {
      // Move existing
      const existing = currentTrack.value.tiles.find((t) => t.id === dragMovingId.value);
      if (existing) {
        existing.gridX = dragGridX.value;
        existing.gridY = dragGridY.value;
        existing.rotation = dragRotation.value;
        resultId = existing.id;
      } else {
        resultId = '';
      }
    } else {
      // Place new
      const newTile: PlacedTile = {
        id: generateId(),
        tileId: dragTileId.value,
        gridX: dragGridX.value,
        gridY: dragGridY.value,
        rotation: dragRotation.value,
      };
      currentTrack.value.tiles.push(newTile);
      resultId = newTile.id;
    }

    cancelDrag();
    return { placed: true, id: resultId };
  }

  function cancelDrag(): void {
    isDragging.value = false;
    dragTileId.value = null;
    dragMovingId.value = null;
  }

  function removeTile(id: string): void {
    const idx = currentTrack.value.tiles.findIndex((t) => t.id === id);
    if (idx !== -1) {
      currentTrack.value.tiles.splice(idx, 1);
      if (selectedTileId.value === id) selectedTileId.value = null;
    }
  }

  function rotateTile(id: string): void {
    const tile = currentTrack.value.tiles.find((t) => t.id === id);
    if (tile) {
      tile.rotation = ((tile.rotation + 90) % 360) as 0 | 90 | 180 | 270;
    }
  }

  function rotateDrag(): void {
    dragRotation.value = ((dragRotation.value + 90) % 360) as 0 | 90 | 180 | 270;
  }

  function selectTile(id: string | null): void {
    selectedTileId.value = id;
  }

  function clearTrack(): void {
    currentTrack.value.tiles = [];
    selectedTileId.value = null;
  }

  function newTrack(): void {
    currentTrack.value = { id: null, name: 'New Track', tiles: [] };
    selectedTileId.value = null;
  }

  // Is placed tile connected?
  function isPlacedConnected(placedId: string): boolean {
    const placed = currentTrack.value.tiles.find((t) => t.id === placedId);
    if (!placed) return false;
    if (currentTrack.value.tiles.length === 1) return true; // First tile always "connected"
    const def = getTileById(placed.tileId);
    if (!def) return false;
    return isTileConnected(
      def,
      placed.gridX,
      placed.gridY,
      placed.rotation,
      currentTrack.value.tiles,
      placed.id,
    );
  }

  // Get connected sides for a placed tile
  function getPlacedConnectedSides(placedId: string): string[] {
    const placed = currentTrack.value.tiles.find((t) => t.id === placedId);
    if (!placed) return [];
    const def = getTileById(placed.tileId);
    if (!def) return [];
    return getConnectedSides(
      def,
      placed.gridX,
      placed.gridY,
      placed.rotation,
      currentTrack.value.tiles,
      placed.id,
    );
  }

  const hasStartFinish = computed(() =>
    currentTrack.value.tiles.some((t) => t.tileId === 'start-finish'),
  );

  const disconnectedCount = computed(
    () => currentTrack.value.tiles.filter((t) => !isPlacedConnected(t.id)).length,
  );

  function exportTrack(): string {
    return JSON.stringify(currentTrack.value, null, 2);
  }

  return {
    currentTrack,
    selectedTileId,
    selectedTile,
    isDragging,
    dragTileId,
    dragGridX,
    dragGridY,
    dragRotation,
    dragValid,
    dragMovingId,
    showGrid,
    availableTiles,
    hasStartFinish,
    disconnectedCount,
    startDragFromPalette,
    startDragPlaced,
    updateDragPosition,
    endDrag,
    cancelDrag,
    removeTile,
    rotateTile,
    rotateDrag,
    selectTile,
    clearTrack,
    newTrack,
    isPlacedConnected,
    getPlacedConnectedSides,
    exportTrack,
    getTileById,
    CELL_SIZE,
  };
});
