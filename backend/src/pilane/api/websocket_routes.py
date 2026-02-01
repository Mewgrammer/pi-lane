"""WebSocket routes for real-time race updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import uuid
import json
import logging

from pilane.websocket import manager, create_ws_message

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time race updates."""
    connection_id = str(uuid.uuid4())
    await manager.connect(websocket, connection_id)
    
    logger.info(f"Client connected: {connection_id}")
    
    # Send welcome message
    await manager.send_personal(
        connection_id,
        create_ws_message("connected", {"connection_id": connection_id})
    )
    
    try:
        while True:
            # Receive and parse message
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_personal(
                    connection_id,
                    create_ws_message("error", {"message": "Invalid JSON"})
                )
                continue
            
            msg_type = message.get("type", "")
            payload = message.get("payload", {})
            
            # Handle different message types
            await handle_client_message(connection_id, msg_type, payload)
            
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
    finally:
        await manager.disconnect(connection_id)


async def handle_client_message(connection_id: str, msg_type: str, payload: dict):
    """Handle incoming WebSocket messages from clients."""
    logger.debug(f"Received {msg_type} from {connection_id}: {payload}")
    
    if msg_type == "race:subscribe":
        # Subscribe to a specific race for updates
        race_id = payload.get("race_id")
        if race_id:
            await manager.subscribe_to_race(connection_id, race_id)
            await manager.send_personal(
                connection_id,
                create_ws_message("race:subscribed", {"race_id": race_id})
            )
    
    elif msg_type == "race:unsubscribe":
        # Unsubscribe from a race
        race_id = payload.get("race_id")
        if race_id:
            await manager.unsubscribe_from_race(connection_id, race_id)
            await manager.send_personal(
                connection_id,
                create_ws_message("race:unsubscribed", {"race_id": race_id})
            )
    
    elif msg_type == "race:power":
        # Power level update (will be forwarded to race engine)
        lane = payload.get("lane")
        power_level = payload.get("power_level", 0)
        
        # TODO: Forward to race engine / hardware controller
        logger.info(f"Power update - Lane {lane}: {power_level}%")
        
        # Acknowledge
        await manager.send_personal(
            connection_id,
            create_ws_message("race:power_ack", {"lane": lane, "power_level": power_level})
        )
    
    elif msg_type == "ping":
        # Keep-alive ping
        await manager.send_personal(
            connection_id,
            create_ws_message("pong", {})
        )
    
    else:
        # Unknown message type
        await manager.send_personal(
            connection_id,
            create_ws_message("error", {"message": f"Unknown message type: {msg_type}"})
        )
