// Connector sides (before rotation)
export type Side = 'top' | 'right' | 'bottom' | 'left';

// Tile types
export type TileType = 'start-finish' | 'straight' | 'corner';

export interface TrackLayout {
  id: number | null;
  name: string;
  tiles: PlacedTile[];
}

export interface TileDefinition {
  id: string;
  name: string;
  type: TileType;
  carreraRef: string;

  // Grid size (in grid cells) - proportional to physical dimensions
  gridWidth: number;
  gridHeight: number;

  // Image path for rendering
  image: string;

  // Connectors in default orientation (0° rotation)
  connectors: { side: Side; role: 'entry' | 'exit' }[];

  // For corners: curve info
  curveDirection?: 'right' | 'left';
  curveAngle?: number;
  curveRadius?: string;
}

export interface PlacedTile {
  id: string;
  tileId: string;
  gridX: number;
  gridY: number;
  rotation: 0 | 90 | 180 | 270;
}
