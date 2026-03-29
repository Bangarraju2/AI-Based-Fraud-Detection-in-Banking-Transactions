"""
WebSocket Router
Handles real-time fraud alert streaming to connected clients.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.fraud_service import active_connections
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/alerts")
async def websocket_fraud_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time fraud alerts.
    Clients connect here to receive live notifications when HIGH risk transactions are detected.
    """
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket client connected. Total: {len(active_connections)}")

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to FraudShield real-time alerts",
            "active_clients": len(active_connections),
        })

        # Keep connection alive and listen for client messages
        while True:
            data = await websocket.receive_text()
            # Handle ping/pong for keepalive
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)
