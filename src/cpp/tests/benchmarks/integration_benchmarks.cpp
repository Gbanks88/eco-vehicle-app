#include <benchmark/benchmark.h>
#include <random>
#include "eco_vehicle/autodesk/fusion360_pipeline.hpp"
#include "eco_vehicle/uml/diagram_generator.hpp"

namespace {

using namespace eco_vehicle;

// Fixture for Fusion 360 benchmarks
class Fusion360Benchmark : public benchmark::Fixture {
protected:
    void SetUp(const benchmark::State& state) override {
        config_ = {
            {"api_key", "test_key"},
            {"api_secret", "test_secret"},
            {"timeout_ms", 5000}
        };
        pipeline_ = std::make_unique<autodesk::Fusion360Pipeline>(config_);
        
        // Setup test data
        setup_test_data(state.range(0));
    }
    
    void setup_test_data(size_t complexity) {
        // Generate model parameters based on complexity
        parameters_.dimensions = Eigen::Vector3d(1.0, 2.0, 0.5);
        
        // Add materials
        parameters_.materials["body"] = "steel";
        parameters_.materials["shell"] = "aluminum";
        
        // Add constraints based on complexity
        for (size_t i = 0; i < complexity; ++i) {
            parameters_.constraints.push_back({
                {"x", 0.0},
                {"y", 0.0},
                {"z", 0.0},
                {"rotation", 0.0}
            });
        }
    }
    
    Config config_;
    std::unique_ptr<autodesk::Fusion360Pipeline> pipeline_;
    autodesk::ModelParameters parameters_;
};

// Benchmark model creation
BENCHMARK_DEFINE_F(Fusion360Benchmark, ModelCreation)(benchmark::State& state) {
    for (auto _ : state) {
        auto model_id = pipeline_->create_3d_model(parameters_);
        benchmark::DoNotOptimize(model_id);
    }
    state.SetComplexityN(state.range(0));
}

// Benchmark simulation
BENCHMARK_DEFINE_F(Fusion360Benchmark, Simulation)(benchmark::State& state) {
    auto model_id = pipeline_->create_3d_model(parameters_);
    std::unordered_map<std::string, double> sim_params{
        {"duration", 1.0},
        {"timestep", 0.001},
        {"accuracy", 0.99}
    };
    
    for (auto _ : state) {
        auto future = pipeline_->run_simulation(*model_id, "structural", sim_params);
        auto result = future.get();
        benchmark::DoNotOptimize(result);
    }
    state.SetComplexityN(state.range(0));
}

// Fixture for UML benchmarks
class UMLBenchmark : public benchmark::Fixture {
protected:
    void SetUp(const benchmark::State& state) override {
        config_ = {
            {"output_dir", "test_output"},
            {"format", "png"},
            {"dpi", 300}
        };
        generator_ = std::make_unique<uml::DiagramGenerator>(config_);
        
        // Setup test data
        setup_test_data(state.range(0));
    }
    
    void setup_test_data(size_t size) {
        // Generate class definitions
        classes_.clear();
        for (size_t i = 0; i < size; ++i) {
            uml::ClassDefinition cls{
                "Class" + std::to_string(i),
                {{"attr1", "int"}, {"attr2", "string"}},
                {{"method1", "void()"}, {"method2", "int(string)"}},
                {"BaseClass"},
                {"Dependency1"}
            };
            classes_.push_back(cls);
        }
        
        // Generate sequence messages
        messages_.clear();
        for (size_t i = 0; i < size; ++i) {
            uml::SequenceMessage msg{
                "Object" + std::to_string(i),
                "Object" + std::to_string((i + 1) % size),
                "message" + std::to_string(i),
                "response" + std::to_string(i),
                false
            };
            messages_.push_back(msg);
        }
    }
    
    Config config_;
    std::unique_ptr<uml::DiagramGenerator> generator_;
    std::vector<uml::ClassDefinition> classes_;
    std::vector<uml::SequenceMessage> messages_;
};

// Benchmark class diagram generation
BENCHMARK_DEFINE_F(UMLBenchmark, ClassDiagram)(benchmark::State& state) {
    for (auto _ : state) {
        auto path = generator_->generate_class_diagram(classes_, "test_class");
        benchmark::DoNotOptimize(path);
    }
    state.SetComplexityN(state.range(0));
}

// Benchmark sequence diagram generation
BENCHMARK_DEFINE_F(UMLBenchmark, SequenceDiagram)(benchmark::State& state) {
    for (auto _ : state) {
        auto path = generator_->generate_sequence_diagram(messages_, "test_sequence");
        benchmark::DoNotOptimize(path);
    }
    state.SetComplexityN(state.range(0));
}

// Register benchmarks with different input sizes
BENCHMARK_REGISTER_F(Fusion360Benchmark, ModelCreation)
    ->RangeMultiplier(2)
    ->Range(8, 8<<8)
    ->Complexity()
    ->UseRealTime()
    ->Unit(benchmark::kMillisecond);

BENCHMARK_REGISTER_F(Fusion360Benchmark, Simulation)
    ->RangeMultiplier(2)
    ->Range(8, 8<<8)
    ->Complexity()
    ->UseRealTime()
    ->Unit(benchmark::kMillisecond);

BENCHMARK_REGISTER_F(UMLBenchmark, ClassDiagram)
    ->RangeMultiplier(2)
    ->Range(8, 8<<8)
    ->Complexity()
    ->UseRealTime()
    ->Unit(benchmark::kMillisecond);

BENCHMARK_REGISTER_F(UMLBenchmark, SequenceDiagram)
    ->RangeMultiplier(2)
    ->Range(8, 8<<8)
    ->Complexity()
    ->UseRealTime()
    ->Unit(benchmark::kMillisecond);

} // namespace
