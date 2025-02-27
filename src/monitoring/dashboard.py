"""Web dashboard for real-time system monitoring."""

import asyncio
import json
import logging
from typing import Dict, Optional
from aiohttp import web
from aiohttp import WSMsgType
import aiohttp_cors
from datetime import datetime

from .system_monitor import SystemMonitor
from .visualization import MonitoringDashboard

class DashboardServer:
    """Async web server for monitoring dashboard."""
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.app = web.Application()
        self.monitor = SystemMonitor()
        self.dashboard = MonitoringDashboard()
        self.websockets = set()
        self.setup_routes()
        
    def setup_routes(self):
        """Setup server routes."""
        # Configure CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"
            )
        })
        
        # Add routes
        cors.add(self.app.router.add_get("/", self.handle_index))
        cors.add(self.app.router.add_get("/ws", self.handle_websocket))
        cors.add(self.app.router.add_get("/metrics", self.handle_metrics))
        cors.add(self.app.router.add_get("/system_overview", self.handle_system_overview))
        cors.add(self.app.router.add_get("/performance_trends", self.handle_performance_trends))
        cors.add(self.app.router.add_get("/environmental_dashboard", self.handle_environmental_dashboard))
        
        # Serve static files
        self.app.router.add_static('/static', 'static')
        
    async def start(self):
        """Start the dashboard server."""
        self.monitor.start_monitoring()
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        self.logger.info(f"Dashboard server started at http://{self.host}:{self.port}")
        
        # Start metrics broadcasting
        asyncio.create_task(self.broadcast_metrics())
        
    async def handle_index(self, request: web.Request) -> web.Response:
        """Handle index page request."""
        with open('static/index.html', 'r') as f:
            content = f.read()
        return web.Response(text=content, content_type='text/html')
        
    async def handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Handle websocket connection."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websockets.add(ws)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    if msg.data == 'close':
                        await ws.close()
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
        finally:
            self.websockets.remove(ws)
            
        return ws
        
    async def handle_metrics(self, request: web.Request) -> web.Response:
        """Handle metrics request."""
        metrics = self.monitor.get_system_health()
        return web.json_response(metrics)
        
    async def handle_system_overview(self, request: web.Request) -> web.Response:
        """Handle system overview request."""
        overview = self.dashboard.create_system_overview()
        return web.json_response(overview)
        
    async def handle_performance_trends(self, request: web.Request) -> web.Response:
        """Handle performance trends request."""
        trends = self.dashboard.create_performance_trends()
        return web.json_response(trends)
        
    async def handle_environmental_dashboard(self, request: web.Request) -> web.Response:
        """Handle environmental dashboard request."""
        env_dashboard = self.dashboard.create_environmental_dashboard()
        return web.json_response(env_dashboard)
        
    async def broadcast_metrics(self):
        """Broadcast metrics to connected clients."""
        while True:
            try:
                # Get latest metrics
                metrics = self.monitor.get_system_health()
                self.dashboard.update_metrics(metrics)
                
                # Broadcast to all connected clients
                message = json.dumps({
                    'type': 'metrics_update',
                    'data': metrics,
                    'timestamp': datetime.now().isoformat()
                })
                
                for ws in self.websockets:
                    await ws.send_str(message)
                    
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                self.logger.error(f"Error broadcasting metrics: {e}")
                await asyncio.sleep(1)
