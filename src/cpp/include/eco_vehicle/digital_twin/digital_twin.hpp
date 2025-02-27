#pragma once

#include <memory>
#include <vector>
#include <string>
#include <chrono>
#include <optional>
#include <tbb/concurrent_vector.h>
#include "eco_vehicle/core/logging.hpp"
#include "eco_vehicle/physics/physics_engine.hpp"
#include "eco_vehicle/autodesk/autocad_interface.hpp"
#include "eco_vehicle/autodesk/fusion360_pipeline.hpp"

namespace eco_vehicle {
namespace digital_twin {

/**
 * @brief Vehicle state information
 */
struct VehicleState {
    std::chrono::system_clock::time_point timestamp;
    Eigen::Vector3d position;
    Eigen::Vector3d velocity;
    Eigen::Vector3d acceleration;
    std::unordered_map<std::string, std::string> system_states;
    std::unordered_map<std::string, double> sensor_readings;
    std::unordered_map<std::string, double> component_health;
};

/**
 * @brief Maintenance prediction result
 */
struct MaintenancePrediction {
    std::vector<std::string> critical_components;
    std::unordered_map<std::string, double> failure_probabilities;
    std::vector<std::string> recommended_actions;
    std::chrono::system_clock::time_point next_maintenance_date;
};

/**
 * @brief Simulation scenario configuration
 */
struct SimulationScenario {
    double duration;
    std::unordered_map<std::string, double> environment;
    std::vector<SimulationEvent> events;
};

/**
 * @brief Digital twin for physical vehicle representation
 */
class DigitalTwin {
public:
    /**
     * @brief Initialize digital twin
     * @param vehicle_id Unique identifier for the vehicle
     * @param config Configuration parameters
     */
    DigitalTwin(
        const std::string& vehicle_id,
        const Config& config);
    
    /**
     * @brief Update digital twin state with new telemetry data
     * @param telemetry_data New telemetry data from physical vehicle
     * @return True if update successful
     */
    bool update_state(const TelemetryData& telemetry_data);
    
    /**
     * @brief Predict maintenance needs based on current state and history
     * @return Maintenance predictions
     */
    MaintenancePrediction predict_maintenance();
    
    /**
     * @brief Run simulation using current state
     * @param scenario Simulation scenario parameters
     * @return Simulation results
     */
    SimulationResult run_simulation(const SimulationScenario& scenario);
    
    /**
     * @brief Get current performance metrics
     * @return Performance metrics
     */
    PerformanceMetrics get_performance_metrics() const;
    
    /**
     * @brief Get state history within time range
     * @param start_time Start of time range
     * @param end_time End of time range
     * @return Vector of states within range
     */
    std::vector<VehicleState> get_state_history(
        const std::chrono::system_clock::time_point& start_time,
        const std::chrono::system_clock::time_point& end_time) const;

private:
    // Core components
    std::string vehicle_id_;
    Config config_;
    std::unique_ptr<VehicleState> current_state_;
    tbb::concurrent_vector<VehicleState> history_;
    
    // Subsystems
    std::unique_ptr<physics::PhysicsEngine> physics_engine_;
    std::unique_ptr<autodesk::AutoCADInterface> cad_interface_;
    std::unique_ptr<autodesk::Fusion360Pipeline> fusion_interface_;
    
    // Performance tracking
    PerformanceTracker performance_tracker_;
    
    /**
     * @brief Create state from telemetry data
     */
    VehicleState create_state_from_telemetry(const TelemetryData& telemetry_data);
    
    /**
     * @brief Validate state transition physics and constraints
     */
    bool validate_state_transition(const VehicleState& new_state);
    
    /**
     * @brief Update 3D models with new state
     */
    void update_models(const VehicleState& state);
    
    /**
     * @brief Analyze component health based on current state and history
     */
    std::unordered_map<std::string, double> analyze_component_health();
    
    /**
     * @brief Generate maintenance predictions based on health analysis
     */
    MaintenancePrediction generate_maintenance_predictions(
        const std::unordered_map<std::string, double>& health_analysis);
    
    /**
     * @brief Set up simulation environment with current state
     */
    SimulationEnvironment setup_simulation_environment(
        const SimulationScenario& scenario);
    
    /**
     * @brief Execute simulation and return results
     */
    SimulationResult execute_simulation(
        const SimulationEnvironment& sim_env);
};

} // namespace digital_twin
} // namespace eco_vehicle
