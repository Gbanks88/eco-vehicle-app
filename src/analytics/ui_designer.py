#!/usr/bin/env python3
"""UI Designer for Analytics Dashboard."""

from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO
import json
from pathlib import Path
import logging
import os

app = Flask(__name__)
socketio = SocketIO(app)
logger = logging.getLogger(__name__)

class UIDesigner:
    def __init__(self):
        self.config_dir = Path(__file__).parent / 'ui_configs'
        self.config_dir.mkdir(exist_ok=True)
        self.current_config = self._load_default_config()
    
    def _load_default_config(self):
        """Load default UI configuration."""
        return {
            'theme': {
                'primary_color': '#1a73e8',
                'secondary_color': '#e8f0fe',
                'background_color': '#f0f2f5',
                'text_color': '#202124',
                'accent_color': '#fbbc04'
            },
            'layout': {
                'grid_columns': 2,
                'card_spacing': '20px',
                'card_padding': '20px',
                'border_radius': '10px'
            },
            'components': {
                'efficiency_chart': {
                    'enabled': True,
                    'position': {'row': 1, 'col': 1},
                    'size': {'width': 1, 'height': 1},
                    'title': 'Efficiency Prediction',
                    'chart_type': 'line'
                },
                'optimization_chart': {
                    'enabled': True,
                    'position': {'row': 1, 'col': 2},
                    'size': {'width': 1, 'height': 1},
                    'title': 'Parameter Optimization',
                    'chart_type': 'heatmap'
                },
                'pattern_chart': {
                    'enabled': True,
                    'position': {'row': 2, 'col': 1},
                    'size': {'width': 1, 'height': 1},
                    'title': 'Pattern Analysis',
                    'chart_type': 'bar'
                },
                'metrics_chart': {
                    'enabled': True,
                    'position': {'row': 2, 'col': 2},
                    'size': {'width': 1, 'height': 1},
                    'title': 'Real-time Metrics',
                    'chart_type': 'line'
                }
            },
            'fonts': {
                'main': 'Arial, sans-serif',
                'headers': 'Arial, sans-serif',
                'charts': 'Arial, sans-serif'
            },
            'animations': {
                'enabled': True,
                'duration': '0.3s',
                'type': 'ease-in-out'
            }
        }
    
    def save_config(self, name, config):
        """Save UI configuration."""
        config_path = self.config_dir / f'{name}.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved UI configuration: {name}")
    
    def load_config(self, name):
        """Load UI configuration."""
        config_path = self.config_dir / f'{name}.json'
        if config_path.exists():
            with open(config_path) as f:
                self.current_config = json.load(f)
            logger.info(f"Loaded UI configuration: {name}")
            return self.current_config
        return None
    
    def list_configs(self):
        """List available configurations."""
        return [f.stem for f in self.config_dir.glob('*.json')]
    
    def generate_css(self):
        """Generate CSS from current configuration."""
        theme = self.current_config['theme']
        layout = self.current_config['layout']
        fonts = self.current_config['fonts']
        animations = self.current_config['animations']
        
        return f'''
            :root {{
                --primary-color: {theme['primary_color']};
                --secondary-color: {theme['secondary_color']};
                --background-color: {theme['background_color']};
                --text-color: {theme['text_color']};
                --accent-color: {theme['accent_color']};
            }}
            
            body {{
                font-family: {fonts['main']};
                background: var(--background-color);
                color: var(--text-color);
                margin: 0;
                padding: 20px;
            }}
            
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat({layout['grid_columns']}, 1fr);
                gap: {layout['card_spacing']};
                margin-bottom: 20px;
            }}
            
            .card {{
                background: white;
                border-radius: {layout['border_radius']};
                padding: {layout['card_padding']};
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: all {animations['duration']} {animations['type']};
            }}
            
            .header {{
                background: var(--primary-color);
                color: white;
                padding: 20px;
                border-radius: {layout['border_radius']};
                margin-bottom: 20px;
                font-family: {fonts['headers']};
            }}
        '''

# Initialize UI designer
designer = UIDesigner()

