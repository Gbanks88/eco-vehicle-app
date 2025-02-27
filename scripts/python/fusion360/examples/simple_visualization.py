"""
Simple visualization example to demonstrate design concepts
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon, Arc
from matplotlib.transforms import Affine2D
import math

def create_parametric_design(outer_radius=3.0, inner_radius=1.5, pattern_count=6):
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    
    # Set limits
    limit = outer_radius * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    
    # Draw hexagon
    hexagon = RegularPolygon((0, 0), pattern_count, 
                            radius=outer_radius,
                            orientation=0,
                            fill=False,
                            color='blue',
                            linewidth=2)
    ax.add_patch(hexagon)
    
    # Draw inner circle
    inner_circle = Circle((0, 0), inner_radius,
                         fill=False,
                         color='red',
                         linewidth=2)
    ax.add_patch(inner_circle)
    
    # Add pattern circles
    for i in range(pattern_count):
        angle = 2 * math.pi * i / pattern_count
        x = 2.0 * math.cos(angle)
        y = 2.0 * math.sin(angle)
        pattern_circle = Circle((x, y), 0.3,
                              fill=True,
                              color='lightblue',
                              alpha=0.5)
        ax.add_patch(pattern_circle)
    
    # Add connecting arcs
    for i in range(0, pattern_count, 2):
        angle = 2 * math.pi * i / pattern_count
        start_angle = math.degrees(angle - math.pi/6)
        end_angle = math.degrees(angle + math.pi/6)
        
        arc = Arc((0, 0), 
                 outer_radius*1.2, outer_radius*1.2,
                 theta1=start_angle,
                 theta2=end_angle,
                 color='green',
                 linewidth=2)
        ax.add_patch(arc)
    
    # Add construction lines
    for i in range(pattern_count):
        angle = 2 * math.pi * i / pattern_count
        x = outer_radius * math.cos(angle)
        y = outer_radius * math.sin(angle)
        ax.plot([0, x], [0, y], 'gray', linestyle='--', alpha=0.5)
    
    # Add dimensions
    ax.plot([-outer_radius, outer_radius], [-outer_radius*1.3, -outer_radius*1.3],
            'k-', linewidth=1)
    ax.plot([-outer_radius, -outer_radius], [-outer_radius*1.25, -outer_radius*1.35],
            'k-', linewidth=1)
    ax.plot([outer_radius, outer_radius], [-outer_radius*1.25, -outer_radius*1.35],
            'k-', linewidth=1)
    ax.text(0, -outer_radius*1.4, f'Width: {outer_radius*2:.1f} units',
            horizontalalignment='center')
    
    # Add title and parameter info
    ax.set_title('Parametric Design Visualization', pad=20)
    param_text = f'Parameters:\n' \
                 f'Outer Radius: {outer_radius:.1f}\n' \
                 f'Inner Radius: {inner_radius:.1f}\n' \
                 f'Pattern Count: {pattern_count}'
    ax.text(limit*0.7, limit*0.7, param_text,
            bbox=dict(facecolor='white', alpha=0.8))
    
    # Remove axis for cleaner look
    ax.set_axis_off()
    
    return fig

def main():
    # Create design with default parameters
    fig = create_parametric_design()
    
    # Create design with custom parameters
    fig_custom = create_parametric_design(
        outer_radius=4.0,
        inner_radius=2.0,
        pattern_count=8
    )
    
    # Show the designs
    plt.show()

if __name__ == '__main__':
    main()
