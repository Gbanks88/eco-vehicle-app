#!/bin/bash

# Start data sync service
echo "Starting data sync service..."
python src/services/data_sync_service.py &

# Start monitoring service
echo "Starting monitoring service..."
python src/services/monitoring_service.py &

# Start analytics dashboard
echo "Starting analytics dashboard..."
python src/analytics/dashboard.py &

# Wait for all services to start
sleep 5

# Check service status
echo "Checking service status..."
curl -s http://localhost:5000/api/status

echo "All services started. Access the monitoring dashboard at http://localhost:5000"
