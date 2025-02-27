#pragma once

#include "evehicle/types.hpp"
#include <chrono>
#include <vector>
#include <memory>

namespace evehicle {
namespace environmental {

// Impact severity levels
enum class ImpactSeverity {
    NEGLIGIBLE,
    LOW,
    MODERATE,
    HIGH,
    CRITICAL
};

// Impact categories
enum class ImpactCategory {
    CARBON_EMISSIONS,
    ENERGY_CONSUMPTION,
    RESOURCE_USAGE,
    WASTE_GENERATION,
    ECOSYSTEM_IMPACT
};

// Metrics snapshot
struct MetricsSnapshot {
    std::chrono::system_clock::time_point timestamp;
    double co2Emissions;      // in kg
    double energyConsumption; // in kWh
    double resourceUsage;     // normalized 0-1
    double wasteGeneration;   // in kg
    double ecosystemImpact;   // normalized 0-1

    static MetricsSnapshot fromJson(const Json& json);
    Json toJson() const;
};

// Impact recommendation
struct Recommendation {
    String description;
    double potentialImprovement;
    double implementationCost;
    double roi;
    ImpactCategory category;
    ImpactSeverity severity;

    static Recommendation fromJson(const Json& json);
    Json toJson() const;
};

// Impact report
struct ImpactReport {
    std::chrono::system_clock::time_point timestamp;
    std::vector<MetricsSnapshot> metrics;
    std::vector<Recommendation> recommendations;
    double overallImpactScore;
    String summary;
    bool hasHighSeverityIssues;

    static ImpactReport fromJson(const Json& json);
    Json toJson() const;
};

// Analyzer configuration
struct ImpactAnalyzerConfig {
    std::chrono::seconds samplingInterval;
    size_t historySize;
    bool enablePredictiveAnalysis;
    double severityThreshold;
    std::vector<ImpactCategory> monitoredCategories;

    static ImpactAnalyzerConfig getDefaultConfig() {
        ImpactAnalyzerConfig config;
        config.samplingInterval = std::chrono::seconds(60);
        config.historySize = 1000;
        config.enablePredictiveAnalysis = true;
        config.severityThreshold = 0.7;
        config.monitoredCategories = {
            ImpactCategory::CARBON_EMISSIONS,
            ImpactCategory::ENERGY_CONSUMPTION,
            ImpactCategory::RESOURCE_USAGE
        };
        return config;
    }
};

class ImpactAnalyzer {
public:
    ImpactAnalyzer();
    ~ImpactAnalyzer();

    // Initialization
    void initialize(const ImpactAnalyzerConfig& config);
    void shutdown();
    bool isOperational() const;

    // Analysis
    ImpactReport generateReport() const;
    double calculateOverallImpact() const;
    std::vector<Recommendation> getRecommendations() const;

    // Data collection
    void startDataCollection();
    void stopDataCollection();
    bool isCollectingData() const;

    // Configuration
    void setSeverityThreshold(double threshold);
    void setMonitoredCategories(const std::vector<ImpactCategory>& categories);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace environmental
} // namespace evehicle
