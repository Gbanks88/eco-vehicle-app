#!/usr/bin/env python3
"""CAD Viewer Server."""

from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__)

# Serve static files
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# API endpoints
@app.route('/api/models')
def list_models():
    """List available CAD models."""
    models_dir = os.path.join(os.path.dirname(__file__), 'static', 'models')
    models = []
    if os.path.exists(models_dir):
        models = [f for f in os.listdir(models_dir) if f.endswith('.json')]
    return jsonify(models)

@app.route('/api/model/<model_name>')
def get_model(model_name):
    """Get specific model data."""
    model_path = os.path.join(os.path.dirname(__file__), 'static', 'models', model_name)
    if os.path.exists(model_path):
        with open(model_path, 'r') as f:
            return jsonify(f.read())
    return jsonify({'error': 'Model not found'}), 404

if __name__ == '__main__':
    app.run(port=8081)
