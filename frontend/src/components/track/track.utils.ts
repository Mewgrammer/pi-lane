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
    gridWidth: 1,
    gridHeight: 2,
    image: '/tiles/start-finish.png',
    connectors: [
      { side: 'bottom', role: 'entry' },
      { side: 'top', role: 'exit' },
    ],
  },
  {
    id: 'straight',
    name: 'Straight',
    type: 'straight',
    carreraRef: '20509',
    gridWidth: 1,
    gridHeight: 2,
    image: '/tiles/straight.png',
    connectors: [
      { side: 'bottom', role: 'entry' },
      { side: 'top', role: 'exit' },
    ],
  },
  {
    id: 'straight-1-3',
    name: 'Short',
    type: 'straight',
    carreraRef: '20611',
    gridWidth: 1,
    gridHeight: 1,
    image: '/tiles/straight-short.png',
    connectors: [
      { side: 'bottom', role: 'entry' },
      { side: 'top', role: 'exit' },
    ],
  },
  {
    id: 'corner-r1',
    name: 'Corner R1',
    type: 'corner',
    carreraRef: '20571',
    gridWidth: 2,
    gridHeight: 2,
    image: '/tiles/corner-r1.png',
    curveDirection: 'right',
    curveAngle: 60,
    curveRadius: 'R1',
    connectors: [
      { side: 'bottom', role: 'entry' },
      { side: 'right', role: 'exit' },
    ],
  },
  {
    id: 'corner-r2',
    name: 'Corner R2',
    type: 'corner',
    carreraRef: '20572',
    gridWidth: 2,
    gridHeight: 2,
    image: '/tiles/corner-r2.png',
    curveDirection: 'right',
    curveAngle: 30,
    curveRadius: 'R2',
    connectors: [
      { side: 'bottom', role: 'entry' },
      { side: 'right', role: 'exit' },
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

// Get rotated grid dimensions (width/height swap on 90/270 rotation)
export function getRotatedDimensions(
  tile: TileDefinition,
  rotation: 0 | 90 | 180 | 270,
): { width: number; height: number } {
  if (rotation === 90 || rotation === 270) {
    return { width: tile.gridHeight, height: tile.gridWidth };
  }
  return { width: tile.gridWidth, height: tile.gridHeight };
}

// Get all grid cells occupied by a placed tile
export function getOccupiedCells(
  gridX: number,
  gridY: number,
  tile: TileDefinition,
  rotation: 0 | 90 | 180 | 270,
): { x: number; y: number }[] {
  const { width, height } = getRotatedDimensions(tile, rotation);
  const cells: { x: number; y: number }[] = [];
  for (let dx = 0; dx < width; dx++) {
    for (let dy = 0; dy < height; dy++) {
      cells.push({ x: gridX + dx, y: gridY + dy });
    }
  }
  return cells;
}

// Get edge cells for a specific side of a multi-cell tile
export function getEdgeCells(
  gridX: number,
  gridY: number,
  tile: TileDefinition,
  rotation: 0 | 90 | 180 | 270,
  side: Side,
): { x: number; y: number }[] {
  const { width, height } = getRotatedDimensions(tile, rotation);
  const cells: { x: number; y: number }[] = [];

  switch (side) {
    case 'top':
      for (let dx = 0; dx < width; dx++) {
        cells.push({ x: gridX + dx, y: gridY - 1 });
      }
      break;
    case 'bottom':
      for (let dx = 0; dx < width; dx++) {
        cells.push({ x: gridX + dx, y: gridY + height });
      }
      break;
    case 'left':
      for (let dy = 0; dy < height; dy++) {
        cells.push({ x: gridX - 1, y: gridY + dy });
      }
      break;
    case 'right':
      for (let dy = 0; dy < height; dy++) {
        cells.push({ x: gridX + width, y: gridY + dy });
      }
      break;
  }
  return cells;
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

// Find a placed tile that occupies a specific cell
export function findTileAtCell(
  cellX: number,
  cellY: number,
  allTiles: PlacedTile[],
  excludeId?: string,
): PlacedTile | undefined {
  for (const placed of allTiles) {
    if (placed.id === excludeId) continue;
    const def = getTileById(placed.tileId);
    if (!def) continue;
    const cells = getOccupiedCells(placed.gridX, placed.gridY, def, placed.rotation);
    if (cells.some((c) => c.x === cellX && c.y === cellY)) {
      return placed;
    }
  }
  return undefined;
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
    const edgeCells = getEdgeCells(gridX, gridY, tile, rotation, side);
    for (const cell of edgeCells) {
      const neighbor = findTileAtCell(cell.x, cell.y, allTiles, excludeId);
      if (neighbor) {
        const neighborDef = getTileById(neighbor.tileId);
        if (
          neighborDef &&
          areTilesConnected(tile, rotation, neighborDef, neighbor.rotation, side)
        ) {
          return true;
        }
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
    const edgeCells = getEdgeCells(gridX, gridY, tile, rotation, side);
    for (const cell of edgeCells) {
      const neighbor = findTileAtCell(cell.x, cell.y, allTiles, excludeId);
      if (neighbor) {
        const neighborDef = getTileById(neighbor.tileId);
        if (
          neighborDef &&
          areTilesConnected(tile, rotation, neighborDef, neighbor.rotation, side)
        ) {
          connected.push(side);
          break; // Found connection on this side
        }
      }
    }
  }
  return connected;
}

// Check if any cell in the proposed position is occupied
export function isPositionOccupied(
  gridX: number,
  gridY: number,
  tile: TileDefinition,
  rotation: 0 | 90 | 180 | 270,
  allTiles: PlacedTile[],
  excludeId?: string,
): boolean {
  const cells = getOccupiedCells(gridX, gridY, tile, rotation);
  for (const cell of cells) {
    if (findTileAtCell(cell.x, cell.y, allTiles, excludeId)) {
      return true;
    }
  }
  return false;
}
