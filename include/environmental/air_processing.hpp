#pragma once

#include "evehicle/types.hpp"
#include <array>
#include <chrono>

namespace evehicle {
namespace environmental {

// Atmospheric composition
struct AtmosphericComposition {
    double nitrogen;    // Target: 78%
    double oxygen;      // Target: 21%
    double argon;       // Target: 0.93%
    double co2;         // Target: 0.04% (400ppm)
    double other;       // Remaining trace gases

    static AtmosphericComposition getEarthNormal() {
        return {
            .nitrogen = 78.084,
            .oxygen = 20.946,
            .argon = 0.934,
            .co2 = 0.0415,    // 415ppm
            .other = 0.001825
        };
    }

    bool isWithinSafeRange() const {
        // Check if composition is within safe ranges
        const double OXYGEN_MIN = 19.5;   // OSHA minimum safe level
        const double OXYGEN_MAX = 23.5;   // OSHA maximum safe level
        const double CO2_MAX = 0.1;      // 1000ppm maximum
        
        return oxygen >= OXYGEN_MIN && 
               oxygen <= OXYGEN_MAX && 
               co2 <= CO2_MAX;
    }
};

// Air quality parameters
struct AirQualityParams {
    double particulateMatter;  // PM2.5 levels
    double volatileOrganics;   // VOC levels
    double humidity;           // Relative humidity
    double temperature;        // Temperature in Celsius

    bool isHealthy() const {
        return particulateMatter < 12.0 &&    // EPA standard
               volatileOrganics < 0.5 &&      // WHO guideline
               humidity >= 30 && humidity <= 60 &&
               temperature >= 20 && temperature <= 25;
    }
};

// Air processor configuration
struct AirProcessorConfig {
    AtmosphericComposition targetComposition;
    double targetAirQuality;
    bool enableContinuousMonitoring;
    std::chrono::seconds samplingInterval;

    static AirProcessorConfig getDefaultConfig() {
        AirProcessorConfig config;
        config.targetComposition = AtmosphericComposition::getEarthNormal();
        config.targetAirQuality = 95.0;
        config.enableContinuousMonitoring = true;
        config.samplingInterval = std::chrono::seconds(30);
        return config;
    }
};

class AirProcessor {
public:
    AirProcessor();
    ~AirProcessor();

    // Initialization
    void initialize(const AirProcessorConfig& config);
    void shutdown();

    // Air composition monitoring
    AtmosphericComposition getCurrentComposition() const;
    void setTargetComposition(const AtmosphericComposition& target);
    
    // Air quality control
    double getAirQualityIndex() const;
    void setAirQualityTarget(double target);
    
    // Processing control
    void startProcessing();
    void stopProcessing();
    bool isProcessing() const;

    // System metrics
    SystemMetrics getMetrics() const;
    double getEfficiency() const;
    double getPowerConsumption() const;
    double getFilterWaste() const;
    void increaseProcessingPower();

private:
    AirProcessorConfig config_;
    AtmosphericComposition currentComposition_;
    AtmosphericComposition targetComposition_;
    double airQualityIndex_ = 95.0;
    double targetAirQuality_ = 95.0;
    double efficiency_ = 95.0;
    double powerConsumption_ = 1.0;
    double filterWaste_ = 0.1;
    double processingPower_ = 80.0;
    bool isProcessing_ = false;
};

} // namespace environmental
} // namespace evehicle
