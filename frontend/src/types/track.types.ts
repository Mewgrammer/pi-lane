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
  // Connectors in default orientation (0° rotation)
  // Each connector has a side and whether it's entry or exit
  connectors: { side: Side; role: 'entry' | 'exit' }[];
  // For corners: internal curve direction
  curveDirection?: 'right' | 'left';
  // Internal curve info (doesn't affect grid, just for data)
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
