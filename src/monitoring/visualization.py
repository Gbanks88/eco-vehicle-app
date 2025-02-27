"""Real-time visualization components for system monitoring."""

import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json

from .component_viz import MonitoringComponentVisualizer

class MonitoringDashboard:
    """Real-time monitoring dashboard."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.alert_history: List[Dict] = []
        self.max_history_points = 1000
        self.component_viz = MonitoringComponentVisualizer()
        
    def update_metrics(self, metrics: Dict[str, float], timestamp: Optional[datetime] = None):
        """Update metrics history."""
        if timestamp is None:
            timestamp = datetime.now()
            
        for metric, value in metrics.items():
            if metric not in self.metrics_history:
                self.metrics_history[metric] = []
            
            self.metrics_history[metric].append((timestamp, value))
            
            # Maintain history size
            if len(self.metrics_history[metric]) > self.max_history_points:
                self.metrics_history[metric].pop(0)
                
    def add_alert(self, alert_type: str, message: str, severity: str = 'warning'):
        """Add alert to history."""
        alert = {
            'timestamp': datetime.now(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }
        self.alert_history.append(alert)
        
        # Keep last 100 alerts
        if len(self.alert_history) > 100:
            self.alert_history.pop(0)
            
    def create_system_overview(self) -> dict:
        """Create system overview visualization."""
        # Create subplot figure
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                'System Components',
                'Component Health',
                'CPU Usage (%)',
                'Memory Usage (%)',
                'Network Latency (ms)',
                'Battery Level (%)',
                'Environmental Impact',
                'Alerts'
            ),
            specs=[
                [{'type': 'xy'}, {'type': 'xy'}],
                [{'type': 'xy'}, {'type': 'xy'}],
                [{'type': 'xy'}, {'type': 'xy'}],
                [{'type': 'indicator'}, {'type': 'table'}]
            ],
            vertical_spacing=0.12
        )
        
        # Add component visualization
        latest_metrics = {}
        for metric in ['cpu_usage', 'memory_usage', 'environmental_score']:
            if metric in self.metrics_history and self.metrics_history[metric]:
                latest_metrics[metric] = self.metrics_history[metric][-1][1]
        
        component_fig = self.component_viz.create_component_view(latest_metrics)
        for trace in component_fig.data:
            fig.add_trace(trace, row=1, col=1)
        
        # Add metric traces
        metrics_map = {
            'cpu_usage': (2, 1),
            'memory_usage': (2, 2),
            'network_latency': (3, 1),
            'battery_level': (3, 2)
        }
        
        for metric, (row, col) in metrics_map.items():
            if metric in self.metrics_history:
                times, values = zip(*self.metrics_history[metric])
                fig.add_trace(
                    go.Scatter(
                        x=times,
                        y=values,
                        name=metric.replace('_', ' ').title(),
                        line=dict(width=2)
                    ),
                    row=row, col=col
                )
                
        # Add environmental impact gauge
        if 'environmental_score' in self.metrics_history:
            _, scores = zip(*self.metrics_history['environmental_score'])
            current_score = scores[-1] if scores else 0
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=current_score * 100,
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': self._get_score_color(current_score)},
                        'steps': [
                            {'range': [0, 33], 'color': "red"},
                            {'range': [33, 66], 'color': "yellow"},
                            {'range': [66, 100], 'color': "green"}
                        ]
                    }
                ),
                row=3, col=1
            )
            
        # Add recent alerts
        alert_text = self._format_alerts()
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Time', 'Type', 'Message'],
                    font=dict(size=12),
                    align="left"
                ),
                cells=dict(
                    values=alert_text,
                    font=dict(size=11),
                    align="left"
                )
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="System Monitoring Dashboard",
            title_x=0.5
        )
        
        return json.loads(fig.to_json())
        
    def create_performance_trends(self) -> dict:
        """Create performance trends visualization."""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(
                'System Metrics Trends',
                'Performance Distribution'
            ),
            specs=[[{"type": "scatter"}],
                  [{"type": "box"}]]
        )
        
        # Add trend lines
        for metric in ['cpu_usage', 'memory_usage', 'network_latency']:
            if metric in self.metrics_history:
                times, values = zip(*self.metrics_history[metric])
                
                # Calculate trend
                x = np.arange(len(values))
                z = np.polyfit(x, values, 1)
                p = np.poly1d(z)
                
                fig.add_trace(
                    go.Scatter(
                        x=times,
                        y=values,
                        name=metric.replace('_', ' ').title(),
                        mode='lines',
                        line=dict(width=1)
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=[times[0], times[-1]],
                        y=[p(0), p(len(values)-1)],
                        name=f"{metric.replace('_', ' ').title()} Trend",
                        line=dict(dash='dash', width=1)
                    ),
                    row=1, col=1
                )
                
                # Add box plot
                fig.add_trace(
                    go.Box(
                        y=values,
                        name=metric.replace('_', ' ').title(),
                        boxpoints='outliers'
                    ),
                    row=2, col=1
                )
                
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="System Performance Analysis",
            title_x=0.5
        )
        
        return json.loads(fig.to_json())
        
    def create_environmental_dashboard(self) -> dict:
        """Create environmental metrics dashboard."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Air Quality Metrics',
                'Emissions Analysis',
                'Environmental Score Trend',
                'Impact Distribution'
            )
        )
        
        # Air quality metrics
        air_metrics = ['co2_level', 'co_level', 'nox_level', 'pm25_level', 'pm10_level']
        for metric in air_metrics:
            if metric in self.metrics_history:
                times, values = zip(*self.metrics_history[metric])
                fig.add_trace(
                    go.Scatter(
                        x=times,
                        y=values,
                        name=metric.replace('_', ' ').title(),
                        line=dict(width=1)
                    ),
                    row=1, col=1
                )
                
        # Emissions analysis
        if 'emissions' in self.metrics_history:
            times, values = zip(*self.metrics_history['emissions'])
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=values,
                    name='Emissions',
                    fill='tozeroy'
                ),
                row=1, col=2
            )
            
        # Environmental score trend
        if 'environmental_score' in self.metrics_history:
            times, values = zip(*self.metrics_history['environmental_score'])
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=values,
                    name='Environmental Score',
                    line=dict(color='green', width=2)
                ),
                row=2, col=1
            )
            
        # Impact distribution
        if 'environmental_score' in self.metrics_history:
            _, values = zip(*self.metrics_history['environmental_score'])
            fig.add_trace(
                go.Histogram(
                    x=values,
                    name='Score Distribution',
                    nbinsx=20
                ),
                row=2, col=2
            )
            
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="Environmental Impact Dashboard",
            title_x=0.5
        )
        
        return json.loads(fig.to_json())
        
    def _format_alerts(self) -> List[List]:
        """Format recent alerts for display."""
        times = []
        types = []
        messages = []
        
        for alert in reversed(self.alert_history[-5:]):  # Show last 5 alerts
            times.append(alert['timestamp'].strftime('%H:%M:%S'))
            types.append(alert['type'])
            messages.append(alert['message'])
            
        return [times, types, messages]
        
    def _get_score_color(self, score: float) -> str:
        """Get color based on score."""
        if score >= 0.66:
            return "green"
        elif score >= 0.33:
            return "yellow"
        return "red"
