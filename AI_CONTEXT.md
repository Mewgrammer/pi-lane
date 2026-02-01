# AI Context for Pi-Lane

## Project Background & Scope

The project revolves around revitalizing an old **Carrera analog slot racing track** by integrating it with a **Raspberry Pi** to provide modern digital features.

**Hardware Setup:**

- **Track**: Carrera Analog Track (no digital API available).
- **Controller**: Raspberry Pi with a PWM-capable controller for track power management.
- **Sensors**: Light barriers installed at the start/finish line of each lane to track lap passing.
- **Constraints**: We are physically limited by the analog nature of the track but simulate digital features where possible.

**Core Objectives:**

- Track laps, times, and vehicle positions.
- Manage track power via PWM.
- Provide a modern web interface for race management.

## Architecture & Simulation

### Backend (Python)

The backend manages the hardware interaction and race logic.

- **REST API**: Manages static data (Tracks, Races, Leaderboards, Cars, Users).
- **WebSockets**: Handles real-time race data (telemetry, state changes).
- **Hardware Abstraction**: Currently uses a **Simulation Mode** but is designed to switch to physical RPi GPIO interaction.

**Simulation Logic:**

- Simulates car position based on configurable speed and track definitions (type + distance).
- Uses specific car speed with random deviation per track piece.
- Calculates movement over time (e.g., 10cm piece @ 25mm/s).
- Supports multiple lanes and cars simultaneously.

### Frontend (Vue 3)

The UI serves as the control center for drivers and spectators.

**Key Features:**

- **Track Editor**: Design and save track layouts.
- **Race Control**: Settings for rules, timers, race modes, and fuel simulation.
- **Dashboard**: Graphical display of the track with real-time (estimated) car positions.
- **Management**: User registration, Car management, and Leaderboards.

## Tech Stack

### Backend

- **Language**: Python (>= 3.11)
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Real-time**: WebSockets
- **Database**: TinyDB
- **Hardware Interaction**: `RPi.GPIO`, `pigpio`

### Frontend

- **Framework**: Vue 3 (Composition API)
- **UI Framework**: Quasar v2
- **Build Tool**: Vite
- **Language**: TypeScript
- **State Management**: Pinia
- **HTTP Client**: Axios

## Project Structure

- `backend/src/pilane/`: Main backend application code.
- `frontend/src/`: Main frontend application code.
- `docs/`: Project documentation.

## Carrera Specification

Ideally, refer to [docs/carrera.md](docs/carrera.md) for detailed specifications of Carrera Evolution track pieces.
This file contains:

- Track width and lane spacing.
- Dimensions for standard, 1/3, and 1/4 straights.
- Geometry for various curve radii (Radius 1-4).

## Coding Standards

### Python (Backend)

- **Style**: Follow PEP 8 guidelines.
- **Typing**: Use Python type hints extensively.
- **Models**: Use Pydantic for data validation and schema definition.
- **Async**: Utilize `async`/`await` for asynchronous route handlers and I/O operations.
- **Structure**: Keep business logic, database access, and API routes separated.

### Vue 3 (Frontend)

- **Composition API**: **REQUIRED**. Use `<script setup lang="ts">`.
- **Component Structure**:
  1. `<script setup>`
  2. `<template>`
  3. `<style>` (scoped)
- **Types**:
  - Keep types separated in the `frontend/src/types` directory.
  - Avoid defining complex types inside components.
- **State Management**: Use **Pinia** for all global state and data persistence.
- **Best Practices**:
  - Use `defineProps` and `defineEmits` with TypeScript interfaces.
  - Avoid Options API.
  - Use scoped styles to prevent bleeding.
  - Follow Quasar best practices for component usage.

## Hardware & Constraints

- **Platform**: Targeted for Raspberry Pi (deployment).
- **GPIO**: Direct access to GPIO pins is managed by the backend.
- **Performance**: Resource usage should be optimized for the Raspberry Pi environment.

## Detailed Feature Specifications

### 1. Basic Race Logic

The core race engine must handle the following lifecycle:

- **Safe Start**: A countdown (5 lights logic) that holds cars stationary (0 PWM) until the race starts. False start detection (passing sensor before start) should penalty the driver.
- **Lap Counting**: Increment laps when the light barrier is triggered. Implement "Minimum Lap Time" to prevent double-counting from sensor jitter.
- **Time Limit**: Support "Time Attack" races (max laps within X minutes) or "Endurance" (max distance within X minutes).
- **Finish**:
  - **Lap Race**: First to complete N laps wins. Others finish their current lap.
  - **Timed Race**: After time expires, finish the current lap to lock in position.

### 2. Fuel Simulation

Since analog cars don't report fuel, we simulate it based on throttle usage:

- **Consumption Model**: Fuel decreases based on PWM usage over time (e.g., `Fuel -= CurrentPWM * ConsumptionRate`).
- **Weight Penalty**: (Optional) Fully fueled cars could have a simulated "sluggishness" (max PWM capped slightly lower) or braking distance increased.
- **Empty Fuel**: If fuel reaches 0, the car enters "Limp Mode" (max PWM restricted to 20-30%) or stops completely.

### 3. Pit Stops (Virtual)

On an analog track without a physical pit lane, we simulate pit stops via behavior:

- **Trigger**: Driver holds a specific button or stops the car for N seconds.
- **Execution**:
  - The system detects the car is stationary (0 PWM sent and no sensor triggers).
  - UI shows a "Refueling/Changing Tires" progress bar.
  - **Constraint**: Car _cannot_ move during this time. Any throttle input pauses the pit stop.
- **Strategic Element**: Drivers must choose when to stop on the track (ideally near start/finish) to "refuel".

### 4. Safety Car / Yellow Flags

Used for hazards or race management:

- **Yellow Flag**: limit all cars to a safe speed (e.g., max 40% PWM). Overtaking is tracked virtually (if position context exists) or simply enforced by speed limits.
- **Safety Car**: A virtual safety car phase where a delta time is enforced, or all cars are software-limited to a slow speed to bunch up the field.
- **Red Flag**: Immediate power cut (0 PWM) to all lanes. Race paused.

### 5. Assisted / Auto Drive

Leveraging the track definition and estimated position:

- **Corner Braking**: The system "knows" a corner is approaching based on the estimated position on the track map.
  - _Action_: Automatically reduce PWM if the user is entering a sharp corner too fast.
- **Lane Keeping**: (Not applicable to slot cars directly, but "Deslotting Prevention")
- **Pace Car**: A computer-controlled opponent on an empty lane that drives at a set difficulty level (variable PWM based on track section).

## Future Improvements

### 1. Ghost Car / Replay

- Record the throttle inputs and lap times of a "Best Lap".
- Replay this on a spare lane (or virtually on the UI) to race against yourself.

### 2. Championship Mode

- Link multiple races into a season.
- Track driver points [1st=25, 2nd=18, etc.] across the season.
- Save history and stats (Best season, most wins).

### 3. Voice Commentary & Spotter

- Use browser Text-to-Speech (TTS) to announce:
  - "Lap times: 5.4s"
  - "Low Fuel Warning"
  - "Yellow Flag in Sector 2"
  - "Winner: Driver X"

### 4. Hardware Telemetry Expansion

- **Sector Sensors**: Add more light barriers for sector timing.
- **Current Sensing**: Measure actual current draw to detect deslotting (current drops to 0) vs. just stopped car.
