"""Component visualization for the monitoring dashboard."""

from typing import Dict, List, Optional
import plotly.graph_objs as go
from ..modeling.uml.diagrams.component import (
    ComponentDiagramGenerator,
    Component,
    ComponentType,
    Interface,
    InterfaceType
)
from ..modeling.uml.core import Model

class MonitoringComponentVisualizer:
    """Visualize system components and their relationships."""
    
    def __init__(self):
        self.model = Model("Eco Vehicle Monitoring")
        self.diagram_gen = ComponentDiagramGenerator(self.model)
        self._setup_components()
        
    def _setup_components(self):
        """Setup the monitoring system components."""
        # Create main components
        monitoring = Component(
            name="Monitoring System",
            component_type=ComponentType.SUBSYSTEM
        )
        
        dashboard = Component(
            name="Dashboard",
            component_type=ComponentType.COMPONENT
        )
        
        metrics = Component(
            name="Metrics Collector",
            component_type=ComponentType.COMPONENT
        )
        
        analyzer = Component(
            name="Performance Analyzer",
            component_type=ComponentType.COMPONENT
        )
        
        env_monitor = Component(
            name="Environmental Monitor",
            component_type=ComponentType.COMPONENT
        )
        
        # Create interfaces
        metrics_interface = Interface(
            name="IMetrics",
            interface_type=InterfaceType.PROVIDED,
            operations=["collect_metrics()", "process_metrics()"]
        )
        
        analysis_interface = Interface(
            name="IAnalysis",
            interface_type=InterfaceType.PROVIDED,
            operations=["analyze_performance()", "detect_anomalies()"]
        )
        
        env_interface = Interface(
            name="IEnvironmental",
            interface_type=InterfaceType.PROVIDED,
            operations=["monitor_impact()", "calculate_score()"]
        )
        
        # Add interfaces to components
        metrics.provided_interfaces.append(metrics_interface)
        analyzer.provided_interfaces.append(analysis_interface)
        env_monitor.provided_interfaces.append(env_interface)
        
        dashboard.required_interfaces.extend([
            metrics_interface,
            analysis_interface,
            env_interface
        ])
        
        # Add components to subsystem
        monitoring.subcomponents.extend([
            dashboard,
            metrics,
            analyzer,
            env_monitor
        ])
        
        # Add to diagram generator
        self.diagram_gen.add_component(monitoring)
        
    def create_component_view(self, health_metrics: Dict[str, float]) -> go.Figure:
        """Create interactive component visualization."""
        # Create base figure
        fig = go.Figure()
        
        # Add component nodes
        components = self._get_component_nodes()
        for comp in components:
            fig.add_trace(go.Scatter(
                x=[comp['x']],
                y=[comp['y']],
                mode='markers+text',
                name=comp['name'],
                text=[comp['name']],
                textposition='bottom center',
                marker=dict(
                    size=30,
                    color=self._get_component_color(comp['name'], health_metrics),
                    symbol='square',
                    line=dict(width=2, color='black')
                ),
                hovertemplate=(
                    f"Component: {comp['name']}<br>"
                    f"Type: {comp['type']}<br>"
                    f"Status: %{marker.color}<br>"
                    f"<extra></extra>"
                )
            ))
            
        # Add relationship lines
        for rel in self._get_component_relations():
            fig.add_trace(go.Scatter(
                x=[rel['x0'], rel['x1']],
                y=[rel['y0'], rel['y1']],
                mode='lines',
                line=dict(color='black', dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))
            
        # Update layout
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        
        return fig
        
    def _get_component_nodes(self) -> List[Dict]:
        """Get component node positions."""
        # Simplified layout - in practice would use proper graph layout algorithm
        return [
            {'name': 'Dashboard', 'type': 'Component', 'x': 0, 'y': 0},
            {'name': 'Metrics Collector', 'type': 'Component', 'x': -1, 'y': 1},
            {'name': 'Performance Analyzer', 'type': 'Component', 'x': 0, 'y': 1},
            {'name': 'Environmental Monitor', 'type': 'Component', 'x': 1, 'y': 1}
        ]
        
    def _get_component_relations(self) -> List[Dict]:
        """Get component relationships."""
        return [
            {'x0': 0, 'y0': 0, 'x1': -1, 'y1': 1},
            {'x0': 0, 'y0': 0, 'x1': 0, 'y1': 1},
            {'x0': 0, 'y0': 0, 'x1': 1, 'y1': 1}
        ]
        
    def _get_component_color(self, component: str, metrics: Dict[str, float]) -> str:
        """Get component color based on health metrics."""
        if 'cpu_usage' in metrics and component == 'Metrics Collector':
            return 'green' if metrics['cpu_usage'] < 80 else 'red'
        elif 'memory_usage' in metrics and component == 'Performance Analyzer':
            return 'green' if metrics['memory_usage'] < 90 else 'red'
        elif 'environmental_score' in metrics and component == 'Environmental Monitor':
            return 'green' if metrics['environmental_score'] > 70 else 'red'
        return 'blue'  # Default color
