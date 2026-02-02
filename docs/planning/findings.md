# Findings & Decisions

## Requirements

<!-- Captured from user request -->

- Multi-phase project modernization of slot car track
- Backend with GPIO access (RPi)
- Mobile-optimized Vue frontend
- WebSocket & API connection
- Phases:
  1. Basic Frontend with Track Editor
  2. Track & Car Simulation
  3. Basic Race Modes
  4. GPIO Integration
  5. User & Car Management
  6. Fuel Simulation & Advanced Racing
  7. Assisted/Auto Drive

## Research Findings

<!-- Key discoveries during exploration -->

- **Existing Backend**: FastAPI, Uvicorn, TinyDB. Structure in `backend/src/pilane`.
  - `api/tracks.py`: Full CRUD exists for tracks.
  - `schemas.py`: Comprehensive Pydantic models for Tracks, Races, Users, Cars.
  - `websocket.py`: Basic WebSocket structure exists.
- **Existing Frontend**: Vue 3 + Quasar + Pinia. Structure in `frontend/src`.
  - `TrackEditor.vue`: Functional drag-and-drop editor.
  - `track-editor-store.ts`: State management for editor.
  - `track.utils.ts`: Tile definitions (currently limited mainly to Straights and R1 curves).
- **Documentation**:
  - `docs/carrera.md`: Contains specs for all Carrera pieces (R1-R4), essential for Phase 1.

## Technical Decisions

<!-- Decisions made with rationale -->

| Decision     | Rationale                                                                                |
| ------------ | ---------------------------------------------------------------------------------------- |
| **TinyDB**   | Currently used in backend. Good for prototyping, but monitor performance with many laps. |
| **Quasar**   | Already in place. Good for mobile optimization (requested).                              |
| **Pydantic** | Used for validation. Strict schemas already defined in `schemas.py`.                     |

## Issues Encountered

<!-- Errors and how they were resolved -->

| Issue | Resolution |
| ----- | ---------- |
|       |            |

## Resources

<!-- URLs, file paths, API references -->

- `backend/src/pilane/schemas.py`: Data models
- `docs/carrera.md`: Track piece specifications
- `frontend/src/components/track/track.utils.ts`: Current tile implementation

## Visual/Browser Findings

<!-- CRITICAL: Update after every 2 view/browser operations -->

- `TrackEditor.vue` shows a dark theme UI with toolbar on top, palette on left, canvas in center.
- Tiles are rendered using SVG in `TileRenderer.vue`.
