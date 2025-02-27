#pragma once

#include "evehicle/types.hpp"
#include <chrono>

namespace evehicle {
namespace environmental {

// Forward declarations
struct GenerationStats;
struct SystemRequirements;

// Power modes
enum class PowerMode {
    ECO,        // Maximum efficiency
    NORMAL,     // Normal operation
    BOOST,      // High performance
    MAXIMUM     // Maximum output
};

// Generation methods
enum class GenerationMethod {
    ELECTROLYSIS,         // Water electrolysis
    CHEMICAL_REDUCTION,   // Chemical reduction
    PRESSURE_SWING,      // Pressure swing adsorption
    MEMBRANE_SEPARATION  // Membrane separation
};

// O2 generator configuration
struct O2GeneratorConfig {
    double targetO2Level;      // Target O2 level in percent (e.g., 21%)
    double maxGenerationRate;  // Maximum O2 generation rate in kg/hour
    GenerationMethod method;   // Generation method to use
    bool enableAutoRegulation; // Auto-regulate based on demand

    static O2GeneratorConfig getDefaultConfig() {
        O2GeneratorConfig config;
        config.targetO2Level = 20.946;     // Earth normal
        config.maxGenerationRate = 1.5;    // 1.5 kg/hour
        config.method = GenerationMethod::ELECTROLYSIS;
        config.enableAutoRegulation = true;
        return config;
    }
};

class O2Generator {
public:
    using Mode = PowerMode;

    O2Generator();
    ~O2Generator();

    // System control
    void initialize(const O2GeneratorConfig& config);
    void shutdown();
    bool isOperational() const;

    // Generation control
    void startGeneration();
    void stopGeneration();
    void setGenerationRate(double targetRate);

    // Monitoring
    double getCurrentO2Level() const;       // in percent
    double getGenerationRate() const;       // in kg/hour
    double getEfficiency() const;           // 0-1
    
    // System metrics
    SystemMetrics getMetrics() const;
    GenerationStats getStats() const;
    double getO2Level() const;
    double getPowerConsumption() const;
    double getWasteGeneration() const;
    void increaseOutput();

    // Mode control
    void setPowerMode(Mode mode);

private:
    void applyMode();
    StatusCode determineStatus() const;

    O2GeneratorConfig config_;
    bool isOperational_ = false;
    bool isGenerating_ = false;
    Mode currentMode_ = Mode::NORMAL;
    double currentO2Level_ = 20.946;
    double generationRate_ = 1.0;
    double efficiency_ = 0.9;
    double powerConsumption_ = 1.0;
    double waterConsumption_ = 1.0;
    double wasteGeneration_ = 0.1;
};

// Generation statistics
struct GenerationStats {
    double currentLevel;       // Current O2 level in percent
    double generationRate;    // Current generation rate in kg/hour
    double efficiency;        // Current efficiency (0-1)
    double powerConsumption;  // Power consumption in kW
    double waterConsumption;  // Water consumption in L/hour
    std::chrono::system_clock::time_point timestamp;

    Json toJson() const;
    static GenerationStats fromJson(const Json& json);
};

// System requirements
struct SystemRequirements {
    double minWaterLevel;      // Minimum water level in L
    double minPower;          // Minimum power in kW
    double operatingTemp;     // Operating temperature in Celsius
    double operatingPressure; // Operating pressure in bar

    bool areMet() const;
    String getUnmetRequirements() const;
};

} // namespace environmental
} // namespace evehicle
