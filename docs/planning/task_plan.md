# Task Plan: Pi-Lane Slot Car Modernization

## Goal

Transform an analog Carrera slot car track into a modern, digitally-enhanced racing experience using Raspberry Pi, Vue 3, and Python FastAPI, featuring track editor, simulation, and hardware integration.

## Current Phase

Phase 1

## Phases

### Phase 1: Basic Frontend with Track Editor

- [ ] Requirements & Discovery (Analyze existing code)
- [ ] Track Editor Enhancements (Visuals, Logic)
- [ ] Track Piece Library (All Carrera pieces)
- [ ] Track Persistence (Save/Load API)
- [ ] Backend Track API Implementation
- [ ] Track Validation logic
- **Status:** in_progress

### Phase 2: Track & Car Simulation

- [ ] Track Model (Linear distance calculation)
- [ ] Car Simulation Engine (Physics loop)
- [ ] Frontend Visualization (Real-time overlay)
- [ ] WebSocket Infrastructure (Telemetry)
- **Status:** pending

### Phase 3: Basic Race Modes

- [ ] Race Engine (State machine)
- [ ] Lap Counting Logic
- [ ] Race Modes (Practice, Time Trial, Laps)
- [ ] Race Control UI
- **Status:** pending

### Phase 4: GPIO Integration

- [ ] Hardware Abstraction Layer
- [ ] GPIO Implementation (PWM, Sensors)
- [ ] Simulation Fallback
- [ ] Hardware Configuration
- **Status:** pending

### Phase 5: User & Car Management, Leaderboards

- [ ] User Management (CRUD, Stats)
- [ ] Car Management (CRUD, Ownership)
- [ ] Leaderboards (Per track, All-time)
- [ ] Data Persistence (TinyDB Refinements)
- **Status:** pending

### Phase 6: Fuel Simulation & Advanced Features

- [ ] Fuel Consumption Model
- [ ] Virtual Pit Stops
- [ ] Sector Timing
- [ ] Safety Features (Yellow/Red Flag)
- **Status:** pending

### Phase 7: Assisted Drive / Auto Drive

- [ ] Corner Braking Assist
- [ ] Pace Car Mode (Computer opponent)
- [ ] Ghost Car / Replay System
- **Status:** pending

## Key Questions

1. Is pigpio sufficient for PWM control on the target RPi model?
2. How to handle sensor jitter/debounce effectively in software vs hardware?
3. Best strategy for mobile browser performance with high-frequency WebSocket updates?

## Decisions Made

| Decision                      | Rationale                                                  |
| ----------------------------- | ---------------------------------------------------------- |
| Use existing Quasar/Vue stack | Matches user's current project structure and request       |
| Python FastAPI Backend        | Leverages existing code and fits RPi environment well      |
| TinyDB for storage            | Simple, file-based, sufficient for single-user/local scale |

## Errors Encountered

| Error | Attempt | Resolution |
| ----- | ------- | ---------- |
|       | 1       |            |

## Notes

- Update phase status as you progress: pending → in_progress → complete
- Log ALL errors - they help avoid repetition
