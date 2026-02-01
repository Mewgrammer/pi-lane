# Pi-Lane Backend

Slot car racing control system backend built with FastAPI.

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the development server
python -m uvicorn pilane.main:app --reload

# Or simply
python -m pilane.main
```

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## WebSocket

Connect to `ws://localhost:8000/ws` for real-time race updates.

### Message Types

**Subscribe to race:**

```json
{ "type": "race:subscribe", "payload": { "race_id": 1 } }
```

**Set power:**

```json
{ "type": "race:power", "payload": { "lane": 1, "power_level": 75 } }
```

## Environment Variables

| Variable               | Default                           | Description                    |
| ---------------------- | --------------------------------- | ------------------------------ |
| `PILANE_DEBUG`         | `false`                           | Enable debug mode              |
| `PILANE_HARDWARE_MODE` | `simulation`                      | `simulation` or `raspberry_pi` |
| `PILANE_DATABASE_URL`  | `sqlite+aiosqlite:///./pilane.db` | Database connection string     |
