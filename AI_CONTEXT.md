# AI Context for Pi-Lane

## Project Overview

Pi-Lane is a Raspberry Pi controlled race management system for Carrera analog slot car tracks. It bridges the gap between hardware sensors and a modern digital experience for slot car racing.

## Goals

- **Race Management**: Accurate lap counting, timing, and race control.
- **Hardware Integration**: Seamless interaction with Raspberry Pi GPIO for sensors.
- **User Experience**: A responsive, modern web interface for drivers and spectators.

## Architecture

The project is divided into two main components:

- **Backend (`/backend`)**: A Python-based FastAPI application that handles hardware interaction, race logic, and data storage.
- **Frontend (`/frontend`)**: A Vue 3 application (built with Quasar) that provides the user interface.

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
