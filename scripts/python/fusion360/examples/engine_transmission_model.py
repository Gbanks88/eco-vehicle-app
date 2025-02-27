"""
Engine and Transmission System Visualization
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
import matplotlib.transforms as transforms
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import math

class EngineTransmissionVisualizer:
    def __init__(self):
        self.fig = plt.figure(figsize=(15, 10))
        self.ax_side = self.fig.add_subplot(121)  # Side view
        self.ax_top = self.fig.add_subplot(122)   # Top view
        
        # Set equal aspect ratio
        self.ax_side.set_aspect('equal')
        self.ax_top.set_aspect('equal')
        
        # Remove axis for cleaner look
        self.ax_side.set_axis_off()
        self.ax_top.set_axis_off()
        
        # Set titles
        self.ax_side.set_title('Engine & Transmission - Side View')
        self.ax_top.set_title('Engine & Transmission - Top View')
        
        # Parameters
        self.engine_length = 4
        self.engine_width = 3
        self.engine_height = 3
        self.transmission_length = 2
        self.cylinder_radius = 0.4
        self.cylinder_count = 4
        
    def draw_engine_block_side(self):
        # Main engine block
        engine_block = Rectangle((-self.engine_length/2, 0),
                               self.engine_length,
                               self.engine_height,
                               fill=True,
                               color='gray',
                               alpha=0.5)
        self.ax_side.add_patch(engine_block)
        
        # Crankshaft
        crankshaft = Rectangle((-self.engine_length/2, 0.5),
                             self.engine_length,
                             0.3,
                             fill=True,
                             color='darkgray')
        self.ax_side.add_patch(crankshaft)
        
        # Cylinders
        for i in range(self.cylinder_count):
            x = -self.engine_length/3 + i * self.engine_length/2
            cylinder = Rectangle((x, 1),
                               0.3,
                               self.engine_height-1,
                               fill=True,
                               color='lightgray')
            self.ax_side.add_patch(cylinder)
            
        # Transmission housing
        trans_x = self.engine_length/2
        transmission = Rectangle((trans_x, 0),
                               self.transmission_length,
                               self.engine_height*0.8,
                               fill=True,
                               color='darkgray',
                               alpha=0.5)
        self.ax_side.add_patch(transmission)
        
    def draw_engine_block_top(self):
        # Main engine block
        engine_block = Rectangle((-self.engine_length/2, -self.engine_width/2),
                               self.engine_length,
                               self.engine_width,
                               fill=True,
                               color='gray',
                               alpha=0.5)
        self.ax_top.add_patch(engine_block)
        
        # Cylinders from top
        for i in range(self.cylinder_count):
            x = -self.engine_length/3 + i * self.engine_length/2
            cylinder = Circle((x, 0),
                            self.cylinder_radius,
                            fill=True,
                            color='lightgray')
            self.ax_top.add_patch(cylinder)
            
        # Transmission housing
        trans_x = self.engine_length/2
        transmission = Rectangle((trans_x, -self.engine_width/3),
                               self.transmission_length,
                               self.engine_width*2/3,
                               fill=True,
                               color='darkgray',
                               alpha=0.5)
        self.ax_top.add_patch(transmission)
        
    def add_dimensions(self):
        # Side view dimensions
        self.ax_side.plot([-self.engine_length/2, self.engine_length/2 + self.transmission_length],
                         [-0.5, -0.5], 'k-', linewidth=1)
        self.ax_side.text(0, -0.8, f'Total Length: {self.engine_length + self.transmission_length:.1f} units',
                         horizontalalignment='center')
        
        # Height dimension
        self.ax_side.plot([-self.engine_length/2 - 0.5, -self.engine_length/2 - 0.5],
                         [0, self.engine_height], 'k-', linewidth=1)
        self.ax_side.text(-self.engine_length/2 - 0.8, self.engine_height/2,
                         f'Height:\n{self.engine_height:.1f} units',
                         verticalalignment='center')
        
        # Top view dimensions
        self.ax_top.plot([-self.engine_length/2, -self.engine_length/2],
                        [-self.engine_width/2 - 0.5, self.engine_width/2 + 0.5],
                        'k-', linewidth=1)
        self.ax_top.text(-self.engine_length/2 - 0.3, 0,
                        f'Width:\n{self.engine_width:.1f} units',
                        horizontalalignment='right')
        
    def add_labels(self):
        # Engine components
        self.ax_side.text(-self.engine_length/4, self.engine_height + 0.3,
                         'Engine Block',
                         horizontalalignment='center')
        self.ax_side.text(self.engine_length/2 + self.transmission_length/2,
                         self.engine_height + 0.3,
                         'Transmission',
                         horizontalalignment='center')
        self.ax_side.text(-self.engine_length/4, 0.3,
                         'Crankshaft',
                         horizontalalignment='center')
        
        # Add parameters text
        params_text = f'Parameters:\n' \
                     f'Engine Length: {self.engine_length:.1f}\n' \
                     f'Engine Width: {self.engine_width:.1f}\n' \
                     f'Engine Height: {self.engine_height:.1f}\n' \
                     f'Transmission Length: {self.transmission_length:.1f}\n' \
                     f'Cylinder Count: {self.cylinder_count}'
        self.ax_top.text(self.engine_length/2 + self.transmission_length + 0.5,
                        self.engine_width/2,
                        params_text,
                        bbox=dict(facecolor='white', alpha=0.8))
        
    def render(self):
        # Set view limits
        limit_x = (self.engine_length + self.transmission_length) * 0.7
        limit_y = self.engine_height * 1.2
        
        self.ax_side.set_xlim(-limit_x, limit_x)
        self.ax_side.set_ylim(-1, limit_y)
        self.ax_top.set_xlim(-limit_x, limit_x)
        self.ax_top.set_ylim(-limit_y, limit_y)
        
        # Draw components
        self.draw_engine_block_side()
        self.draw_engine_block_top()
        self.add_dimensions()
        self.add_labels()
        
        plt.tight_layout()
        plt.show()

def main():
    visualizer = EngineTransmissionVisualizer()
    visualizer.render()

if __name__ == '__main__':
    main()
