"""WebSocket connection manager for real-time race updates."""

from typing import Any
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        # Active connections: {connection_id: WebSocket}
        self.active_connections: dict[str, WebSocket] = {}
        # Connection metadata: {connection_id: {user_id, race_id, etc.}}
        self.connection_metadata: dict[str, dict[str, Any]] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, connection_id: str) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self.active_connections[connection_id] = websocket
            self.connection_metadata[connection_id] = {
                "connected_at": datetime.utcnow().isoformat(),
                "subscribed_races": set(),
            }
    
    async def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection."""
        async with self._lock:
            self.active_connections.pop(connection_id, None)
            self.connection_metadata.pop(connection_id, None)
    
    async def subscribe_to_race(self, connection_id: str, race_id: int) -> None:
        """Subscribe a connection to receive updates for a specific race."""
        async with self._lock:
            if connection_id in self.connection_metadata:
                self.connection_metadata[connection_id]["subscribed_races"].add(race_id)
    
    async def unsubscribe_from_race(self, connection_id: str, race_id: int) -> None:
        """Unsubscribe a connection from a specific race."""
        async with self._lock:
            if connection_id in self.connection_metadata:
                self.connection_metadata[connection_id]["subscribed_races"].discard(race_id)
    
    async def send_personal(self, connection_id: str, message: dict) -> None:
        """Send a message to a specific connection."""
        websocket = self.active_connections.get(connection_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception:
                await self.disconnect(connection_id)
    
    async def broadcast(self, message: dict) -> None:
        """Broadcast a message to all connected clients."""
        await self._send_to_connections(list(self.active_connections.keys()), message)
    
    async def broadcast_to_race(self, race_id: int, message: dict) -> None:
        """Broadcast a message to all clients subscribed to a specific race."""
        connection_ids = []
        async with self._lock:
            for conn_id, metadata in self.connection_metadata.items():
                if race_id in metadata.get("subscribed_races", set()):
                    connection_ids.append(conn_id)
        
        await self._send_to_connections(connection_ids, message)
    
    async def _send_to_connections(self, connection_ids: list[str], message: dict) -> None:
        """Send a message to multiple connections."""
        disconnected = []
        for connection_id in connection_ids:
            websocket = self.active_connections.get(connection_id)
            if websocket:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(connection_id)
        
        # Clean up disconnected clients
        for connection_id in disconnected:
            await self.disconnect(connection_id)
    
    @property
    def connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()


def create_ws_message(event_type: str, payload: Any) -> dict:
    """Create a standardized WebSocket message."""
    return {
        "type": event_type,
        "payload": payload,
        "timestamp": datetime.utcnow().timestamp(),
    }
