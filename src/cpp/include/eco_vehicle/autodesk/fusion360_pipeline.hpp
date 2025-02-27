#pragma once

#include <memory>
#include <vector>
#include <string>
#include <optional>
#include <future>
#include <Eigen/Dense>
#include "eco_vehicle/core/logging.hpp"
#include "eco_vehicle/core/config.hpp"

namespace eco_vehicle {
namespace autodesk {

/**
 * @brief Model parameters for Fusion 360
 */
struct ModelParameters {
    Eigen::Vector3d dimensions;
    std::unordered_map<std::string, std::string> materials;
    std::vector<std::unordered_map<std::string, double>> constraints;
    std::unordered_map<std::string, double> simulation_settings;
};

/**
 * @brief Simulation result from Fusion 360
 */
struct SimulationResult {
    bool success;
    std::vector<Eigen::Vector3d> displacement_field;
    std::vector<Eigen::Matrix3d> stress_tensors;
    std::vector<double> safety_factors;
    std::unordered_map<std::string, double> performance_metrics;
};

/**
 * @brief High-performance Fusion 360 integration pipeline
 */
class Fusion360Pipeline {
public:
    /**
     * @brief Initialize Fusion 360 pipeline
     * @param config Pipeline configuration
     */
    explicit Fusion360Pipeline(const Config& config);
    
    /**
     * @brief Create new 3D model
     * @param parameters Model parameters
     * @return Model ID if successful
     */
    std::optional<std::string> create_3d_model(const ModelParameters& parameters);
    
    /**
     * @brief Run simulation on model
     * @param model_id Model identifier
     * @param simulation_type Type of simulation
     * @param parameters Simulation parameters
     * @return Future containing simulation results
     */
    std::future<SimulationResult> run_simulation(
        const std::string& model_id,
        const std::string& simulation_type,
        const std::unordered_map<std::string, double>& parameters);
    
    /**
     * @brief Export model to specified format
     * @param model_id Model identifier
     * @param format Export format
     * @return Path to exported file if successful
     */
    std::optional<std::string> export_model(
        const std::string& model_id,
        const std::string& format = "STEP");
    
    /**
     * @brief Update model parameters
     * @param model_id Model identifier
     * @param parameters New parameters
     * @return True if update successful
     */
    bool update_model_parameters(
        const std::string& model_id,
        const ModelParameters& parameters);
    
    /**
     * @brief Get current performance metrics
     * @return Pipeline performance metrics
     */
    PerformanceMetrics get_performance_metrics() const;

private:
    // Configuration
    Config config_;
    std::unique_ptr<Fusion360Client> client_;
    PerformanceTracker performance_tracker_;
    
    // Thread pool for async operations
    ThreadPool thread_pool_;
    
    /**
     * @brief Create base model with dimensions
     */
    std::optional<std::string> create_base_model(
        const Eigen::Vector3d& dimensions);
    
    /**
     * @brief Apply materials to model components
     */
    bool apply_materials(
        const std::string& model_id,
        const std::unordered_map<std::string, std::string>& materials);
    
    /**
     * @brief Apply constraints to model
     */
    bool apply_constraints(
        const std::string& model_id,
        const std::vector<std::unordered_map<std::string, double>>& constraints);
    
    /**
     * @brief Save model and get its ID
     */
    std::optional<std::string> save_model(const std::string& model_id);
    
    /**
     * @brief Load model from ID
     */
    std::optional<ModelHandle> load_model(const std::string& model_id);
    
    /**
     * @brief Setup simulation environment
     */
    std::optional<SimulationHandle> setup_simulation(
        const ModelHandle& model,
        const std::string& sim_type,
        const std::unordered_map<std::string, double>& parameters);
    
    /**
     * @brief Run simulation and process results
     */
    SimulationResult run_simulation_internal(
        const SimulationHandle& simulation);
};

} // namespace autodesk
} // namespace eco_vehicle
