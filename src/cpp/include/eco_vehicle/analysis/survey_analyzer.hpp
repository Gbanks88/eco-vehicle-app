#pragma once

#include <memory>
#include <vector>
#include <string>
#include <optional>
#include <filesystem>
#include <nlohmann/json.hpp>
#include "eco_vehicle/core/logging.hpp"
#include "eco_vehicle/core/config.hpp"
#include "eco_vehicle/uml/diagram_generator.hpp"

namespace eco_vehicle {
namespace analysis {

/**
 * @brief Survey response data structure
 */
struct SurveyResponse {
    std::string employee_id;
    std::string department;
    std::string role;
    std::map<std::string, double> satisfaction_scores;
    std::vector<std::string> feedback_comments;
    std::chrono::system_clock::time_point timestamp;
};

/**
 * @brief Department performance metrics
 */
struct DepartmentMetrics {
    std::string name;
    double avg_satisfaction;
    double turnover_rate;
    std::vector<std::string> common_issues;
    std::vector<std::string> improvement_suggestions;
};

/**
 * @brief Advanced survey analysis engine
 */
class SurveyAnalyzer {
public:
    /**
     * @brief Initialize survey analyzer
     * @param config Analyzer configuration
     */
    explicit SurveyAnalyzer(const Config& config);
    
    /**
     * @brief Load survey data from JSON
     * @param json_path Path to JSON data file
     * @return Success status
     */
    bool load_survey_data(const std::filesystem::path& json_path);
    
    /**
     * @brief Analyze department performance
     * @param department Department name
     * @return Department metrics
     */
    std::optional<DepartmentMetrics> analyze_department(
        const std::string& department);
    
    /**
     * @brief Generate performance visualization
     * @param metrics List of department metrics
     * @param filename Output filename
     * @return Path to generated visualization
     */
    std::optional<std::filesystem::path> generate_visualization(
        const std::vector<DepartmentMetrics>& metrics,
        const std::string& filename);
    
    /**
     * @brief Generate UML diagrams for organizational structure
     * @param metrics Department metrics to visualize
     * @return Success status
     */
    bool generate_organization_diagrams(
        const std::vector<DepartmentMetrics>& metrics);
    
    /**
     * @brief Export analysis results
     * @param output_path Output directory
     * @return Success status
     */
    bool export_results(const std::filesystem::path& output_path);
    
private:
    // Internal helper methods
    void analyze_satisfaction_trends();
    void identify_common_issues();
    void generate_improvement_suggestions();
    void update_organization_model();
    
    // Data members
    std::vector<SurveyResponse> survey_responses_;
    std::map<std::string, DepartmentMetrics> department_metrics_;
    std::unique_ptr<uml::DiagramGenerator> diagram_generator_;
    Config config_;
    Logger logger_;
};

} // namespace analysis
} // namespace eco_vehicle
