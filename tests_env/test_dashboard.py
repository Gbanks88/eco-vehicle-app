"""Tests for the monitoring dashboard server."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import asyncio
from aiohttp import web
import aiohttp
import json
from src.monitoring.dashboard import DashboardServer

@pytest.fixture
async def server():
    """Create test server."""
    return DashboardServer()

@pytest.fixture
async def app(server):
    """Create test application."""
    return server.app

@pytest.fixture
async def client(app):
    """Create test client."""
    async with aiohttp.ClientSession() as session:
        yield session

@pytest.mark.asyncio
async def test_dashboard_server(server, client):
    """Test dashboard server endpoints."""
    server = await server
    client = await anext(client)
    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    
    # Test index page
    async with client.get('http://localhost:8080/') as resp:
        assert resp.status == 200
        text = await resp.text()
        assert 'Eco Vehicle Monitoring Dashboard' in text
    
    # Test metrics endpoint
    async with client.get('http://localhost:8080/metrics') as resp:
        assert resp.status == 200
        data = await resp.json()
        assert isinstance(data, dict)
    
    # Test system overview endpoint
    async with client.get('http://localhost:8080/system_overview') as resp:
        assert resp.status == 200
        data = await resp.json()
        assert isinstance(data, dict)
        assert 'data' in data
        assert 'layout' in data
    
    # Test performance trends endpoint
    async with client.get('http://localhost:8080/performance_trends') as resp:
        assert resp.status == 200
        data = await resp.json()
        assert isinstance(data, dict)
        assert 'data' in data
        assert 'layout' in data
    
    # Test environmental dashboard endpoint
    async with client.get('http://localhost:8080/environmental_dashboard') as resp:
        assert resp.status == 200
        data = await resp.json()
        assert isinstance(data, dict)
        assert 'data' in data
        assert 'layout' in data
        
    # Cleanup
    await runner.cleanup()

@pytest.mark.asyncio
async def test_websocket(server, client):
    """Test websocket connection and messaging."""
    server = await server
    client = await anext(client)
    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8081)
    await site.start()
    
    try:
        # Start the server's metrics broadcast
        broadcast_task = asyncio.create_task(server.broadcast_metrics())
        
        # Connect to websocket
        async with client.ws_connect('ws://localhost:8081/ws') as ws:
            # Wait for a metrics update
            msg = await ws.receive_json(timeout=5)
            assert msg['type'] == 'metrics_update'
            assert 'data' in msg
            assert 'timestamp' in msg
    finally:
        # Cancel broadcast task and cleanup
        broadcast_task.cancel()
        try:
            await broadcast_task
        except asyncio.CancelledError:
            pass
        await runner.cleanup()
    
@pytest.mark.asyncio
async def test_metrics_broadcast(server):
    """Test metrics broadcasting to multiple clients."""
    server = await server
    
    # Create mock websockets
    class MockWebSocket:
        def __init__(self):
            self.messages = []
            
        async def send_str(self, message):
            self.messages.append(message)
            
        async def close(self):
            pass
    
    try:
        # Add mock clients
        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        server.websockets.add(ws1)
        server.websockets.add(ws2)
        
        # Start broadcast task
        broadcast_task = asyncio.create_task(server.broadcast_metrics())
        
        # Wait briefly for broadcast to happen
        await asyncio.sleep(1)
        
        # Check that both clients received the message
        assert len(ws1.messages) == 1
        assert len(ws2.messages) == 1
        
        # Verify message format
        msg1 = json.loads(ws1.messages[0])
        assert msg1['type'] == 'metrics_update'
        assert 'data' in msg1
        assert 'timestamp' in msg1
    finally:
        # Clean up
        broadcast_task.cancel()
        try:
            await broadcast_task
        except asyncio.CancelledError:
            pass
        await ws1.close()
        await ws2.close()
        server.websockets.clear()
