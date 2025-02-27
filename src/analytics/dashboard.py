#!/usr/bin/env python3
"""Analytics Dashboard for Eco-Vehicle System."""

from flask import Flask, render_template_string
from flask_socketio import SocketIO
import json
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path
from .predictor import VehiclePredictor, RealTimeOptimizer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize predictors with different models
predictors = {
    'random_forest': VehiclePredictor(),
    'gradient_boost': VehiclePredictor(model_type='gradient_boost'),
    'neural_net': VehiclePredictor(model_type='neural_net')
}

optimizer = RealTimeOptimizer(predictors['random_forest'])

@app.route('/analytics')
def analytics_dashboard():
    """Render analytics dashboard."""
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>CG4F Analytics Platform</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { 
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f0f2f5;
                }
                .dashboard-grid {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .card {
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .header {
                    background: #1a73e8;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }
                .metric {
                    font-size: 24px;
                    font-weight: bold;
                    color: #1a73e8;
                }
                .prediction-card {
                    grid-column: span 2;
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                }
                .model-comparison {
                    display: flex;
                    gap: 20px;
                    margin-top: 10px;
                }
                .model-metric {
                    flex: 1;
                    padding: 10px;
                    border-radius: 5px;
                    background: #f8f9fa;
                }
                .recommendations {
                    background: #e8f0fe;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                .chart-container {
                    height: 300px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Eco-Vehicle Analytics Dashboard</h1>
            </div>
            
            <div class="dashboard-grid">
                <div class="card">
                    <h2>Efficiency Prediction</h2>
                    <div class="chart-container" id="efficiency-chart"></div>
                    <div class="model-comparison">
                        <div class="model-metric">
                            <h4>Random Forest</h4>
                            <div id="rf-accuracy"></div>
                        </div>
                        <div class="model-metric">
                            <h4>Gradient Boost</h4>
                            <div id="gb-accuracy"></div>
                        </div>
                        <div class="model-metric">
                            <h4>Neural Network</h4>
                            <div id="nn-accuracy"></div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Parameter Optimization</h2>
                    <div class="chart-container" id="optimization-chart"></div>
                    <div class="recommendations" id="optimization-recommendations">
                    </div>
                </div>
                
                <div class="card">
                    <h2>Pattern Analysis</h2>
                    <div class="chart-container" id="pattern-chart"></div>
                </div>
                
                <div class="card">
                    <h2>Real-time Metrics</h2>
                    <div class="chart-container" id="metrics-chart"></div>
                </div>
            </div>

            <script>
                const socket = io();
                let efficiencyData = [];
                let optimizationData = [];
                let patternData = [];
                
                // Initialize charts
                const efficiencyChart = Plotly.newPlot('efficiency-chart', [{
                    y: [],
                    name: 'Actual',
                    type: 'scatter'
                }, {
                    y: [],
                    name: 'Predicted',
                    type: 'scatter'
                }], {
                    title: 'Efficiency Over Time',
                    height: 300,
                    margin: { t: 30, b: 30, l: 30, r: 30 }
                });
                
                const optimizationChart = Plotly.newPlot('optimization-chart', [{
                    z: [[]], 
                    type: 'heatmap',
                    colorscale: 'Viridis'
                }], {
                    title: 'Parameter Optimization Map',
                    height: 300,
                    margin: { t: 30, b: 50, l: 50, r: 30 }
                });
                
                const patternChart = Plotly.newPlot('pattern-chart', [{
                    y: [],
                    type: 'bar'
                }], {
                    title: 'Hourly Efficiency Patterns',
                    height: 300,
                    margin: { t: 30, b: 30, l: 30, r: 30 }
                });
                
                const metricsChart = Plotly.newPlot('metrics-chart', [{
                    y: [],
                    name: 'Voltage',
                    type: 'scatter'
                }, {
                    y: [],
                    name: 'Current',
                    type: 'scatter'
                }, {
                    y: [],
                    name: 'Temperature',
                    type: 'scatter'
                }], {
                    title: 'System Metrics',
                    height: 300,
                    margin: { t: 30, b: 30, l: 30, r: 30 }
                });

                socket.on('analytics_update', function(data) {
                    // Update efficiency predictions
                    Plotly.extendTraces('efficiency-chart', {
                        y: [[data.actual_efficiency], [data.predicted_efficiency]]
                    }, [0, 1]);
                    
                    // Update model accuracies
                    document.getElementById('rf-accuracy').textContent = 
                        `Accuracy: ${(data.model_accuracies.random_forest * 100).toFixed(1)}%`;
                    document.getElementById('gb-accuracy').textContent = 
                        `Accuracy: ${(data.model_accuracies.gradient_boost * 100).toFixed(1)}%`;
                    document.getElementById('nn-accuracy').textContent = 
                        `Accuracy: ${(data.model_accuracies.neural_net * 100).toFixed(1)}%`;
                    
                    // Update optimization heatmap
                    Plotly.update('optimization-chart', {
                        z: [data.optimization_map]
                    });
                    
                    // Update recommendations
                    const recsDiv = document.getElementById('optimization-recommendations');
                    recsDiv.innerHTML = data.recommendations.map(rec => 
                        `<p><strong>${rec.type}:</strong> ${rec.message}</p>`
                    ).join('');
                    
                    // Update pattern analysis
                    if (data.patterns) {
                        Plotly.update('pattern-chart', {
                            x: [Object.keys(data.patterns)],
                            y: [Object.values(data.patterns)]
                        });
                    }
                    
                    // Update metrics
                    Plotly.extendTraces('metrics-chart', {
                        y: [[data.metrics.voltage], [data.metrics.current], [data.metrics.temperature]]
                    }, [0, 1, 2]);
                });
            </script>
        </body>
        </html>
    ''')

def generate_mock_data():
    """Generate mock data for testing."""
    while True:
        data = {
            'actual_efficiency': np.random.normal(15, 2),
            'predicted_efficiency': np.random.normal(15, 1.5),
            'model_accuracies': {
                'random_forest': np.random.uniform(0.85, 0.95),
                'gradient_boost': np.random.uniform(0.83, 0.93),
                'neural_net': np.random.uniform(0.80, 0.90)
            },
            'optimization_map': np.random.rand(10, 10).tolist(),
            'recommendations': [
                {
                    'type': 'Parameter Optimization',
                    'message': 'Increase voltage by 0.5V for optimal efficiency'
                },
                {
                    'type': 'Timing',
                    'message': 'Current time period shows historically high efficiency'
                }
            ],
            'patterns': {
                f'{i:02d}:00': np.random.normal(15, 2) for i in range(24)
            },
            'metrics': {
                'voltage': np.random.normal(48, 1),
                'current': np.random.normal(10, 2),
                'temperature': np.random.normal(25, 3)
            }
        }
        socketio.emit('analytics_update', data)
        time.sleep(1)

if __name__ == '__main__':
    # Start mock data generation in background
    threading.Thread(target=generate_mock_data, daemon=True).start()
    
    # Start server
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
