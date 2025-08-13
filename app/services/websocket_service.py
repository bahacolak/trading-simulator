import json
import asyncio
import logging
from typing import List, Optional
from fastapi import WebSocket, WebSocketDisconnect

from .price_service import price_service

logger = logging.getLogger(__name__)

class WebSocketManager:
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._broadcast_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        if not self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

    async def start_price_broadcast(self):
        if self._broadcast_task and not self._broadcast_task.done():
            return
        
        self._broadcast_task = asyncio.create_task(self._price_broadcast_loop())
        logger.info("Price broadcast service started")

    async def stop_price_broadcast(self):
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
            logger.info("Price broadcast service stopped")

    async def _price_broadcast_loop(self):
        while True:
            try:
                if self.active_connections:
                    prices = price_service.get_all_prices()
                    await self.broadcast(json.dumps(prices))
                
                await asyncio.sleep(2)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in price broadcast loop: {e}")
                await asyncio.sleep(5)

websocket_manager = WebSocketManager()
