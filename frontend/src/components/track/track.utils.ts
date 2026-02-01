/**
 * Simplified Track Pieces - All tiles are 1x1 grid cells
 *
 * Tile Types:
 * - Start/Finish: entry on right, exit on left
 * - Straight: entry on right, exit on left
 * - Corner (Right): entry on right, exit on top (internal direction: right)
 *   Rotating twice flips direction (right ↔ left)
 *
 * Rotation: 0°, 90°, 180°, 270° clockwise
 * Connectors rotate with the tile
 */

import type { PlacedTile, Side, TileDefinition } from 'src/types/track.types';

// Grid cell size in pixels
export const CELL_SIZE = 60;

// === TILE DEFINITIONS ===

export const TILES: TileDefinition[] = [
  {
    id: 'start-finish',
    name: 'Start/Finish',
    type: 'start-finish',
    carreraRef: '20515',
    connectors: [
      { side: 'right', role: 'entry' },
      { side: 'left', role: 'exit' },
    ],
  },
  {
    id: 'straight',
    name: 'Straight',
    type: 'straight',
    carreraRef: '20509',
    connectors: [
      { side: 'right', role: 'entry' },
      { side: 'left', role: 'exit' },
    ],
  },
  {
    id: 'straight-1-3',
    name: 'Straight 1/3',
    type: 'straight',
    carreraRef: '20611',
    connectors: [
      { side: 'right', role: 'entry' },
      { side: 'left', role: 'exit' },
    ],
  },
  {
    id: 'corner-r1',
    name: 'Corner R1',
    type: 'corner',
    carreraRef: '20571',
    curveDirection: 'right',
    curveAngle: 60,
    curveRadius: 'R1',
    connectors: [
      { side: 'right', role: 'entry' },
      { side: 'top', role: 'exit' },
    ],
  },
  {
    id: 'corner-r2',
    name: 'Corner R2',
    type: 'corner',
    carreraRef: '20572',
    curveDirection: 'right',
    curveAngle: 30,
    curveRadius: 'R2',
    connectors: [
      { side: 'right', role: 'entry' },
      { side: 'top', role: 'exit' },
    ],
  },
  {
    id: 'corner-r3',
    name: 'Corner R3',
    type: 'corner',
    carreraRef: '20573',
    curveDirection: 'right',
    curveAngle: 30,
    curveRadius: 'R3',
    connectors: [
      { side: 'right', role: 'entry' },
      { side: 'top', role: 'exit' },
    ],
  },
];

// === HELPERS ===

export function getTileById(id: string): TileDefinition | undefined {
  return TILES.find((t) => t.id === id);
}

// Rotate a side clockwise by given degrees
export function rotateSide(side: Side, rotation: 0 | 90 | 180 | 270): Side {
  const sides: Side[] = ['top', 'right', 'bottom', 'left'];
  const idx = sides.indexOf(side);
  const steps = rotation / 90;
  return sides[(idx + steps) % 4]!;
}

// Get the opposite side
export function oppositeSide(side: Side): Side {
  const map: Record<Side, Side> = { top: 'bottom', right: 'left', bottom: 'top', left: 'right' };
  return map[side];
}

// Get world sides of connectors for a placed tile
export function getConnectorSides(tile: TileDefinition, rotation: 0 | 90 | 180 | 270): Side[] {
  return tile.connectors.map((c) => rotateSide(c.side, rotation));
}

// Get adjacent grid position for a side
export function getAdjacentPos(x: number, y: number, side: Side): { x: number; y: number } {
  switch (side) {
    case 'top':
      return { x, y: y - 1 };
    case 'bottom':
      return { x, y: y + 1 };
    case 'left':
      return { x: x - 1, y };
    case 'right':
      return { x: x + 1, y };
  }
}

// Check if a tile at position has a connector on the given side
export function hasConnectorOnSide(
  tile: TileDefinition,
  rotation: 0 | 90 | 180 | 270,
  side: Side,
): boolean {
  const sides = getConnectorSides(tile, rotation);
  return sides.includes(side);
}

// Check if two adjacent tiles are connected
export function areTilesConnected(
  tile1: TileDefinition,
  rot1: 0 | 90 | 180 | 270,
  tile2: TileDefinition,
  rot2: 0 | 90 | 180 | 270,
  sharedSide: Side, // side of tile1 that faces tile2
): boolean {
  const tile1HasConnector = hasConnectorOnSide(tile1, rot1, sharedSide);
  const tile2HasConnector = hasConnectorOnSide(tile2, rot2, oppositeSide(sharedSide));
  return tile1HasConnector && tile2HasConnector;
}

// Check if a placed tile is connected to any neighbor
export function isTileConnected(
  tile: TileDefinition,
  gridX: number,
  gridY: number,
  rotation: 0 | 90 | 180 | 270,
  allTiles: PlacedTile[],
  excludeId?: string,
): boolean {
  const sides = getConnectorSides(tile, rotation);

  for (const side of sides) {
    const adj = getAdjacentPos(gridX, gridY, side);
    const neighbor = allTiles.find(
      (t) => t.gridX === adj.x && t.gridY === adj.y && t.id !== excludeId,
    );
    if (neighbor) {
      const neighborDef = getTileById(neighbor.tileId);
      if (neighborDef && areTilesConnected(tile, rotation, neighborDef, neighbor.rotation, side)) {
        return true;
      }
    }
  }
  return false;
}

// Get connected sides for a placed tile
export function getConnectedSides(
  tile: TileDefinition,
  gridX: number,
  gridY: number,
  rotation: 0 | 90 | 180 | 270,
  allTiles: PlacedTile[],
  excludeId?: string,
): Side[] {
  const connected: Side[] = [];
  const sides = getConnectorSides(tile, rotation);

  for (const side of sides) {
    const adj = getAdjacentPos(gridX, gridY, side);
    const neighbor = allTiles.find(
      (t) => t.gridX === adj.x && t.gridY === adj.y && t.id !== excludeId,
    );
    if (neighbor) {
      const neighborDef = getTileById(neighbor.tileId);
      if (neighborDef && areTilesConnected(tile, rotation, neighborDef, neighbor.rotation, side)) {
        connected.push(side);
      }
    }
  }
  return connected;
}

// Check if position is occupied
export function isPositionOccupied(
  gridX: number,
  gridY: number,
  allTiles: PlacedTile[],
  excludeId?: string,
): boolean {
  return allTiles.some((t) => t.gridX === gridX && t.gridY === gridY && t.id !== excludeId);
}
