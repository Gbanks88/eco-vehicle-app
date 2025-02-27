#!/usr/bin/env python3
"""Real-time monitoring dashboard for the eco-vehicle system."""

from flask import Flask, render_template_string
from flask_socketio import SocketIO
import json
import random
import time
from threading import Thread
import logging

app = Flask(__name__)
socketio = SocketIO(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML template with real-time updates
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Eco-Vehicle Monitoring Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .card {
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 8px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .status { font-weight: bold; }
        .warning { color: orange; }
        .error { color: red; }
        .normal { color: green; }
    </style>
</head>
<body>
    <h1>Eco-Vehicle Monitoring Dashboard</h1>
    
    <div class="grid">
        <div class="card">
            <h2>Power Management</h2>
            <p>State: <span id="power-state" class="status">-</span></p>
            <p>Voltage: <span id="voltage">-</span> V</p>
            <p>Current: <span id="current">-</span> A</p>
            <div id="power-chart"></div>
        </div>
        
        <div class="card">
            <h2>Environmental Metrics</h2>
            <p>CO2 Level: <span id="co2">-</span> ppm</p>
            <p>NOx Level: <span id="nox">-</span> ppm</p>
            <p>Efficiency: <span id="efficiency">-</span> kWh/100km</p>
            <div id="emissions-chart"></div>
        </div>
        
        <div class="card">
            <h2>System Status</h2>
            <p>Operating Mode: <span id="mode" class="status">-</span></p>
            <p>Temperature: <span id="temp">-</span>°C</p>
            <p>Health Status: <span id="health" class="status">-</span></p>
        </div>
        
        <div class="card">
            <h2>Alerts</h2>
            <div id="alerts"></div>
        </div>
    </div>

    <script>
        const socket = io();
        let powerData = {time: [], voltage: [], current: []};
        let emissionsData = {time: [], co2: [], nox: []};
        
        // Initialize charts
        Plotly.newPlot('power-chart', [
            {name: 'Voltage', y: [], mode: 'lines', line: {color: '#2196F3'}},
            {name: 'Current', y: [], mode: 'lines', line: {color: '#4CAF50'}}
        ], {margin: {t: 0, b: 30, l: 30, r: 30}, height: 200});
        
        Plotly.newPlot('emissions-chart', [
            {name: 'CO2', y: [], mode: 'lines', line: {color: '#FF5722'}},
            {name: 'NOx', y: [], mode: 'lines', line: {color: '#9C27B0'}}
        ], {margin: {t: 0, b: 30, l: 30, r: 30}, height: 200});

        socket.on('metrics_update', function(data) {
            // Update power metrics
            document.getElementById('power-state').textContent = data.power_state;
            document.getElementById('voltage').textContent = data.voltage.toFixed(1);
            document.getElementById('current').textContent = data.current.toFixed(1);
            
            // Update environmental metrics
            document.getElementById('co2').textContent = data.co2.toFixed(1);
            document.getElementById('nox').textContent = data.nox.toFixed(1);
            document.getElementById('efficiency').textContent = data.efficiency.toFixed(2);
            
            // Update system status
            document.getElementById('mode').textContent = data.mode;
            document.getElementById('temp').textContent = data.temperature.toFixed(1);
            document.getElementById('health').textContent = data.health;
            
            // Update charts
            const time = new Date().toLocaleTimeString();
            
            Plotly.extendTraces('power-chart', {
                y: [[data.voltage], [data.current]]
            }, [0, 1]);
            
            Plotly.extendTraces('emissions-chart', {
                y: [[data.co2], [data.nox]]
            }, [0, 1]);
            
            // Keep charts showing last 50 points
            if (powerData.time.length > 50) {
                Plotly.relayout('power-chart', {
                    xaxis: {range: [powerData.time.length-50, powerData.time.length]}
                });
                Plotly.relayout('emissions-chart', {
                    xaxis: {range: [emissionsData.time.length-50, emissionsData.time.length]}
                });
            }
        });

        socket.on('alert', function(data) {
            const alertsDiv = document.getElementById('alerts');
            const alertElem = document.createElement('p');
            alertElem.textContent = `${new Date().toLocaleTimeString()}: ${data.message}`;
            alertElem.className = data.level;
            alertsDiv.insertBefore(alertElem, alertsDiv.firstChild);
            
            // Keep only last 5 alerts
            if (alertsDiv.children.length > 5) {
                alertsDiv.removeChild(alertsDiv.lastChild);
            }
        });
    </script>
</body>
</html>
'''

class SystemSimulator:
    def __init__(self):
        self.power_states = ['STANDBY', 'POWER_ON', 'CHARGING']
        self.modes = ['NORMAL_POWER', 'ECO_POWER', 'HIGH_POWER']
        self.health_states = ['NORMAL', 'WARNING', 'FAULT']
        self.current_state = 'STANDBY'
        self.current_mode = 'NORMAL_POWER'
        self.current_health = 'NORMAL'
        
    def get_metrics(self):
        """Simulate system metrics."""
        # Simulate some realistic variations
        base_voltage = 48.0
        base_current = 10.0
        base_temp = 25.0
        base_co2 = 120.0
        base_nox = 40.0
        base_efficiency = 15.0
        
        # Add some random variations
        voltage = base_voltage + random.uniform(-2, 2)
        current = base_current + random.uniform(-1, 1)
        temperature = base_temp + random.uniform(-5, 5)
        co2 = base_co2 + random.uniform(-10, 10)
        nox = base_nox + random.uniform(-5, 5)
        efficiency = base_efficiency + random.uniform(-2, 2)
        
        # Occasionally change states
        if random.random() < 0.05:
            self.current_state = random.choice(self.power_states)
        if random.random() < 0.03:
            self.current_mode = random.choice(self.modes)
        if random.random() < 0.02:
            self.current_health = random.choice(self.health_states)
        
        return {
            'power_state': self.current_state,
            'voltage': voltage,
            'current': current,
            'temperature': temperature,
            'co2': co2,
            'nox': nox,
            'efficiency': efficiency,
            'mode': self.current_mode,
            'health': self.current_health
        }

simulator = SystemSimulator()

@app.route('/')
def index():
    """Render dashboard."""
    return render_template_string(DASHBOARD_HTML)

def emit_metrics():
    """Emit metrics periodically."""
    while True:
        metrics = simulator.get_metrics()
        socketio.emit('metrics_update', metrics)
        
        # Generate random alerts
        if random.random() < 0.1:
            alert_types = ['info', 'warning', 'error']
            alert_messages = [
                'System operating normally',
                'High power consumption detected',
                'Temperature approaching threshold',
                'CO2 levels elevated',
                'Switching to ECO mode',
                'Battery health check required'
            ]
            alert = {
                'level': random.choice(alert_types),
                'message': random.choice(alert_messages)
            }
            socketio.emit('alert', alert)
        
        time.sleep(1)

if __name__ == '__main__':
    # Start metrics emission in a background thread
    Thread(target=emit_metrics, daemon=True).start()
    socketio.run(app, debug=True, port=5000)