@app.route('/designer')
def ui_designer():
    """Render UI designer interface."""
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>CG4F Analytics Designer</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/vue@2.6.14"></script>
            <link href="https://cdn.jsdelivr.net/npm/@mdi/font@6.5.95/css/materialdesignicons.min.css" rel="stylesheet">
            <style>
                [v-cloak] { display: none; }
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .designer-grid {
                    display: grid;
                    grid-template-columns: 300px 1fr;
                    gap: 20px;
                }
                .sidebar {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .preview {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .color-picker {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin-bottom: 10px;
                }
                .color-preview {
                    width: 30px;
                    height: 30px;
                    border-radius: 5px;
                    border: 1px solid #ddd;
                }
                .section {
                    margin-bottom: 20px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #eee;
                }
                .component-card {
                    padding: 10px;
                    margin-bottom: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    cursor: move;
                }
                .btn {
                    background: var(--primary-gradient);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-bottom: 10px;
                }
                .btn:hover { background: #1557b0; }
                input, select {
                    width: 100%;
                    padding: 8px;
                    margin-bottom: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div id="app" v-cloak>
                <div class="header">
                    <h1>CG4F Analytics Designer</h1>
                    <p class="subtitle">Customize Your Analytics Experience</p>
                </div>
                <div class="designer-grid">
                    <div class="sidebar">
                        <div class="section">
                            <h3>Saved Configurations</h3>
                            <button class="btn" @click="saveConfig">Save Current</button>
                            <select v-model="selectedConfig" @change="loadConfig">
                                <option v-for="config in savedConfigs" :value="config">
                                    {% raw %}{{ config }}{% endraw %}
                                </option>
                            </select>
                        </div>
                        
                        <div class="section">
                            <h3>Theme</h3>
                            <div v-for="(color, name) in config.theme" class="color-picker">
                                <label>{% raw %}{{ name }}{% endraw %}</label>
                                <div class="color-preview" :style="{ background: color }"></div>
                                <input type="color" v-model="config.theme[name]" @change="updatePreview">
                            </div>
                        </div>
                        
                        <div class="section">
                            <h3>Layout</h3>
                            <label>Grid Columns</label>
                            <input type="number" v-model="config.layout.grid_columns" @change="updatePreview">
                            
                            <label>Card Spacing</label>
                            <input type="text" v-model="config.layout.card_spacing" @change="updatePreview">
                            
                            <label>Border Radius</label>
                            <input type="text" v-model="config.layout.border_radius" @change="updatePreview">
                        </div>
                        
                        <div class="section">
                            <h3>Components</h3>
                            <div v-for="(comp, name) in config.components" class="component-card">
                                <label>
                                    <input type="checkbox" v-model="comp.enabled" @change="updatePreview">
                                    {% raw %}{{ comp.title }}{% endraw %}
                                </label>
                                <div v-if="comp.enabled">
                                    <label>Position</label>
                                    <input type="number" v-model="comp.position.row" placeholder="Row">
                                    <input type="number" v-model="comp.position.col" placeholder="Column">
                                    
                                    <label>Chart Type</label>
                                    <select v-model="comp.chart_type" @change="updatePreview">
                                        <option value="line">Line</option>
                                        <option value="bar">Bar</option>
                                        <option value="heatmap">Heatmap</option>
                                        <option value="scatter">Scatter</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="section">
                            <h3>Animations</h3>
                            <label>
                                <input type="checkbox" v-model="config.animations.enabled" @change="updatePreview">
                                Enable Animations
                            </label>
                            <div v-if="config.animations.enabled">
                                <label>Duration</label>
                                <input type="text" v-model="config.animations.duration" @change="updatePreview">
                                
                                <label>Type</label>
                                <select v-model="config.animations.type" @change="updatePreview">
                                    <option value="ease">Ease</option>
                                    <option value="ease-in">Ease In</option>
                                    <option value="ease-out">Ease Out</option>
                                    <option value="ease-in-out">Ease In Out</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="preview">
                        <h2>Preview</h2>
                        <div id="preview-content"></div>
                    </div>
                </div>
            </div>

            <script>
                const socket = io();
                
                new Vue({
                    el: '#app',
                    data: {
                        config: null,
                        savedConfigs: [],
                        selectedConfig: '',
                        previewHtml: ''
                    },
                    mounted() {
                        this.loadInitialConfig();
                        this.loadSavedConfigs();
                        
                        socket.on('config_updated', (data) => {
                            this.previewHtml = data.html;
                            document.getElementById('preview-content').innerHTML = this.previewHtml;
                        });
                    },
                    methods: {
                        loadInitialConfig() {
                            fetch('/api/config/default')
                                .then(response => response.json())
                                .then(data => {
                                    this.config = data;
                                    this.updatePreview();
                                });
                        },
                        loadSavedConfigs() {
                            fetch('/api/configs')
                                .then(response => response.json())
                                .then(data => {
                                    this.savedConfigs = data;
                                });
                        },
                        saveConfig() {
                            const name = prompt('Enter configuration name:');
                            if (name) {
                                fetch('/api/config/save', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({
                                        name: name,
                                        config: this.config
                                    })
                                }).then(() => this.loadSavedConfigs());
                            }
                        },
                        loadConfig() {
                            if (this.selectedConfig) {
                                fetch(`/api/config/load/${this.selectedConfig}`)
                                    .then(response => response.json())
                                    .then(data => {
                                        this.config = data;
                                        this.updatePreview();
                                    });
                            }
                        },
                        updatePreview() {
                            socket.emit('update_preview', this.config);
                        }
                    }
                });
            </script>
        </body>
        </html>
    ''')

@app.route('/api/config/default')
def get_default_config():
    """Get default configuration."""
    return jsonify(designer.current_config)

@app.route('/api/configs')
def get_configs():
    """Get list of saved configurations."""
    return jsonify(designer.list_configs())

@app.route('/api/config/save', methods=['POST'])
def save_config():
    """Save configuration."""
    data = request.json
    designer.save_config(data['name'], data['config'])
    return jsonify({'status': 'success'})

@app.route('/api/config/load/<name>')
def load_config(name):
    """Load configuration."""
    config = designer.load_config(name)
    if config:
        return jsonify(config)
    return jsonify({'error': 'Configuration not found'}), 404

@socketio.on('update_preview')
def handle_preview_update(config):
    """Handle preview updates."""
    designer.current_config = config
    css = designer.generate_css()
    
    # Generate preview HTML
    preview_html = f'''
        <style>{css}</style>
        <div class="dashboard-grid">
    '''
    
    # Add enabled components
    for name, comp in config['components'].items():
        if comp['enabled']:
            preview_html += f'''
                <div class="card" style="
                    grid-row: {comp['position']['row']};
                    grid-column: {comp['position']['col']};
                    grid-column-end: span {comp['size']['width']};
                    grid-row-end: span {comp['size']['height']};
                ">
                    <h3>{comp['title']}</h3>
                    <div class="chart-container">
                        [Chart: {comp['chart_type']}]
                    </div>
                </div>
            '''
    
    preview_html += '</div>'
    
    socketio.emit('config_updated', {
        'html': preview_html
    })

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)
