#include <benchmark/benchmark.h>
#include <random>
#include "eco_vehicle/physics/physics_engine.hpp"

namespace {

using namespace eco_vehicle::physics;

// Fixture for physics benchmarks
class PhysicsBenchmark : public benchmark::Fixture {
protected:
    void SetUp(const benchmark::State& state) override {
        config_ = {
            {"gravity", -9.81},
            {"air_density", 1.225},
            {"time_step", 0.001}
        };
        engine_ = std::make_unique<PhysicsEngine>(config_);
        
        // Setup test data
        setup_test_data(state.range(0));
    }
    
    void setup_test_data(size_t size) {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> pos_dist(-100.0, 100.0);
        std::uniform_real_distribution<> force_dist(0.0, 1000.0);
        
        // Generate random forces
        forces_.clear();
        for (size_t i = 0; i < size; ++i) {
            forces_.push_back(ForceVector{
                force_dist(gen),
                {pos_dist(gen), pos_dist(gen), pos_dist(gen)},
                {pos_dist(gen), pos_dist(gen), pos_dist(gen)}
            });
        }
        
        // Generate initial state
        initial_state_ = {
            {pos_dist(gen), pos_dist(gen), pos_dist(gen)},
            {pos_dist(gen), pos_dist(gen), pos_dist(gen)},
            {0.0, 0.0, 0.0}
        };
    }
    
    Config config_;
    std::unique_ptr<PhysicsEngine> engine_;
    std::vector<ForceVector> forces_;
    State initial_state_;
};

// Benchmark motion calculation
BENCHMARK_DEFINE_F(PhysicsBenchmark, MotionCalculation)(benchmark::State& state) {
    for (auto _ : state) {
        auto result = engine_->calculate_motion(initial_state_, forces_, 1.0);
        benchmark::DoNotOptimize(result);
    }
    state.SetComplexityN(state.range(0));
}

// Benchmark deformation analysis
BENCHMARK_DEFINE_F(PhysicsBenchmark, DeformationAnalysis)(benchmark::State& state) {
    PhysicalProperties component{
        1000.0,  // mass
        {1.0, 2.0, 0.5},  // dimensions
        {0.0, 0.0, 0.0},  // center of mass
        Eigen::Matrix3d::Identity(),  // moment of inertia
        {{"young_modulus", 200e9}, {"poisson_ratio", 0.3}}  // steel properties
    };
    
    for (auto _ : state) {
        auto result = engine_->calculate_deformation(component, forces_);
        benchmark::DoNotOptimize(result);
    }
    state.SetComplexityN(state.range(0));
}

// Benchmark collision detection
BENCHMARK_DEFINE_F(PhysicsBenchmark, CollisionDetection)(benchmark::State& state) {
    Object obj1{initial_state_, {1.0, 1.0, 1.0}};
    Object obj2{initial_state_, {1.0, 1.0, 1.0}};
    
    for (auto _ : state) {
        auto result = engine_->check_collision(obj1, obj2);
        benchmark::DoNotOptimize(result);
    }
}

// Register benchmarks with different input sizes
BENCHMARK_REGISTER_F(PhysicsBenchmark, MotionCalculation)
    ->RangeMultiplier(2)
    ->Range(8, 8<<10)
    ->Complexity()
    ->UseRealTime()
    ->Unit(benchmark::kMillisecond);

BENCHMARK_REGISTER_F(PhysicsBenchmark, DeformationAnalysis)
    ->RangeMultiplier(2)
    ->Range(8, 8<<10)
    ->Complexity()
    ->UseRealTime()
    ->Unit(benchmark::kMillisecond);

BENCHMARK_REGISTER_F(PhysicsBenchmark, CollisionDetection)
    ->UseRealTime()
    ->Unit(benchmark::kMicrosecond);

} // namespace
