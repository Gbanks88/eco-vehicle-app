"""
Enhanced Oscilloscope and Engine Analysis Configuration
"""

# Oscilloscope Settings
SCOPE_SETTINGS = {
    'sampling_rate': 1000000,  # 1 MHz
    'record_length': 1000,     # Number of points
    'voltage_range': 5,        # ±5V range
    'trigger_level': 2.5,      # Trigger at 2.5V
    'trigger_slope': 'RISE',   # Rising edge trigger
    'coupling': 'DC',          # DC coupling
    'impedance': 1E6,          # 1MΩ input impedance
    'bandwidth': 100E6,        # 100 MHz bandwidth
    'vertical_scale': 1.0,     # V/div
    'horizontal_scale': 1E-3,  # s/div
    'probe_attenuation': 10,   # 10x probe
}

# Engine Performance Parameters
ENGINE_PARAMS = {
    # Basic Engine Specs
    'cylinders': 4,
    'displacement': 2.0,    # Liters
    'compression_ratio': 10.5,
    'firing_order': [1, 3, 4, 2],
    
    # RPM Ranges
    'max_rpm': 7000,
    'redline': 6500,
    'idle_rpm': 800,
    'optimal_rpm': 4500,
    
    # Power and Torque
    'max_power': 250,      # HP
    'max_torque': 350,     # Nm
    'torque_peak_rpm': 3500,
    'power_peak_rpm': 5500,
    
    # Transmission
    'gear_ratios': {
        1: 3.42,
        2: 2.14,
        3: 1.45,
        4: 1.0,
        5: 0.75
    },
    'final_drive': 3.73,
    'transmission_efficiency': 0.95,
    
    # Vehicle Parameters
    'wheel_diameter': 0.6,  # meters
    'vehicle_weight': 1500, # kg
    'drag_coefficient': 0.32,
    'frontal_area': 2.2,   # m²
    
    # Fuel System
    'injector_flow_rate': 440, # cc/min
    'fuel_pressure': 3.0,      # bar
    'stoich_afr': 14.7,        # Air-Fuel Ratio
    'fuel_density': 0.75,      # kg/L
    
    # Boost System
    'max_boost': 1.2,          # bar
    'boost_threshold_rpm': 2000,
    'wastegate_pressure': 1.0,  # bar
    
    # Cooling System
    'optimal_temp': 90,        # °C
    'max_temp': 105,          # °C
    'thermostat_temp': 82,    # °C
    
    # Oil System
    'optimal_oil_pressure': 60,  # psi
    'min_oil_pressure': 10,     # psi
    'oil_temp_range': [80, 110] # °C
}

# Analysis Settings
ANALYSIS_SETTINGS = {
    # FFT Analysis
    'fft_size': 1024,
    'window_type': 'hanning',
    'overlap': 0.5,
    'averaging': 4,
    
    # Update Rates
    'rpm_update_rate': 0.1,    # seconds
    'metrics_update_rate': 0.2, # seconds
    'display_update_rate': 0.1, # seconds
    
    # Filtering
    'lowpass_cutoff': 500,     # Hz
    'highpass_cutoff': 10,     # Hz
    'noise_floor': -60,        # dB
    
    # Knock Detection
    'knock_frequency': 6000,   # Hz
    'knock_threshold': 0.5,    # V
    'knock_window': 0.002,     # seconds
    
    # Data Recording
    'max_history': 3600,       # seconds
    'log_interval': 0.1,       # seconds
    'csv_export_rate': 1.0,    # seconds
    
    # Performance Calculation
    'acceleration_window': 0.5, # seconds
    'power_calc_interval': 0.2, # seconds
    'torque_smoothing': 0.3,   # smoothing factor
    
    # Alerts
    'rpm_alert': 6500,
    'temp_alert': 105,
    'boost_alert': 1.5,
    'knock_alert_threshold': 0.7
}

# Display Settings
DISPLAY_SETTINGS = {
    # General
    'theme': 'dark',
    'plot_style': 'seaborn-dark',
    'update_interval': 100,    # ms
    
    # Waveform Display
    'waveform_length': 1000,
    'waveform_persistence': 0.5,
    'trigger_position': 0.5,
    
    # Gauges
    'rpm_max_scale': 8000,
    'speed_max_scale': 260,
    'boost_max_scale': 2.0,
    'temp_max_scale': 120,
    
    # Colors
    'normal_color': '#00FF00',
    'warning_color': '#FFFF00',
    'alert_color': '#FF0000',
    'trace_color': '#00FFFF',
    
    # Precision
    'rpm_precision': 0,
    'speed_precision': 1,
    'temp_precision': 1,
    'pressure_precision': 2,
    'power_precision': 1,
    'timing_precision': 3
}

# Channel Mappings
CHANNEL_MAPS = {
    # Engine Management
    'engine_speed': 1,     # RPM signal
    'throttle': 2,         # Throttle position
    'map_sensor': 3,       # Manifold pressure
    'maf_sensor': 4,       # Mass air flow
    
    # Ignition System
    'ignition_primary': 5,
    'ignition_secondary': 6,
    'knock_sensor': 7,
    'cam_position': 8,
    
    # Fuel System
    'oxygen_sensor': 9,
    'fuel_pressure': 10,
    'injector_pulse': 11,
    
    # Sensors
    'coolant_temp': 12,
    'oil_pressure': 13,
    'oil_temp': 14,
    'boost_pressure': 15,
    
    # Transmission
    'vehicle_speed': 16,
    'gear_position': 17,
    'clutch_position': 18,
    'shaft_speed': 19
}
