#pragma once

#include "evehicle/types.hpp"
#include <chrono>

namespace evehicle {
namespace environmental {

// Forward declarations
struct CaptureMetrics;
struct StorageStatus;

// Operating modes
enum class CaptureMode {
    EFFICIENT,          // Maximum efficiency
    BALANCED,          // Balance between efficiency and performance
    PERFORMANCE,       // Maximum performance
    SAFETY            // Safety-critical operation
};

// Capture methods
enum class CaptureMethod {
    DIRECT_AIR,           // Direct air capture
    CHEMICAL_ABSORPTION,  // Chemical absorption
    MEMBRANE_SEPARATION,  // Membrane separation
    CRYOGENIC_SEPARATION // Cryogenic separation
};

// CO2 capture configuration
struct CO2CaptureConfig {
    double targetCO2Level;    // Target CO2 level in ppm (e.g., 400ppm)
    double maxCaptureRate;    // Maximum CO2 capture rate in kg/hour
    double storageCapacity;   // Storage capacity in kg
    CaptureMethod method;     // Capture method to use

    static CO2CaptureConfig getDefaultConfig() {
        CO2CaptureConfig config;
        config.targetCO2Level = 400.0;    // Earth normal
        config.maxCaptureRate = 2.0;      // 2 kg/hour
        config.storageCapacity = 50.0;    // 50 kg
        config.method = CaptureMethod::DIRECT_AIR;
        return config;
    }
};

class CO2Capture {
public:
    using Mode = CaptureMode;

    CO2Capture();
    ~CO2Capture();

    // System control
    void initialize(const CO2CaptureConfig& config);
    void shutdown();
    bool isOperational() const;

    // Capture control
    void startCapture();
    void stopCapture();
    void setCaptureRate(double targetRate);

    // Monitoring
    double getCurrentCO2Level() const;      // in ppm
    double getCaptureEfficiency() const;    // 0-1
    double getTotalCO2Captured() const;     // in kg
    
    // Environmental impact
    double getCarbonOffset() const;         // in kg CO2
    SystemMetrics getMetrics() const;
    double getCO2Impact() const;
    double getPowerConsumption() const;
    double getWasteGeneration() const;
    void increaseCaptureRate();

    // Mode control
    void setOperatingMode(Mode mode);

private:
    void applyMode();
    StatusCode determineStatus() const;

    CO2CaptureConfig config_;
    bool isOperational_ = false;
    bool isCapturing_ = false;
    Mode currentMode_ = Mode::BALANCED;
    double currentCO2Level_ = 400.0;
    double captureRate_ = 1.0;
    double efficiency_ = 0.9;
    double totalCaptured_ = 0.0;
    double co2Impact_ = 20.0;
    double powerConsumption_ = 1.0;
    double wasteGeneration_ = 0.1;
};

// Capture metrics
struct CaptureMetrics {
    double currentLevel;      // Current CO2 level in ppm
    double captureRate;       // Current capture rate in kg/hour
    double efficiency;        // Current efficiency (0-1)
    double totalCaptured;     // Total CO2 captured in kg
    double storageLevel;      // Current storage level in kg
    std::chrono::system_clock::time_point timestamp;

    Json toJson() const;
    static CaptureMetrics fromJson(const Json& json);
};

// Storage status
struct StorageStatus {
    double capacity;          // Total capacity in kg
    double currentLevel;      // Current storage level in kg
    double fillRate;         // Current fill rate in kg/hour
    bool needsRecycling;     // Whether storage needs recycling
    std::chrono::system_clock::time_point lastRecycled;
};

} // namespace environmental
} // namespace evehicle
