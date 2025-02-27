import asyncio
import websockets
import json
from typing import Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SyncEvent:
    event_type: str
    component: str
    data: Dict
    timestamp: str
    user: str

class RealtimeSync:
    def __init__(self, websocket_url: str = "ws://localhost:8765"):
        self.websocket_url = websocket_url
        self.connected_users: List[str] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.websocket = None

    async def connect(self):
        """Connect to the websocket server"""
        self.websocket = await websockets.connect(self.websocket_url)
        await self.send_event("connection", "system", {
            "status": "connected",
            "client_type": "integration"
        })

    async def send_event(self, event_type: str, component: str, data: Dict):
        """Send a sync event"""
        if not self.websocket:
            await self.connect()

        event = SyncEvent(
            event_type=event_type,
            component=component,
            data=data,
            timestamp=datetime.now().isoformat(),
            user="current_user"  # Replace with actual user management
        )
        
        await self.websocket.send(json.dumps(event.__dict__))

    async def listen_for_events(self):
        """Listen for incoming sync events"""
        if not self.websocket:
            await self.connect()

        try:
            while True:
                message = await self.websocket.recv()
                event = json.loads(message)
                await self.handle_event(event)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed. Attempting to reconnect...")
            await self.connect()

    async def handle_event(self, event: Dict):
        """Handle incoming sync events"""
        event_type = event['event_type']
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                await handler(event)

    def register_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def sync_model_update(self, model_data: Dict):
        """Sync model updates across all connected clients"""
        await self.send_event("model_update", "fusion360", model_data)

    async def sync_game_state(self, game_data: Dict):
        """Sync game state across all connected clients"""
        await self.send_event("game_update", "game", game_data)

    async def sync_diagram_update(self, diagram_data: Dict):
        """Sync SysML diagram updates across all connected clients"""
        await self.send_event("diagram_update", "sysml", diagram_data)

    def close(self):
        """Close the websocket connection"""
        if self.websocket:
            asyncio.get_event_loop().run_until_complete(self.websocket.close())
