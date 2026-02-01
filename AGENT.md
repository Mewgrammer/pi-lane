# Pi-Lane Agent Guidelines

> [!IMPORTANT]
> **ALWAYS READ `AI_CONTEXT.md` FIRST**
> That file contains the source-of-truth for project architecture, tech stack details, and core coding standards.

## 🚀 Quick Start for Agents

1.  **Context**: This is a **Raspberry Pi** slot car race manager.
    - **Backend**: Python (FastAPI/TinyDB) - focuses on hardware control & race logic.
    - **Frontend**: Vue 3 (Quasar/TypeScript) - focuses on mobile-first UI.
2.  **Package Manager**: ALWAYS use `pnpm` for frontend commands.
3.  **Database**: We use **TinyDB** (JSON file), NOT SQLAlchemy/SQLite/Postgres.

## ⚠️ Critical Rules (Do Not Ignore)

1.  **Quasar & Vue 3**:
    - Use **Composition API** `<script setup lang="ts">` exclusively.
    - Do **NOT** use Options API.
    - Do **NOT** use Vuetify or Tailwind classes unless verified (Quasar has its own class system, e.g., `q-pa-md`, `row`, `col`).
2.  **Carrera Specs**:
    - **Strictly follow** real-world dimensions for track pieces (19.8cm width).
    - See `docs/carrera.md` for exact measurements.
3.  **Hardware Mocking**:
    - When running on non-Pi systems (Windows/Linux/Mac), the backend **MUST** run in "Simulation Mode".
    - Check `config.py` default settings.

## 🛠️ Common Tasks Cheat Sheet

- **Run Frontend**: `pnpm dev` (in `/frontend`)
- **Run Backend**: `python src/pilane/main.py` (in `/backend`)
- **Frontend Lint**: `pnpm run lint`
- **Add Frontend Dependency**: `pnpm add <package>`

## 📂 Key File Locations

- **Track Pieces**: `frontend/src/components/track/trackPieces.ts` (Definitions & Geometry)
- **Track Editor**: `frontend/src/components/track/TrackEditor.vue` (Canvas Logic)
- **Race Engine**: `backend/src/pilane/race/engine.py` (Core Race Logic)
- **Database**: `backend/src/pilane/database.py` (TinyDB Wrapper)
