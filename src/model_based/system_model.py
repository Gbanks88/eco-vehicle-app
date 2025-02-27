import numpy as np
from scipy.integrate import solve_ivp
from dataclasses import dataclass
from typing import List, Dict, Optional
import json

@dataclass
class SystemState:
    time: float
    position: np.ndarray
    velocity: np.ndarray
    acceleration: np.ndarray
    battery_charge: float
    temperature: Dict[str, float]
    stress: Dict[str, float]
    efficiency: float

class SystemModelBase:
    def __init__(self, config_path: Optional[str] = None):
        self.parameters = self.load_parameters(config_path)
        self.state_history: List[SystemState] = []
        self.current_state: Optional[SystemState] = None
        self.time = 0.0
        
    def load_parameters(self, config_path: Optional[str]) -> dict:
        default_params = {
            'mass': 1800.0,  # kg
            'wheelbase': 2.7,  # m
            'track_width': 1.6,  # m
            'cg_height': 0.5,  # m
            'battery_capacity': 75.0,  # kWh
            'motor_efficiency': 0.92,
            'inverter_efficiency': 0.95,
            'battery_efficiency': 0.98,
            'regenerative_efficiency': 0.70,
            'thermal_parameters': {
                'battery_thermal_mass': 250.0,  # J/K
                'motor_thermal_mass': 50.0,  # J/K
                'cooling_coefficient': 15.0,  # W/K
                'ambient_temperature': 298.15  # K
            },
            'aerodynamics': {
                'drag_coefficient': 0.30,
                'frontal_area': 2.3,  # m²
                'air_density': 1.225  # kg/m³
            },
            'powertrain': {
                'max_power': 150000,  # W
                'max_torque': 350,  # Nm
                'gear_ratio': 7.94,
                'wheel_radius': 0.33  # m
            }
        }
        
        if config_path:
            with open(config_path, 'r') as f:
                loaded_params = json.load(f)
                default_params.update(loaded_params)
        
        return default_params
    
    def system_dynamics(self, t: float, y: np.ndarray, u: np.ndarray) -> np.ndarray:
        """
        System dynamics function for numerical integration
        y: [x, y, z, vx, vy, vz, battery_charge, T_battery, T_motor]
        u: [throttle, brake, steering]
        """
        # Extract states
        position = y[0:3]
        velocity = y[3:6]
        battery_charge = y[6]
        T_battery = y[7]
        T_motor = y[8]
        
        # Calculate forces
        F_traction = self.calculate_traction_force(velocity[0], u[0], u[1])
        F_drag = self.calculate_aerodynamic_drag(velocity)
        F_rolling = self.calculate_rolling_resistance(velocity)
        F_gravity = np.array([0, 0, -self.parameters['mass'] * 9.81])
        
        # Net force and acceleration
        F_net = F_traction + F_drag + F_rolling + F_gravity
        acceleration = F_net / self.parameters['mass']
        
        # Power and energy calculations
        P_mechanical = np.dot(F_traction, velocity)
        P_electrical = self.calculate_electrical_power(P_mechanical, u[0])
        battery_derivative = -P_electrical / (self.parameters['battery_capacity'] * 3600000)
        
        # Thermal dynamics
        Q_battery = self.calculate_battery_heat(P_electrical)
        Q_motor = self.calculate_motor_heat(P_mechanical)
        
        T_battery_derivative = (Q_battery - self.parameters['thermal_parameters']['cooling_coefficient'] * 
                              (T_battery - self.parameters['thermal_parameters']['ambient_temperature'])) / \
                              self.parameters['thermal_parameters']['battery_thermal_mass']
        
        T_motor_derivative = (Q_motor - self.parameters['thermal_parameters']['cooling_coefficient'] * 
                            (T_motor - self.parameters['thermal_parameters']['ambient_temperature'])) / \
                            self.parameters['thermal_parameters']['motor_thermal_mass']
        
        return np.concatenate([
            velocity,
            acceleration,
            [battery_derivative],
            [T_battery_derivative],
            [T_motor_derivative]
        ])
    
    def calculate_traction_force(self, velocity: float, throttle: float, brake: float) -> np.ndarray:
        # Calculate available motor torque
        max_torque = self.parameters['powertrain']['max_torque']
        motor_torque = max_torque * (throttle - brake)
        
        # Convert torque to force
        wheel_radius = self.parameters['powertrain']['wheel_radius']
        gear_ratio = self.parameters['powertrain']['gear_ratio']
        
        traction_force = motor_torque * gear_ratio / wheel_radius
        
        # Apply efficiency
        if throttle > 0:
            traction_force *= (self.parameters['motor_efficiency'] * 
                             self.parameters['inverter_efficiency'])
        elif brake > 0:
            traction_force *= self.parameters['regenerative_efficiency']
        
        return np.array([traction_force, 0, 0])
    
    def calculate_aerodynamic_drag(self, velocity: np.ndarray) -> np.ndarray:
        velocity_magnitude = np.linalg.norm(velocity)
        if velocity_magnitude < 1e-6:
            return np.zeros(3)
        
        drag_coefficient = self.parameters['aerodynamics']['drag_coefficient']
        frontal_area = self.parameters['aerodynamics']['frontal_area']
        air_density = self.parameters['aerodynamics']['air_density']
        
        drag_force_magnitude = 0.5 * air_density * drag_coefficient * \
                             frontal_area * velocity_magnitude ** 2
        
        return -drag_force_magnitude * velocity / velocity_magnitude
    
    def calculate_rolling_resistance(self, velocity: np.ndarray) -> np.ndarray:
        velocity_magnitude = np.linalg.norm(velocity)
        if velocity_magnitude < 1e-6:
            return np.zeros(3)
        
        rolling_coefficient = 0.015  # Base rolling resistance coefficient
        normal_force = self.parameters['mass'] * 9.81
        
        # Speed-dependent rolling resistance
        rolling_coefficient *= (1 + velocity_magnitude / 100)
        
        rolling_force_magnitude = rolling_coefficient * normal_force
        
        return -rolling_force_magnitude * velocity / velocity_magnitude
    
    def calculate_electrical_power(self, mechanical_power: float, throttle: float) -> float:
        if throttle > 0:
            return mechanical_power / (self.parameters['motor_efficiency'] * 
                                    self.parameters['inverter_efficiency'] * 
                                    self.parameters['battery_efficiency'])
        else:
            return mechanical_power * self.parameters['regenerative_efficiency'] * \
                   self.parameters['battery_efficiency']
    
    def calculate_battery_heat(self, electrical_power: float) -> float:
        # Simple battery heat model based on I²R losses
        return abs(electrical_power) * (1 - self.parameters['battery_efficiency'])
    
    def calculate_motor_heat(self, mechanical_power: float) -> float:
        # Simple motor heat model based on copper and iron losses
        return abs(mechanical_power) * (1 - self.parameters['motor_efficiency'])
    
    def simulate(self, t_span: tuple, control_inputs: np.ndarray, 
                initial_state: Optional[np.ndarray] = None) -> List[SystemState]:
        if initial_state is None:
            initial_state = np.zeros(9)
            initial_state[6] = 1.0  # Full battery
            initial_state[7] = self.parameters['thermal_parameters']['ambient_temperature']
            initial_state[8] = self.parameters['thermal_parameters']['ambient_temperature']
        
        def dynamics_wrapper(t, y):
            # Find the appropriate control input for current time
            time_index = int(t / (t_span[1] - t_span[0]) * (len(control_inputs) - 1))
            u = control_inputs[time_index]
            return self.system_dynamics(t, y, u)
        
        # Solve ODE
        solution = solve_ivp(
            dynamics_wrapper,
            t_span,
            initial_state,
            method='RK45',
            t_eval=np.linspace(t_span[0], t_span[1], len(control_inputs))
        )
        
        # Convert solution to SystemState objects
        self.state_history = []
        for i in range(len(solution.t)):
            y = solution.y[:, i]
            state = SystemState(
                time=solution.t[i],
                position=y[0:3],
                velocity=y[3:6],
                acceleration=self.system_dynamics(solution.t[i], y, control_inputs[i])[3:6],
                battery_charge=y[6],
                temperature={
                    'battery': y[7],
                    'motor': y[8]
                },
                stress=self.calculate_stress(y, control_inputs[i]),
                efficiency=self.calculate_efficiency(y, control_inputs[i])
            )
            self.state_history.append(state)
            self.current_state = state
        
        return self.state_history
    
    def calculate_stress(self, state: np.ndarray, control: np.ndarray) -> Dict[str, float]:
        """Calculate mechanical and thermal stress on components"""
        velocity = state[3:6]
        battery_temp = state[7]
        motor_temp = state[8]
        
        # Mechanical stress factors
        velocity_stress = np.linalg.norm(velocity) / 50.0  # Normalized by 50 m/s
        acceleration_stress = np.linalg.norm(
            self.system_dynamics(0, state, control)[3:6]
        ) / 10.0  # Normalized by 10 m/s²
        
        # Thermal stress factors
        battery_temp_stress = (battery_temp - 298.15) / 40.0  # Normalized by 40K over ambient
        motor_temp_stress = (motor_temp - 298.15) / 60.0  # Normalized by 60K over ambient
        
        return {
            'mechanical': float(0.7 * velocity_stress + 0.3 * acceleration_stress),
            'battery_thermal': float(battery_temp_stress),
            'motor_thermal': float(motor_temp_stress)
        }
    
    def calculate_efficiency(self, state: np.ndarray, control: np.ndarray) -> float:
        """Calculate overall system efficiency"""
        velocity = state[3:6]
        mechanical_power = np.dot(
            self.calculate_traction_force(np.linalg.norm(velocity), control[0], control[1]),
            velocity
        )
        
        if abs(mechanical_power) < 1e-6:
            return 1.0
        
        electrical_power = self.calculate_electrical_power(mechanical_power, control[0])
        
        if electrical_power > 0:
            return mechanical_power / electrical_power
        else:
            return electrical_power / mechanical_power
    
    def get_state_summary(self) -> dict:
        """Get a summary of the current system state"""
        if not self.current_state:
            return {}
        
        return {
            'time': self.current_state.time,
            'speed': float(np.linalg.norm(self.current_state.velocity)),
            'acceleration': float(np.linalg.norm(self.current_state.acceleration)),
            'battery_charge': float(self.current_state.battery_charge),
            'temperature': self.current_state.temperature,
            'stress': self.current_state.stress,
            'efficiency': float(self.current_state.efficiency)
        }
    
    def export_simulation_data(self, filepath: str):
        """Export simulation history to a file"""
        if not self.state_history:
            return
        
        data = {
            'parameters': self.parameters,
            'history': [
                {
                    'time': state.time,
                    'position': state.position.tolist(),
                    'velocity': state.velocity.tolist(),
                    'acceleration': state.acceleration.tolist(),
                    'battery_charge': float(state.battery_charge),
                    'temperature': state.temperature,
                    'stress': state.stress,
                    'efficiency': float(state.efficiency)
                }
                for state in self.state_history
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
