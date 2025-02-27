from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import os
import redis
from flask_socketio import SocketIO

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

# Configure Redis
redis_url = os.getenv('REDIS_URL')
if redis_url:
    redis_client = redis.Redis.from_url(redis_url)
else:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Initialize SocketIO
socketio = SocketIO(app)

# Forge API configuration
FORGE_CLIENT_ID = os.environ.get('FORGE_CLIENT_ID')
FORGE_CLIENT_SECRET = os.environ.get('FORGE_CLIENT_SECRET')
FORGE_CALLBACK_URL = os.environ.get('FORGE_CALLBACK_URL')
MODEL_DERIVATIVE_API = os.environ.get('MODEL_DERIVATIVE_API_URL')
FORGE_BUCKET_KEY = os.environ.get('FORGE_BUCKET_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vehicle_viewer')
def vehicle_viewer():
    return render_template('vehicle_viewer.html')

@app.route('/health')
def health_check():
    try:
        # Check Redis connection
        redis_status = 'healthy' if redis_client.ping() else 'unhealthy'
        
        # Check Forge credentials
        forge_status = 'healthy' if all([FORGE_CLIENT_ID, FORGE_CLIENT_SECRET]) else 'missing_credentials'
        
        # Basic app health status
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'redis': redis_status,
                'forge': forge_status
            }
        }
        return jsonify(health_data)
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)
