"""Demo script to run the monitoring dashboard."""

import asyncio
import logging
from aiohttp import web
from src.monitoring.dashboard import DashboardServer

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    """Run the dashboard server."""
    server = DashboardServer(host='localhost', port=8080)
    
    try:
        # Start the server and metrics broadcast
        await server.start()
        print(f"Dashboard running at http://{server.host}:{server.port}")
        
        # Keep the server running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
