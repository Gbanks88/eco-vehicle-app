#!/usr/bin/env python3
"""Dashboard Server for Eco-Vehicle System."""

from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO
import json
import random
import time
from threading import Thread
import logging
from pathlib import Path

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Load configuration
config_path = Path(__file__).parent / 'config.json'
with open(config_path) as f:
    config = json.load(f)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardServer:
    def __init__(self):
        self.power_states = ['STANDBY', 'POWER_ON', 'CHARGING']
        self.modes = ['NORMAL_POWER', 'ECO_POWER', 'HIGH_POWER']
        self.current_state = 'STANDBY'
        self.current_mode = 'NORMAL_POWER'
        
    def get_system_metrics(self):
        """Get current system metrics."""
        return {
            'power_state': self.current_state,
            'mode': self.current_mode,
            'voltage': 48.0 + random.uniform(-2, 2),
            'current': 10.0 + random.uniform(-1, 1),
            'temperature': 25.0 + random.uniform(-5, 5),
            'emissions': {
                'co2': 120.0 + random.uniform(-10, 10),
                'nox': 40.0 + random.uniform(-5, 5)
            },
            'efficiency': 15.0 + random.uniform(-2, 2)
        }

# Create dashboard instance
dashboard = DashboardServer()

@app.route('/')
def index():
    """Render dashboard interface."""
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Eco-Vehicle Dashboard</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
                .card {
                    border: 1px solid #ddd;
                    padding: 20px;
                    border-radius: 8px;
                    background: white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .header {
                    background: #2196F3;
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }
                .metric { font-size: 24px; font-weight: bold; }
                .label { color: #666; }
                .chart { height: 300px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Eco-Vehicle System Dashboard</h1>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h2>Power Management</h2>
                    <div class="metric" id="power-state">-</div>
                    <div class="label">Current State</div>
                    <div class="chart" id="power-chart"></div>
                </div>
                
                <div class="card">
                    <h2>Environmental Impact</h2>
                    <div class="metric" id="emissions">-</div>
                    <div class="label">CO2 Emissions (ppm)</div>
                    <div class="chart" id="emissions-chart"></div>
                </div>
                
                <div class="card">
                    <h2>System Performance</h2>
                    <div class="metric" id="efficiency">-</div>
                    <div class="label">Energy Efficiency (kWh/100km)</div>
                    <div class="chart" id="performance-chart"></div>
                </div>
                
                <div class="card">
                    <h2>Alerts & Notifications</h2>
                    <div id="alerts"></div>
                </div>
            </div>

            <script>
                const socket = io();
                let powerData = [];
                let emissionsData = [];
                let efficiencyData = [];
                
                // Initialize charts
                const powerChart = Plotly.newPlot('power-chart', [{
                    y: [],
                    type: 'line',
                    name: 'Voltage'
                }], {
                    title: 'Power Consumption',
                    height: 250,
                    margin: { t: 30, b: 30, l: 30, r: 30 }
                });
                
                const emissionsChart = Plotly.newPlot('emissions-chart', [{
                    y: [],
                    type: 'line',
                    name: 'CO2'
                }], {
                    title: 'Emissions',
                    height: 250,
                    margin: { t: 30, b: 30, l: 30, r: 30 }
                });
                
                const performanceChart = Plotly.newPlot('performance-chart', [{
                    y: [],
                    type: 'line',
                    name: 'Efficiency'
                }], {
                    title: 'System Performance',
                    height: 250,
                    margin: { t: 30, b: 30, l: 30, r: 30 }
                });

                socket.on('metrics_update', function(data) {
                    // Update metrics
                    document.getElementById('power-state').textContent = data.power_state;
                    document.getElementById('emissions').textContent = data.emissions.co2.toFixed(1);
                    document.getElementById('efficiency').textContent = data.efficiency.toFixed(2);
                    
                    // Update charts
                    Plotly.extendTraces('power-chart', {
                        y: [[data.voltage]]
                    }, [0]);
                    
                    Plotly.extendTraces('emissions-chart', {
                        y: [[data.emissions.co2]]
                    }, [0]);
                    
                    Plotly.extendTraces('performance-chart', {
                        y: [[data.efficiency]]
                    }, [0]);
                    
                    // Keep charts showing last 50 points
                    if (powerData.length > 50) {
                        Plotly.relayout('power-chart', {
                            xaxis: {range: [powerData.length-50, powerData.length]}
                        });
                    }
                });

                socket.on('alert', function(data) {
                    const alertsDiv = document.getElementById('alerts');
                    const alertElem = document.createElement('div');
                    alertElem.textContent = `${new Date().toLocaleTimeString()}: ${data.message}`;
                    alertElem.style.color = data.level === 'error' ? 'red' : 
                                          data.level === 'warning' ? 'orange' : 'green';
                    alertsDiv.insertBefore(alertElem, alertsDiv.firstChild);
                    
                    if (alertsDiv.children.length > 5) {
                        alertsDiv.removeChild(alertsDiv.lastChild);
                    }
                });
            </script>
        </body>
        </html>
    ''')

def emit_metrics():
    """Emit system metrics periodically."""
    while True:
        metrics = dashboard.get_system_metrics()
        socketio.emit('metrics_update', metrics)
        
        # Simulate random alerts
        if random.random() < 0.1:
            alert_types = ['info', 'warning', 'error']
            alert_messages = [
                'System operating normally',
                'Power consumption spike detected',
                'Temperature approaching threshold',
                'Switching to ECO mode',
                'Battery optimization in progress'
            ]
            alert = {
                'level': random.choice(alert_types),
                'message': random.choice(alert_messages)
            }
            socketio.emit('alert', alert)
        
        time.sleep(1)

if __name__ == '__main__':
    # Start metrics emission in background
    Thread(target=emit_metrics, daemon=True).start()
    
    # Start server
    port = config.get('port', 5000)
    debug = config.get('debug', True)
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)
