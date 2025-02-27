#include "eco_vehicle/analysis/survey_analyzer.hpp"
#include <fstream>
#include <algorithm>
#include <numeric>
#include <boost/algorithm/string.hpp>
#include <nlohmann/json.hpp>

namespace eco_vehicle {
namespace analysis {

using json = nlohmann::json;

SurveyAnalyzer::SurveyAnalyzer(const Config& config)
    : config_(config)
    , logger_("SurveyAnalyzer")
    , diagram_generator_(std::make_unique<uml::DiagramGenerator>(config)) {
    logger_.info("Initializing survey analyzer");
}

bool SurveyAnalyzer::load_survey_data(const std::filesystem::path& json_path) {
    try {
        std::ifstream file(json_path);
        json data = json::parse(file);
        
        survey_responses_.clear();
        for (const auto& response : data["responses"]) {
            SurveyResponse sr;
            sr.employee_id = response["employee_id"];
            sr.department = response["department"];
            sr.role = response["role"];
            
            for (const auto& [key, value] : response["satisfaction_scores"].items()) {
                sr.satisfaction_scores[key] = value;
            }
            
            for (const auto& comment : response["feedback_comments"]) {
                sr.feedback_comments.push_back(comment);
            }
            
            sr.timestamp = std::chrono::system_clock::from_time_t(
                response["timestamp"].get<std::time_t>());
            
            survey_responses_.push_back(sr);
        }
        
        logger_.info("Loaded {} survey responses", survey_responses_.size());
        return true;
    } catch (const std::exception& e) {
        logger_.error("Failed to load survey data: {}", e.what());
        return false;
    }
}

std::optional<DepartmentMetrics> SurveyAnalyzer::analyze_department(
    const std::string& department) {
    try {
        auto dept_responses = std::count_if(
            survey_responses_.begin(),
            survey_responses_.end(),
            [&](const auto& sr) { return sr.department == department; }
        );
        
        if (dept_responses == 0) {
            logger_.warn("No responses found for department: {}", department);
            return std::nullopt;
        }
        
        DepartmentMetrics metrics;
        metrics.name = department;
        
        // Calculate average satisfaction
        double total_satisfaction = 0.0;
        for (const auto& response : survey_responses_) {
            if (response.department == department) {
                total_satisfaction += std::accumulate(
                    response.satisfaction_scores.begin(),
                    response.satisfaction_scores.end(),
                    0.0,
                    [](double sum, const auto& pair) { return sum + pair.second; }
                ) / response.satisfaction_scores.size();
            }
        }
        metrics.avg_satisfaction = total_satisfaction / dept_responses;
        
        // Analyze common issues and suggestions
        identify_common_issues();
        generate_improvement_suggestions();
        
        department_metrics_[department] = metrics;
        return metrics;
    } catch (const std::exception& e) {
        logger_.error("Failed to analyze department {}: {}", department, e.what());
        return std::nullopt;
    }
}

std::optional<std::filesystem::path> SurveyAnalyzer::generate_visualization(
    const std::vector<DepartmentMetrics>& metrics,
    const std::string& filename) {
    try {
        // Create UML class definitions for organizational structure
        std::vector<uml::ClassDefinition> classes;
        
        for (const auto& metric : metrics) {
            uml::ClassDefinition dept;
            dept.name = metric.name;
            
            // Add metrics as attributes
            dept.attributes.emplace_back("avg_satisfaction",
                                       std::to_string(metric.avg_satisfaction));
            dept.attributes.emplace_back("turnover_rate",
                                       std::to_string(metric.turnover_rate));
            
            // Add improvement methods
            for (const auto& suggestion : metric.improvement_suggestions) {
                dept.methods.emplace_back("improve",
                                        "void " + boost::algorithm::replace_all_copy(
                                            suggestion, " ", "_"));
            }
            
            classes.push_back(dept);
        }
        
        return diagram_generator_->generate_class_diagram(classes, filename);
    } catch (const std::exception& e) {
        logger_.error("Failed to generate visualization: {}", e.what());
        return std::nullopt;
    }
}

bool SurveyAnalyzer::generate_organization_diagrams(
    const std::vector<DepartmentMetrics>& metrics) {
    try {
        // Generate class diagram showing department relationships
        auto class_diagram = generate_visualization(metrics, "organization_structure.png");
        if (!class_diagram) {
            return false;
        }
        
        // Generate sequence diagram for improvement workflow
        std::vector<uml::SequenceMessage> messages;
        for (const auto& metric : metrics) {
            if (metric.avg_satisfaction < 0.7) {  // Threshold for improvement needed
                messages.push_back({
                    "HR",
                    metric.name,
                    "implement_improvements",
                    "improvement_status",
                    false
                });
            }
        }
        
        auto sequence_diagram = diagram_generator_->generate_sequence_diagram(
            messages, "improvement_workflow.png");
        
        // Generate state diagram for department satisfaction levels
        std::vector<uml::State> states = {
            {"Low_Satisfaction", {"alert_management"}, {"prepare_action_plan"}, {}},
            {"Medium_Satisfaction", {"monitor_trends"}, {"review_feedback"}, {}},
            {"High_Satisfaction", {"maintain_programs"}, {"document_success"}, {}}
        };
        
        std::vector<uml::Transition> transitions = {
            {"Low_Satisfaction", "Medium_Satisfaction", "implement_improvements", 
             "satisfaction > 0.5", "track_progress"},
            {"Medium_Satisfaction", "High_Satisfaction", "continuous_improvement",
             "satisfaction > 0.8", "document_methods"}
        };
        
        auto state_diagram = diagram_generator_->generate_state_diagram(
            states, transitions, "satisfaction_states.png");
        
        return sequence_diagram && state_diagram;
    } catch (const std::exception& e) {
        logger_.error("Failed to generate organization diagrams: {}", e.what());
        return false;
    }
}

bool SurveyAnalyzer::export_results(const std::filesystem::path& output_path) {
    try {
        std::filesystem::create_directories(output_path);
        
        json output;
        output["analysis_timestamp"] = std::chrono::system_clock::to_time_t(
            std::chrono::system_clock::now());
        
        for (const auto& [dept, metrics] : department_metrics_) {
            json dept_data;
            dept_data["name"] = metrics.name;
            dept_data["avg_satisfaction"] = metrics.avg_satisfaction;
            dept_data["turnover_rate"] = metrics.turnover_rate;
            dept_data["common_issues"] = metrics.common_issues;
            dept_data["improvement_suggestions"] = metrics.improvement_suggestions;
            
            output["departments"].push_back(dept_data);
        }
        
        std::ofstream file(output_path / "analysis_results.json");
        file << std::setw(2) << output << std::endl;
        
        logger_.info("Exported analysis results to {}", output_path.string());
        return true;
    } catch (const std::exception& e) {
        logger_.error("Failed to export results: {}", e.what());
        return false;
    }
}

void SurveyAnalyzer::analyze_satisfaction_trends() {
    for (const auto& [dept, metrics] : department_metrics_) {
        // Group responses by time periods
        std::map<std::string, std::vector<double>> period_scores;
        
        for (const auto& response : survey_responses_) {
            if (response.department == dept) {
                auto time = std::chrono::system_clock::to_time_t(response.timestamp);
                std::string period = std::to_string(time / (60 * 60 * 24 * 30)); // Monthly
                
                double avg_score = std::accumulate(
                    response.satisfaction_scores.begin(),
                    response.satisfaction_scores.end(),
                    0.0,
                    [](double sum, const auto& pair) { return sum + pair.second; }
                ) / response.satisfaction_scores.size();
                
                period_scores[period].push_back(avg_score);
            }
        }
        
        // Calculate trend line using linear regression
        std::vector<double> x_values, y_values;
        for (const auto& [period, scores] : period_scores) {
            double avg = std::accumulate(scores.begin(), scores.end(), 0.0) / scores.size();
            x_values.push_back(std::stod(period));
            y_values.push_back(avg);
        }
        
        if (x_values.size() >= 2) {
            double x_mean = std::accumulate(x_values.begin(), x_values.end(), 0.0) / x_values.size();
            double y_mean = std::accumulate(y_values.begin(), y_values.end(), 0.0) / y_values.size();
            
            double slope = 0.0, denominator = 0.0;
            for (size_t i = 0; i < x_values.size(); ++i) {
                slope += (x_values[i] - x_mean) * (y_values[i] - y_mean);
                denominator += (x_values[i] - x_mean) * (x_values[i] - x_mean);
            }
            slope /= denominator;
            
            logger_.info("Department {} satisfaction trend slope: {}", dept, slope);
        }
    }
}

void SurveyAnalyzer::identify_common_issues() {
    // Use simple NLP techniques to identify common themes in feedback
    std::map<std::string, int> issue_frequency;
    std::vector<std::string> stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to"};
    
    for (const auto& response : survey_responses_) {
        for (const auto& comment : response.feedback_comments) {
            // Tokenize and clean comment
            std::vector<std::string> tokens;
            boost::split(tokens, boost::to_lower_copy(comment), boost::is_any_of(" ,.!?-"));
            
            // Remove stop words and create bigrams
            std::vector<std::string> cleaned_tokens;
            for (const auto& token : tokens) {
                if (std::find(stop_words.begin(), stop_words.end(), token) == stop_words.end()) {
                    cleaned_tokens.push_back(token);
                }
            }
            
            // Count bigrams
            for (size_t i = 0; i < cleaned_tokens.size() - 1; ++i) {
                std::string bigram = cleaned_tokens[i] + " " + cleaned_tokens[i + 1];
                issue_frequency[bigram]++;
            }
        }
    }
    
    // Sort issues by frequency
    std::vector<std::pair<std::string, int>> sorted_issues(
        issue_frequency.begin(), issue_frequency.end());
    std::sort(sorted_issues.begin(), sorted_issues.end(),
              [](const auto& a, const auto& b) { return a.second > b.second; });
    
    // Take top N issues
    const size_t N = 5;
    for (size_t i = 0; i < std::min(N, sorted_issues.size()); ++i) {
        department_metrics_["all"].common_issues.push_back(sorted_issues[i].first);
    }
}

void SurveyAnalyzer::generate_improvement_suggestions() {
    // Map common issues to predefined improvement strategies
    std::map<std::string, std::vector<std::string>> improvement_strategies = {
        {"communication", {
            "Implement regular team meetings",
            "Set up anonymous feedback channels",
            "Create department newsletter"
        }},
        {"work environment", {
            "Conduct ergonomic assessment",
            "Improve office lighting",
            "Create quiet work spaces"
        }},
        {"professional development", {
            "Establish mentorship program",
            "Provide training budget",
            "Create skill-sharing workshops"
        }},
        {"work life", {
            "Implement flexible hours",
            "Allow remote work options",
            "Review workload distribution"
        }},
        {"management style", {
            "Provide leadership training",
            "Implement 360-degree feedback",
            "Regular one-on-one meetings"
        }}
    };
    
    for (auto& [dept, metrics] : department_metrics_) {
        metrics.improvement_suggestions.clear();
        
        // Match issues to strategies
        for (const auto& issue : metrics.common_issues) {
            for (const auto& [category, strategies] : improvement_strategies) {
                if (issue.find(category) != std::string::npos) {
                    metrics.improvement_suggestions.insert(
                        metrics.improvement_suggestions.end(),
                        strategies.begin(),
                        strategies.end());
                }
            }
        }
        
        // Add general suggestions if satisfaction is low
        if (metrics.avg_satisfaction < 0.6) {
            metrics.improvement_suggestions.push_back("Conduct detailed department review");
            metrics.improvement_suggestions.push_back("Schedule team building activities");
        }
        
        // Remove duplicates
        std::sort(metrics.improvement_suggestions.begin(),
                  metrics.improvement_suggestions.end());
        metrics.improvement_suggestions.erase(
            std::unique(metrics.improvement_suggestions.begin(),
                       metrics.improvement_suggestions.end()),
            metrics.improvement_suggestions.end());
    }
}

void SurveyAnalyzer::update_organization_model() {
    // Implementation for model updates
}

} // namespace analysis
} // namespace eco_vehicle
