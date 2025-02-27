"""
Oscilloscope Interface and Car Performance Simulation
"""
import pyvisa
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
from datetime import datetime
import time

class OscilloscopeInterface:
    def __init__(self):
        self.rm = pyvisa.ResourceManager('@py')
        self.scope = None
        self.sampling_rate = 1000000  # 1 MHz
        self.record_length = 1000
        
    def list_devices(self):
        """List all available USB devices"""
        devices = self.rm.list_resources()
        print("Available devices:")
        for device in devices:
            print(f"  - {device}")
        return devices
    
    def connect(self, resource_name=None):
        """Connect to oscilloscope"""
        try:
            if resource_name is None:
                # Try to find first USB device
                devices = self.list_devices()
                if not devices:
                    raise ValueError("No USB devices found")
                resource_name = devices[0]
            
            self.scope = self.rm.open_resource(resource_name)
            print(f"Connected to: {self.scope.query('*IDN?')}")
            
            # Configure scope settings
            self.scope.write("*RST")  # Reset
            self.scope.write("DAT:ENC RPB")  # Set encoding
            self.scope.write("DAT:WID 1")  # Set data width
            self.scope.write(f"HOR:RECO {self.record_length}")  # Set record length
            
            return True
            
        except Exception as e:
            print(f"Error connecting to oscilloscope: {e}")
            return False
    
    def configure_channels(self, channels=[1]):
        """Configure oscilloscope channels"""
        try:
            for ch in channels:
                self.scope.write(f"CH{ch}:COUP DC")  # DC coupling
                self.scope.write(f"CH{ch}:POS 0")    # Vertical position
                self.scope.write(f"CH{ch}:SCA 1")    # Vertical scale (V/div)
            return True
        except Exception as e:
            print(f"Error configuring channels: {e}")
            return False
    
    def acquire_waveform(self, channel=1):
        """Acquire waveform data from specified channel"""
        try:
            self.scope.write(f"DAT:SOU CH{channel}")
            self.scope.write("ACQ:STATE ON")  # Start acquisition
            time.sleep(0.1)  # Wait for acquisition
            
            # Get waveform data
            raw_data = self.scope.query_binary_values("CURV?")
            
            # Get scaling factors
            y_mult = float(self.scope.query("WFMP:YMULT?"))
            y_zero = float(self.scope.query("WFMP:YZERO?"))
            y_off = float(self.scope.query("WFMP:YOFF?"))
            
            # Scale data
            scaled_data = [(val - y_off) * y_mult + y_zero for val in raw_data]
            time_data = np.linspace(0, len(scaled_data)/self.sampling_rate, len(scaled_data))
            
            return time_data, scaled_data
            
        except Exception as e:
            print(f"Error acquiring waveform: {e}")
            return None, None

class CarPerformanceSimulator:
    def __init__(self):
        self.engine_rpm = 0
        self.vehicle_speed = 0
        self.throttle_position = 0
        self.gear_position = 1
        
    def analyze_engine_signal(self, time_data, voltage_data):
        """Analyze engine signal for RPM calculation"""
        try:
            # Use FFT to find dominant frequency
            fft = np.fft.fft(voltage_data)
            freqs = np.fft.fftfreq(len(time_data), time_data[1] - time_data[0])
            
            # Find peak frequency (excluding DC)
            peak_freq = abs(freqs[np.argmax(np.abs(fft[1:])) + 1])
            
            # Convert frequency to RPM (assuming 2 revolutions per cycle)
            self.engine_rpm = peak_freq * 60 / 2
            
            return self.engine_rpm
            
        except Exception as e:
            print(f"Error analyzing engine signal: {e}")
            return 0
    
    def calculate_performance_metrics(self, rpm, throttle):
        """Calculate various performance metrics"""
        try:
            # Simple performance calculations
            self.throttle_position = throttle
            
            # Simulate gear selection based on RPM
            if rpm < 1500:
                self.gear_position = 1
            elif rpm < 2500:
                self.gear_position = 2
            elif rpm < 3500:
                self.gear_position = 3
            elif rpm < 4500:
                self.gear_position = 4
            else:
                self.gear_position = 5
            
            # Calculate vehicle speed (simplified)
            wheel_diameter = 0.6  # meters
            final_drive_ratio = 3.73
            gear_ratios = {1: 3.42, 2: 2.14, 3: 1.45, 4: 1.0, 5: 0.75}
            
            # Speed calculation
            wheel_rpm = rpm / (gear_ratios[self.gear_position] * final_drive_ratio)
            wheel_rps = wheel_rpm / 60
            self.vehicle_speed = wheel_rps * (wheel_diameter * np.pi) * 3.6  # km/h
            
            return {
                'rpm': self.engine_rpm,
                'speed': self.vehicle_speed,
                'throttle': self.throttle_position,
                'gear': self.gear_position
            }
            
        except Exception as e:
            print(f"Error calculating performance metrics: {e}")
            return None
    
    def plot_performance_data(self, time_data, voltage_data, metrics):
        """Plot performance data and metrics"""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Plot raw signal
            ax1.plot(time_data, voltage_data, 'b-', label='Engine Signal')
            ax1.set_title('Engine Signal Waveform')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Voltage (V)')
            ax1.grid(True)
            ax1.legend()
            
            # Plot performance metrics
            ax2.text(0.1, 0.7, f"RPM: {metrics['rpm']:.0f}")
            ax2.text(0.1, 0.5, f"Speed: {metrics['speed']:.1f} km/h")
            ax2.text(0.1, 0.3, f"Throttle: {metrics['throttle']:.1f}%")
            ax2.text(0.1, 0.1, f"Gear: {metrics['gear']}")
            ax2.set_title('Performance Metrics')
            ax2.set_xticks([])
            ax2.set_yticks([])
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error plotting data: {e}")

def main():
    # Initialize oscilloscope interface
    scope = OscilloscopeInterface()
    
    # Try to connect to scope
    if not scope.connect():
        print("Using simulated data for demonstration")
        # Generate sample data
        time_data = np.linspace(0, 0.1, 1000)
        voltage_data = 2 * np.sin(2 * np.pi * 50 * time_data) + \
                      0.5 * np.sin(2 * np.pi * 120 * time_data)
    else:
        # Configure and acquire real data
        scope.configure_channels([1])
        time_data, voltage_data = scope.acquire_waveform(1)
        
        if time_data is None:
            print("Failed to acquire data, using simulation")
            time_data = np.linspace(0, 0.1, 1000)
            voltage_data = 2 * np.sin(2 * np.pi * 50 * time_data)
    
    # Initialize simulator
    simulator = CarPerformanceSimulator()
    
    # Analyze engine signal
    rpm = simulator.analyze_engine_signal(time_data, voltage_data)
    
    # Calculate performance metrics (assume 50% throttle for demo)
    metrics = simulator.calculate_performance_metrics(rpm, 50)
    
    # Plot results
    simulator.plot_performance_data(time_data, voltage_data, metrics)

if __name__ == '__main__':
    main()
