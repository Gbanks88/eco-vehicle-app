#pragma once

#include <memory>
#include <vector>
#include <Eigen/Dense>
#include <optional>
#include <chrono>
#include <cuda_runtime.h>
#include "eco_vehicle/core/logging.hpp"
#include "eco_vehicle/core/config.hpp"

namespace eco_vehicle {
namespace physics {

/**
 * @brief Physical properties of a vehicle component
 */
struct PhysicalProperties {
    double mass;                          // kg
    Eigen::Vector3d dimensions;           // meters
    Eigen::Vector3d center_of_mass;       // relative to component origin
    Eigen::Matrix3d moment_of_inertia;    // kg⋅m²
    std::unordered_map<std::string, double> material_properties;
};

/**
 * @brief Force vector with magnitude and direction
 */
struct ForceVector {
    double magnitude;                     // Newtons
    Eigen::Vector3d direction;            // Unit vector components
    Eigen::Vector3d application_point;    // Relative to component origin
};

/**
 * @brief Result of collision detection
 */
struct CollisionResult {
    bool collision_detected;
    Eigen::Vector3d collision_point;
    Eigen::Vector3d collision_normal;
    double penetration_depth;
};

/**
 * @brief High-performance physics engine for vehicle simulation
 */
class PhysicsEngine {
public:
    /**
     * @brief Initialize physics engine
     * @param config Engine configuration
     */
    explicit PhysicsEngine(const Config& config);
    
    /**
     * @brief Calculate motion based on applied forces
     * @param initial_state Initial position, velocity, and acceleration
     * @param forces List of forces acting on the vehicle
     * @param duration Duration of simulation in seconds
     * @return Motion history
     */
    MotionResult calculate_motion(
        const State& initial_state,
        const std::vector<ForceVector>& forces,
        double duration);
    
    /**
     * @brief Calculate component deformation under applied forces
     * @param component Physical properties of the component
     * @param forces Forces acting on the component
     * @return Deformation analysis
     */
    DeformationResult calculate_deformation(
        const PhysicalProperties& component,
        const std::vector<ForceVector>& forces);
    
    /**
     * @brief Check for collision between two objects
     * @param object1 First object properties and position
     * @param object2 Second object properties and position
     * @return Collision result
     */
    CollisionResult check_collision(
        const Object& object1,
        const Object& object2);
    
    /**
     * @brief Get current performance metrics
     * @return Engine performance metrics
     */
    PerformanceMetrics get_performance_metrics() const;

private:
    // Configuration
    Config config_;
    double gravity_;
    double air_density_;
    double time_step_;
    
    // GPU resources
    struct CudaResources;
    std::unique_ptr<CudaResources> cuda_resources_;
    
    // Performance tracking
    PerformanceTracker performance_tracker_;
    
    /**
     * @brief Calculate net force including gravity and drag
     */
    Eigen::Vector3d calculate_net_force(
        const std::vector<ForceVector>& forces,
        const Eigen::Vector3d& position,
        const Eigen::Vector3d& velocity,
        double time);
    
    /**
     * @brief Solve motion equations using GPU acceleration
     */
    void solve_motion_gpu(
        const State& initial_state,
        const std::vector<ForceVector>& forces,
        double duration,
        MotionResult& result);
    
    /**
     * @brief Calculate stress tensor for a component
     */
    Eigen::Matrix3d calculate_stress_tensor(
        const PhysicalProperties& component,
        const std::vector<ForceVector>& forces);
    
    /**
     * @brief Calculate strain tensor from stress tensor
     */
    Eigen::Matrix3d calculate_strain_tensor(
        const Eigen::Matrix3d& stress_tensor,
        const std::unordered_map<std::string, double>& material_properties);
    
    /**
     * @brief Calculate deformation field using finite element analysis
     */
    Eigen::MatrixXd calculate_deformation_field(
        const Eigen::Matrix3d& strain_tensor,
        const Eigen::Vector3d& dimensions);
};

} // namespace physics
} // namespace eco_vehicle
