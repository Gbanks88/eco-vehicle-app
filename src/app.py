from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from services.monitoring_service import MonitoringService
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)
monitoring_service = MonitoringService()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/monitoring')
def monitoring():
    return render_template('monitoring.html')

@socketio.on('get_metrics')
def handle_get_metrics():
    metrics = monitoring_service.get_system_metrics()
    emit('metrics_update', metrics)

def metrics_background_task():
    """Background task to emit metrics periodically"""
    while True:
        metrics = monitoring_service.get_system_metrics()
        socketio.emit('metrics_update', metrics)
        time.sleep(5)  # Update every 5 seconds

if __name__ == '__main__':
    # Start the background metrics task
    metrics_thread = threading.Thread(target=metrics_background_task)
    metrics_thread.daemon = True
    metrics_thread.start()
    
    # Start the Flask-SocketIO server
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
