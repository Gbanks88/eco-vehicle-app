#pragma once

#include "evehicle/types.hpp"
#include "evehicle/environmental/air_processing.hpp"
#include "evehicle/environmental/co2_capture.hpp"
#include "evehicle/environmental/o2_generation.hpp"
#include <functional>
#include <chrono>
#include <vector>

namespace evehicle {
namespace environmental {

// Operating modes
enum class OperatingMode {
    ECO,         // Maximum efficiency
    BALANCED,    // Balance between efficiency and performance
    PERFORMANCE, // Maximum performance
    SAFETY      // Safety-critical operation
};

// Environmental status
struct EnvironmentalStatus {
    double co2Level;      // CO2 level in ppm
    double o2Level;       // O2 level in percent
    double airQuality;    // Air quality index (0-100)
    StatusCode status;    // Overall status
    String message;       // Status message
    OperatingMode currentMode;
    std::chrono::system_clock::time_point timestamp;
};

// Historical record
struct EnvironmentalRecord {
    double co2Level;
    double o2Level;
    double airQuality;
    double efficiency;
    double powerConsumption;
    std::chrono::system_clock::time_point timestamp;

    static EnvironmentalRecord fromJson(const Json& json);
    Json toJson() const;
};

// Environmental system configuration
struct EnvironmentalSystemConfig {
    AirProcessorConfig airConfig;
    CO2CaptureConfig co2Config;
    O2GeneratorConfig o2Config;
    OperatingMode defaultMode;

    static EnvironmentalSystemConfig getDefaultConfig() {
        EnvironmentalSystemConfig config;
        config.airConfig = AirProcessorConfig::getDefaultConfig();
        config.co2Config = CO2CaptureConfig::getDefaultConfig();
        config.o2Config = O2GeneratorConfig::getDefaultConfig();
        config.defaultMode = OperatingMode::BALANCED;
        return config;
    }
};

class System {
public:
    System();
    ~System();

    // System control
    void initialize(const EnvironmentalSystemConfig& config);
    void shutdown();
    bool isOperational() const;

    // Mode control
    void setOperatingMode(OperatingMode mode);

    // Monitoring
    void setMonitoringCallback(std::function<void(const EnvironmentalStatus&)> callback);
    std::vector<EnvironmentalRecord> getHistoricalData(
        std::chrono::system_clock::time_point start,
        std::chrono::system_clock::time_point end) const;
    SystemMetrics getEnvironmentalMetrics() const;

    // Performance optimization
    void optimizePerformance();

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace environmental
} // namespace evehicle
