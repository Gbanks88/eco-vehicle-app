"""Main window for the Eco-Vehicle Monitoring System."""

import sys
from pathlib import Path
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QTabWidget, QPushButton,
    QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor, QFont
import pyqtgraph as pg
from ..monitoring.system_monitor import SystemMonitor
from ..monitoring.visualization import MonitoringDashboard

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eco-Vehicle Monitoring System")
        self.setMinimumSize(1200, 800)
        
        # Initialize monitoring systems
        self.monitor = SystemMonitor()
        self.dashboard = MonitoringDashboard()
        
        # Setup UI
        self.setup_ui()
        
        # Setup update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)  # Update every second
        
    def setup_ui(self):
        """Setup the user interface."""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Component tree and status
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Component status section
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QVBoxLayout(status_frame)
        
        status_label = QLabel("System Components")
        status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_layout.addWidget(status_label)
        
        self.component_labels = {}
        for component in ["Dashboard", "Metrics Collector", 
                         "Performance Analyzer", "Environmental Monitor"]:
            label = QLabel(f"● {component}: Operational")
            label.setFont(QFont("Arial", 10))
            self.component_labels[component] = label
            status_layout.addWidget(label)
            
        status_layout.addStretch()
        left_layout.addWidget(status_frame)
        
        # Right panel - Metrics and visualizations
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tab widget for different views
        tabs = QTabWidget()
        
        # System Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        # Create plots
        self.plots = {}
        plot_titles = {
            'cpu_usage': 'CPU Usage (%)',
            'memory_usage': 'Memory Usage (%)',
            'network_latency': 'Network Latency (ms)',
            'battery_level': 'Battery Level (%)'
        }
        
        for metric, title in plot_titles.items():
            plot_widget = pg.PlotWidget(title=title)
            plot_widget.setBackground('default')
            plot_widget.showGrid(x=True, y=True)
            self.plots[metric] = {
                'widget': plot_widget,
                'curve': plot_widget.plot(pen='b')
            }
            overview_layout.addWidget(plot_widget)
            
        tabs.addTab(overview_tab, "System Overview")
        
        # Environmental Impact tab
        env_tab = QWidget()
        env_layout = QVBoxLayout(env_tab)
        
        self.env_plot = pg.PlotWidget(title='Environmental Impact Score')
        self.env_plot.setBackground('default')
        self.env_plot.showGrid(x=True, y=True)
        self.env_curve = self.env_plot.plot(pen='g')
        
        env_layout.addWidget(self.env_plot)
        tabs.addTab(env_tab, "Environmental Impact")
        
        # Add tabs to right panel
        right_layout.addWidget(tabs)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
    def update_metrics(self):
        """Update displayed metrics."""
        metrics = self.monitor.collect_metrics()
        self.dashboard.update_metrics(metrics)
        
        # Update component status
        status_map = {
            'Dashboard': metrics.get('cpu_usage', 0) < 80,
            'Metrics Collector': metrics.get('memory_usage', 0) < 90,
            'Performance Analyzer': metrics.get('network_latency', 0) < 100,
            'Environmental Monitor': metrics.get('environmental_score', 0) > 70
        }
        
        for component, status in status_map.items():
            label = self.component_labels[component]
            if status:
                label.setText(f"● {component}: Operational")
                label.setStyleSheet("color: green")
            else:
                label.setText(f"● {component}: Warning")
                label.setStyleSheet("color: red")
        
        # Update plots
        for metric, plot_data in self.plots.items():
            if metric in self.dashboard.metrics_history:
                times, values = zip(*self.dashboard.metrics_history[metric][-100:])
                plot_data['curve'].setData(range(len(values)), values)
                
        # Update environmental plot
        if 'environmental_score' in self.dashboard.metrics_history:
            times, values = zip(*self.dashboard.metrics_history['environmental_score'][-100:])
            self.env_curve.setData(range(len(values)), values)
            
def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set dark theme palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
