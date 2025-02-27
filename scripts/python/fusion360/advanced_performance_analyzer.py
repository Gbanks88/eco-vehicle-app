"""
Advanced Car Performance Analyzer with Real-time Processing
"""
import numpy as np
import pandas as pd
from scipy import signal, integrate
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import time
import threading
import queue
from collections import deque
from scope_config import ENGINE_PARAMS, ANALYSIS_SETTINGS, DISPLAY_SETTINGS

class AdvancedPerformanceAnalyzer:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.metrics_queue = queue.Queue()
        self.running = False
        
        # Use deques for efficient history management
        self.history = {
            'time': deque(maxlen=1000),
            'rpm': deque(maxlen=1000),
            'speed': deque(maxlen=1000),
            'acceleration': deque(maxlen=1000),
            'power': deque(maxlen=1000),
        }
        
        # Performance metrics with proper initialization
        self.metrics = {
            'rpm': ENGINE_PARAMS['idle_rpm'],
            'speed': 0.0,
            'throttle': 0.0,
            'gear': 1,
            'acceleration': 0.0,
            'power': 0.0,
            'torque': 0.0,
            'fuel_flow': 0.0,
            'air_fuel_ratio': ENGINE_PARAMS['stoich_afr'],
            'boost_pressure': 0.0,
            'engine_load': 0.0,
            'engine_temp': ENGINE_PARAMS['optimal_temp'],
            'oil_pressure': ENGINE_PARAMS['optimal_oil_pressure'],
        }
        
        # Data validation ranges
        self.validation_ranges = {
            'rpm': (0, ENGINE_PARAMS['max_rpm']),
            'speed': (0, DISPLAY_SETTINGS['speed_max_scale']),
            'throttle': (0, 100),
            'gear': (1, 5),
            'boost_pressure': (0, ENGINE_PARAMS['max_boost']),
            'engine_temp': (0, ENGINE_PARAMS['max_temp']),
            'oil_pressure': (ENGINE_PARAMS['min_oil_pressure'], 
                           ENGINE_PARAMS['optimal_oil_pressure'] * 1.5)
        }
        
        # Initialize plots with dark theme
        plt.style.use(DISPLAY_SETTINGS['plot_style'])
        self.setup_plots()
        
    def validate_metric(self, name, value):
        """Validate metric values against defined ranges"""
        if name in self.validation_ranges:
            min_val, max_val = self.validation_ranges[name]
            return max(min_val, min(value, max_val))
        return value
        
    def setup_plots(self):
        """Initialize matplotlib plots with error handling"""
        try:
            self.fig = plt.figure(figsize=(15, 10))
            gs = self.fig.add_gridspec(3, 3)
            
            # Waveform plot
            self.ax_wave = self.fig.add_subplot(gs[0, :])
            self.ax_wave.set_title('Engine Signal')
            self.ax_wave.set_ylabel('Voltage (V)')
            self.wave_line, = self.ax_wave.plot([], [], 
                                              color=DISPLAY_SETTINGS['trace_color'],
                                              label='Raw Signal')
            self.ax_wave.grid(True, alpha=0.3)
            
            # RPM gauge
            self.ax_rpm = self.fig.add_subplot(gs[1, 0])
            self.ax_rpm.set_title('Engine RPM')
            self.rpm_text = self.ax_rpm.text(0.5, 0.5, str(self.metrics['rpm']), 
                                           horizontalalignment='center',
                                           verticalalignment='center',
                                           fontsize=20)
            self.ax_rpm.set_axis_off()
            
            # Speed gauge
            self.ax_speed = self.fig.add_subplot(gs[1, 1])
            self.ax_speed.set_title('Vehicle Speed')
            self.speed_text = self.ax_speed.text(0.5, 0.5, 
                                               f"{self.metrics['speed']:.1f} km/h", 
                                               horizontalalignment='center',
                                               verticalalignment='center',
                                               fontsize=20)
            self.ax_speed.set_axis_off()
            
            # Power/Torque plot
            self.ax_power = self.fig.add_subplot(gs[1, 2])
            self.ax_power.set_title('Power & Torque')
            self.power_line, = self.ax_power.plot([], [], 
                                                color='red',
                                                label='Power (kW)')
            self.torque_line, = self.ax_power.plot([], [],
                                                 color='blue',
                                                 label='Torque (Nm)')
            self.ax_power.grid(True, alpha=0.3)
            self.ax_power.legend()
            
            # Performance metrics
            self.ax_metrics = self.fig.add_subplot(gs[2, :])
            self.ax_metrics.set_title('Performance Metrics')
            self.metrics_table = self.ax_metrics.table(
                cellText=[[''] * 4] * 3,
                colLabels=['Engine', 'Performance', 'Temperature', 'Pressure'],
                loc='center'
            )
            self.ax_metrics.set_axis_off()
            
            plt.tight_layout()
            
        except Exception as e:
            print(f"Error setting up plots: {e}")
            raise
        
    def simulate_sensor_data(self):
        """Simulate engine sensor data with validation"""
        try:
            t = time.time()
            
            # Simulate engine RPM variation with smooth transitions
            base_rpm = 2000 + 1000 * np.sin(t * 0.5)
            rpm_noise = np.random.normal(0, 50)
            self.metrics['rpm'] = self.validate_metric('rpm',
                base_rpm + rpm_noise)
            
            # Calculate gear based on RPM with hysteresis
            current_gear = self.metrics['gear']
            target_gear = max(1, min(5, int(self.metrics['rpm'] / 1500)))
            if abs(target_gear - current_gear) >= 1:
                self.metrics['gear'] = target_gear
            
            # Simulate throttle position with rate limiting
            target_throttle = 40 + 30 * np.sin(t * 0.3)
            current_throttle = self.metrics['throttle']
            max_rate = 50  # Maximum 50% change per second
            dt = 0.1  # Assumed time step
            max_change = max_rate * dt
            throttle_change = np.clip(
                target_throttle - current_throttle,
                -max_change,
                max_change
            )
            self.metrics['throttle'] = self.validate_metric('throttle',
                current_throttle + throttle_change)
            
            # Calculate vehicle speed with transmission efficiency
            gear_ratio = ENGINE_PARAMS['gear_ratios'][self.metrics['gear']]
            final_drive = ENGINE_PARAMS['final_drive']
            efficiency = ENGINE_PARAMS['transmission_efficiency']
            wheel_rpm = (self.metrics['rpm'] * efficiency / 
                        (gear_ratio * final_drive))
            self.metrics['speed'] = self.validate_metric('speed',
                wheel_rpm * ENGINE_PARAMS['wheel_diameter'] * np.pi * 0.06)
            
            # Calculate power and torque with efficiency losses
            max_torque = ENGINE_PARAMS['max_torque']
            rpm_factor = self.metrics['rpm'] / ENGINE_PARAMS['torque_peak_rpm']
            torque_curve = np.sin(np.pi * rpm_factor)
            self.metrics['torque'] = (max_torque * torque_curve * 
                                    (self.metrics['throttle'] / 100))
            self.metrics['power'] = (self.metrics['torque'] * 
                                   self.metrics['rpm'] * 2 * np.pi / 60 / 1000)
            
            # Simulate other sensors with realistic behavior
            self.metrics['boost_pressure'] = self.validate_metric(
                'boost_pressure',
                max(0, -0.5 + self.metrics['throttle'] / 100))
            
            self.metrics['engine_load'] = self.metrics['throttle']
            
            fuel_factor = self.metrics['power'] * 0.25
            self.metrics['fuel_flow'] = max(0.1, fuel_factor)
            
            afr_base = ENGINE_PARAMS['stoich_afr']
            afr_variation = np.random.normal(0, 0.2)
            self.metrics['air_fuel_ratio'] = max(10, min(16, afr_base + afr_variation))
            
            oil_pressure_base = (ENGINE_PARAMS['optimal_oil_pressure'] * 
                               (0.5 + 0.5 * self.metrics['rpm'] / 
                                ENGINE_PARAMS['max_rpm']))
            self.metrics['oil_pressure'] = self.validate_metric(
                'oil_pressure',
                oil_pressure_base + np.random.normal(0, 2))
            
            temp_factor = self.metrics['power'] * 0.5
            self.metrics['engine_temp'] = self.validate_metric(
                'engine_temp',
                ENGINE_PARAMS['optimal_temp'] + temp_factor + np.random.normal(0, 1))
            
            # Generate waveform
            t_wave = np.linspace(0, 0.1, 1000)
            base_freq = self.metrics['rpm'] / 60 * ENGINE_PARAMS['cylinders'] / 2
            waveform = np.zeros_like(t_wave)
            
            # Add firing pulses for each cylinder
            for i, cylinder in enumerate(ENGINE_PARAMS['firing_order']):
                phase = 2 * np.pi * i / ENGINE_PARAMS['cylinders']
                waveform += np.sin(2 * np.pi * base_freq * t_wave + phase)
            
            # Add realistic noise and interference
            noise = np.random.normal(0, 0.1, size=len(t_wave))
            interference = 0.2 * np.sin(2 * np.pi * 50 * t_wave)  # 50Hz noise
            waveform = waveform + noise + interference
            
            return t_wave, waveform
            
        except Exception as e:
            print(f"Error simulating sensor data: {e}")
            return np.linspace(0, 0.1, 1000), np.zeros(1000)
        
    def update_plot(self, frame):
        """Update plot animation with error handling"""
        try:
            # Get new data
            t_wave, waveform = self.simulate_sensor_data()
            
            # Update waveform plot
            self.wave_line.set_data(t_wave, waveform)
            self.ax_wave.relim()
            self.ax_wave.autoscale_view()
            
            # Update RPM display with color coding
            rpm_color = DISPLAY_SETTINGS['normal_color']
            if self.metrics['rpm'] > ENGINE_PARAMS['redline']:
                rpm_color = DISPLAY_SETTINGS['alert_color']
            elif self.metrics['rpm'] > ENGINE_PARAMS['redline'] * 0.9:
                rpm_color = DISPLAY_SETTINGS['warning_color']
            
            self.rpm_text.set_text(f"{self.metrics['rpm']:.0f}")
            self.rpm_text.set_color(rpm_color)
            
            # Update speed display
            self.speed_text.set_text(f"{self.metrics['speed']:.1f} km/h")
            
            # Update power/torque plot
            rpm_range = np.linspace(0, ENGINE_PARAMS['max_rpm'], 100)
            power_curve = self.metrics['power'] * rpm_range / self.metrics['rpm']
            torque_curve = self.metrics['torque'] * np.ones_like(rpm_range)
            
            self.power_line.set_data(rpm_range, power_curve)
            self.torque_line.set_data(rpm_range, torque_curve)
            self.ax_power.relim()
            self.ax_power.autoscale_view()
            
            # Update metrics table with color coding
            cell_text = [
                [f"RPM: {self.metrics['rpm']:.0f}",
                 f"Power: {self.metrics['power']:.1f} kW",
                 f"Temp: {self.metrics['engine_temp']:.1f}°C",
                 f"Oil: {self.metrics['oil_pressure']:.1f} psi"],
                [f"Gear: {self.metrics['gear']}",
                 f"Torque: {self.metrics['torque']:.1f} Nm",
                 f"Load: {self.metrics['engine_load']:.1f}%",
                 f"Boost: {self.metrics['boost_pressure']:.2f} bar"],
                [f"Throttle: {self.metrics['throttle']:.1f}%",
                 f"Speed: {self.metrics['speed']:.1f} km/h",
                 f"AFR: {self.metrics['air_fuel_ratio']:.1f}",
                 f"Fuel: {self.metrics['fuel_flow']:.1f} l/h"]
            ]
            
            for i in range(len(cell_text)):
                for j in range(len(cell_text[0])):
                    cell = self.metrics_table[i+1, j]
                    cell.get_text().set_text(cell_text[i][j])
                    
                    # Color code based on thresholds
                    if (i == 0 and j == 2 and 
                        self.metrics['engine_temp'] > ENGINE_PARAMS['max_temp']):
                        cell.set_facecolor('red')
                    elif (i == 1 and j == 3 and 
                          self.metrics['boost_pressure'] > ENGINE_PARAMS['max_boost']):
                        cell.set_facecolor('red')
                    else:
                        cell.set_facecolor('none')
            
            # Store historical data
            current_time = time.time()
            self.history['time'].append(current_time)
            self.history['rpm'].append(self.metrics['rpm'])
            self.history['speed'].append(self.metrics['speed'])
            self.history['power'].append(self.metrics['power'])
            
            return (self.wave_line, self.rpm_text, self.speed_text,
                    self.power_line, self.torque_line, self.metrics_table)
            
        except Exception as e:
            print(f"Error updating plot: {e}")
            return None
        
    def run(self):
        """Run the analyzer with proper cleanup"""
        try:
            self.running = True
            ani = FuncAnimation(self.fig, self.update_plot,
                              interval=DISPLAY_SETTINGS['update_interval'],
                              blit=True)
            plt.show()
        except Exception as e:
            print(f"Error running analyzer: {e}")
        finally:
            self.running = False
            plt.close('all')
    
    def stop(self):
        """Stop the analyzer gracefully"""
        self.running = False

def main():
    try:
        analyzer = AdvancedPerformanceAnalyzer()
        analyzer.run()
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        plt.close('all')

if __name__ == '__main__':
    main()
