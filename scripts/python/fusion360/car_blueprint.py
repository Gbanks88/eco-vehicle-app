"""
Interactive Eco-Friendly Vehicle Blueprint Generator
Features PowerPack™ battery system, environmental systems, and detailed specifications
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, PathPatch, FancyBboxPatch
from matplotlib.path import Path
import matplotlib.transforms as transforms
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

# Enhanced specifications with detailed technical data
ECO_CAR_SPECS = {
    'dimensions': {
        'length': 4800,        # mm
        'width': 1850,         # mm
        'height': 1400,        # mm
        'wheelbase': 2850,     # mm
        'ground_clearance': 160,  # mm
        'drag_coefficient': 0.21,
        'frontal_area': 2.2,   # m²
        'cargo_volume': 500,   # L
        'turning_radius': 5.2, # m
    },
    'powerpack': {
        'module_capacity': 10,  # kWh
        'module_weight': 35,    # kg
        'max_modules': 5,
        'swap_time': 2,        # minutes
        'cooling_capacity': 8,  # kW
        'peak_charge': 150,    # kW
        'cell_type': 'LiFePO4',
        'cell_config': '96s2p',
        'thermal_range': [-20, 45],  # °C
        'cycle_life': 3000,
    },
    'environmental': {
        'o2_generation': 35,    # % above ambient
        'co2_capture': 2.5,    # kg/day
        'air_processing': 4000, # m³/h
        'filtration': 99.99,   # %
        'particulate_size': 0.1,  # μm
        'nox_reduction': 95,    # %
        'voc_removal': 98,     # %
        'urban_cooling': 5,    # kW
        'clean_radius': 50,    # m
    },
    'performance': {
        'range': 300,          # miles
        'peak_power': 350,     # kW
        'efficiency': 95,      # %
        'acceleration': 4.5,   # 0-60 mph
        'top_speed': 155,      # mph
        'motor_type': 'PMSM',
        'motor_cooling': 'liquid',
        'regeneration': 100,   # kW
        'power_density': 4.2,  # kW/kg
    },
    'safety': {
        'airbags': 8,
        'crash_rating': 5,     # stars
        'battery_protection': 'titanium alloy',
        'thermal_monitoring': 'distributed fiber optic',
        'emergency_systems': ['fire suppression', 'cell isolation', 'rapid discharge'],
        'structural_integrity': 'carbon fiber monocoque',
    },
    'materials': {
        'body': 'recycled carbon fiber',
        'chassis': 'aluminum alloy',
        'battery_enclosure': 'titanium composite',
        'interior': 'recycled materials',
        'recyclability': 98,   # %
        'carbon_footprint': -2000,  # kg CO2/year
    }
}

class InteractiveEcoCarBlueprint:
    def __init__(self, specs=None):
        self.specs = specs or ECO_CAR_SPECS
        self.app = dash.Dash(__name__)
        self.setup_layout()
        
    def setup_layout(self):
        """Create interactive dashboard layout"""
        self.app.layout = html.Div([
            html.H1('Eco-Friendly Vehicle Technical Blueprint'),
            
            # View selector
            dcc.Dropdown(
                id='view-selector',
                options=[
                    {'label': 'Side View', 'value': 'side'},
                    {'label': 'Top View', 'value': 'top'},
                    {'label': 'Front View', 'value': 'front'},
                    {'label': '3D View', 'value': '3d'}
                ],
                value='side'
            ),
            
            # System selector
            dcc.Checklist(
                id='system-selector',
                options=[
                    {'label': 'PowerPack™ System', 'value': 'powerpack'},
                    {'label': 'Environmental Systems', 'value': 'environmental'},
                    {'label': 'Safety Systems', 'value': 'safety'},
                    {'label': 'Performance Metrics', 'value': 'performance'}
                ],
                value=['powerpack', 'environmental']
            ),
            
            # Main display
            dcc.Graph(id='blueprint-display'),
            
            # Specifications panel
            html.Div([
                html.H3('Technical Specifications'),
                html.Div(id='specs-display')
            ]),
            
            # Interactive features
            html.Div([
                html.H3('Interactive Features'),
                dcc.Slider(
                    id='battery-modules',
                    min=1,
                    max=5,
                    step=1,
                    value=3,
                    marks={i: f'{i} Modules' for i in range(1, 6)}
                ),
                html.Div(id='range-display'),
                
                dcc.Slider(
                    id='environmental-power',
                    min=0,
                    max=100,
                    step=10,
                    value=50,
                    marks={i: f'{i}%' for i in range(0, 101, 10)}
                ),
                html.Div(id='environmental-impact')
            ])
        ])
        
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """Setup interactive callbacks"""
        @self.app.callback(
            [Output('blueprint-display', 'figure'),
             Output('specs-display', 'children'),
             Output('range-display', 'children'),
             Output('environmental-impact', 'children')],
            [Input('view-selector', 'value'),
             Input('system-selector', 'value'),
             Input('battery-modules', 'value'),
             Input('environmental-power', 'value')]
        )
        def update_display(view, systems, modules, env_power):
            # Create appropriate view
            if view == '3d':
                fig = self.create_3d_view(systems)
            else:
                fig = self.create_2d_view(view, systems)
            
            # Update specifications based on selections
            specs_html = self.generate_specs_html(systems, modules, env_power)
            
            # Calculate range based on battery modules
            range_text = f"Estimated Range: {modules * 60} miles"
            
            # Calculate environmental impact
            impact = self.calculate_environmental_impact(env_power)
            impact_text = f"Environmental Impact: {impact}"
            
            return fig, specs_html, range_text, impact_text
    
    def create_3d_view(self, systems):
        """Create interactive 3D view"""
        fig = go.Figure(data=[
            go.Surface(
                contours = {
                    "x": {"show": True, "start": 0, "end": self.specs['dimensions']['length'], "size": 500},
                    "y": {"show": True, "start": 0, "end": self.specs['dimensions']['width'], "size": 500},
                    "z": {"show": True, "start": 0, "end": self.specs['dimensions']['height'], "size": 500}
                },
                colorscale='Viridis'
            )
        ])
        
        fig.update_layout(
            scene = {
                "aspectratio": {"x": 1, "y": 0.5, "z": 0.3},
                "camera": {"eye": {"x": 1.5, "y": 1.5, "z": 1.5}}
            },
            title = "3D Vehicle Model"
        )
        
        return fig
    
    def create_2d_view(self, view, systems):
        """Create detailed 2D view"""
        fig = go.Figure()
        
        # Add base vehicle outline
        outline_coords = self.get_outline_coords(view)
        fig.add_trace(go.Scatter(
            x=outline_coords['x'],
            y=outline_coords['y'],
            mode='lines',
            name='Vehicle Outline'
        ))
        
        # Add selected systems
        if 'powerpack' in systems:
            self.add_powerpack_visualization(fig, view)
        if 'environmental' in systems:
            self.add_environmental_visualization(fig, view)
        
        fig.update_layout(
            title=f"{view.capitalize()} View",
            showlegend=True,
            width=800,
            height=600
        )
        
        return fig
    
    def get_outline_coords(self, view):
        """Get coordinates for vehicle outline"""
        dims = self.specs['dimensions']
        
        if view == 'side':
            return {
                'x': [0, dims['length']],
                'y': [0, dims['height']]
            }
        elif view == 'top':
            return {
                'x': [0, dims['length']],
                'y': [-dims['width']/2, dims['width']/2]
            }
        else:  # front
            return {
                'x': [-dims['width']/2, dims['width']/2],
                'y': [0, dims['height']]
            }
    
    def add_powerpack_visualization(self, fig, view):
        """Add PowerPack™ system visualization"""
        if view == 'side':
            # Add battery modules
            for i in range(self.specs['powerpack']['max_modules']):
                fig.add_shape(
                    type="rect",
                    x0=self.specs['dimensions']['length']*0.4 + i*100,
                    y0=self.specs['dimensions']['ground_clearance']*2,
                    x1=self.specs['dimensions']['length']*0.4 + i*100 + 80,
                    y1=self.specs['dimensions']['ground_clearance']*2 + 150,
                    line=dict(color="red", width=2, dash="dash"),
                )
    
    def add_environmental_visualization(self, fig, view):
        """Add environmental systems visualization"""
        if view == 'front':
            # Add air processing unit
            fig.add_shape(
                type="rect",
                x0=-self.specs['dimensions']['width']/4,
                y0=self.specs['dimensions']['ground_clearance']*2,
                x1=self.specs['dimensions']['width']/4,
                y1=self.specs['dimensions']['ground_clearance']*2 + self.specs['dimensions']['height']*0.2,
                line=dict(color="green", width=2, dash="dash"),
            )
    
    def generate_specs_html(self, systems, modules, env_power):
        """Generate HTML for specifications display"""
        specs_list = []
        
        if 'powerpack' in systems:
            specs_list.extend([
                html.H4('PowerPack™ System'),
                html.Ul([
                    html.Li(f"Total Capacity: {modules * self.specs['powerpack']['module_capacity']} kWh"),
                    html.Li(f"Swap Time: {self.specs['powerpack']['swap_time']} minutes"),
                    html.Li(f"Cooling: {self.specs['powerpack']['cooling_capacity']} kW"),
                    html.Li(f"Cell Type: {self.specs['powerpack']['cell_type']}")
                ])
            ])
        
        if 'environmental' in systems:
            impact = self.calculate_environmental_impact(env_power)
            specs_list.extend([
                html.H4('Environmental Systems'),
                html.Ul([
                    html.Li(f"O2 Generation: {self.specs['environmental']['o2_generation']}%"),
                    html.Li(f"CO2 Capture: {self.specs['environmental']['co2_capture']} kg/day"),
                    html.Li(f"Air Processing: {self.specs['environmental']['air_processing']} m³/h"),
                    html.Li(f"Environmental Impact: {impact}")
                ])
            ])
        
        return html.Div(specs_list)
    
    def calculate_environmental_impact(self, power_level):
        """Calculate environmental impact based on power level"""
        base_co2 = self.specs['materials']['carbon_footprint']
        impact = base_co2 * (power_level/100)
        return f"{impact:.0f} kg CO2/year"
    
    def run_server(self, debug=True):
        """Run the interactive dashboard"""
        self.app.run_server(debug=debug)

def main():
    blueprint = InteractiveEcoCarBlueprint()
    blueprint.run_server()

if __name__ == '__main__':
    main()
