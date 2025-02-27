#pragma once

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <chrono>

namespace circuit {

class DatabaseManager {
public:
    struct ComponentRecord {
        std::string id;
        std::string type;
        std::string manufacturer;
        std::chrono::system_clock::time_point received_date;
        std::string condition;
        double weight;
        std::map<std::string, double> material_composition;
    };

    struct RecyclingRecord {
        std::string id;
        std::string component_id;
        std::string operator_id;
        std::chrono::system_clock::time_point process_date;
        std::string process_type;
        bool success;
        std::map<std::string, double> recovered_materials;
        double recovery_efficiency;
    };

    struct OperatorRecord {
        std::string id;
        std::string name;
        std::string certification_level;
        std::vector<std::string> certifications;
        std::chrono::system_clock::time_point last_training;
        int total_components_processed;
        double efficiency_rating;
    };

    // Component management
    bool addComponent(const ComponentRecord& component) {
        components_[component.id] = component;
        return true;
    }

    bool updateComponent(const std::string& id, 
                        const ComponentRecord& component) {
        if (components_.find(id) == components_.end()) return false;
        components_[id] = component;
        return true;
    }

    ComponentRecord* getComponent(const std::string& id) {
        auto it = components_.find(id);
        return it != components_.end() ? &it->second : nullptr;
    }

    // Recycling records
    bool addRecyclingRecord(const RecyclingRecord& record) {
        recycling_records_[record.id] = record;
        return true;
    }

    std::vector<RecyclingRecord> getOperatorRecords(
        const std::string& operator_id) {
        std::vector<RecyclingRecord> records;
        for (const auto& [id, record] : recycling_records_) {
            if (record.operator_id == operator_id) {
                records.push_back(record);
            }
        }
        return records;
    }

    // Operator management
    bool addOperator(const OperatorRecord& op) {
        operators_[op.id] = op;
        return true;
    }

    bool updateOperator(const std::string& id, 
                       const OperatorRecord& op) {
        if (operators_.find(id) == operators_.end()) return false;
        operators_[id] = op;
        return true;
    }

    OperatorRecord* getOperator(const std::string& id) {
        auto it = operators_.find(id);
        return it != operators_.end() ? &it->second : nullptr;
    }

    // Statistics and reporting
    double getOverallRecoveryEfficiency() {
        double total_efficiency = 0.0;
        int count = 0;
        
        for (const auto& [id, record] : recycling_records_) {
            total_efficiency += record.recovery_efficiency;
            count++;
        }
        
        return count > 0 ? total_efficiency / count : 0.0;
    }

    std::map<std::string, double> getMaterialRecoveryStats() {
        std::map<std::string, double> stats;
        
        for (const auto& [id, record] : recycling_records_) {
            for (const auto& [material, amount] : record.recovered_materials) {
                stats[material] += amount;
            }
        }
        
        return stats;
    }

    std::vector<OperatorRecord> getTopOperators(int limit = 10) {
        std::vector<OperatorRecord> top_operators;
        
        for (const auto& [id, op] : operators_) {
            top_operators.push_back(op);
        }
        
        std::sort(top_operators.begin(), top_operators.end(),
                 [](const OperatorRecord& a, const OperatorRecord& b) {
                     return a.efficiency_rating > b.efficiency_rating;
                 });
        
        if (top_operators.size() > limit) {
            top_operators.resize(limit);
        }
        
        return top_operators;
    }

    // Reporting structures
    struct EfficiencyData {
        double overall_efficiency;
        int total_processed;
        double success_rate;
    };

    struct EfficiencyPoint {
        std::string date;
        double efficiency;
    };

    struct MaterialData {
        std::string type;
        double quantity;
    };

    // Reporting methods
    EfficiencyData getEfficiencyData(
        std::chrono::system_clock::time_point start_date,
        std::chrono::system_clock::time_point end_date) {
        
        EfficiencyData data{0.0, 0, 0.0};
        int success_count = 0;
        
        for (const auto& [id, record] : recycling_records_) {
            if (record.process_date >= start_date && 
                record.process_date <= end_date) {
                
                data.overall_efficiency += record.recovery_efficiency;
                data.total_processed++;
                
                if (record.success) {
                    success_count++;
                }
            }
        }
        
        if (data.total_processed > 0) {
            data.overall_efficiency /= data.total_processed;
            data.success_rate = 
                (static_cast<double>(success_count) / data.total_processed) * 100;
        }
        
        return data;
    }

    std::vector<EfficiencyPoint> getEfficiencyTrends() {
        std::vector<EfficiencyPoint> trends;
        std::map<std::string, std::pair<double, int>> daily_stats;
        
        for (const auto& [id, record] : recycling_records_) {
            auto time = std::chrono::system_clock::to_time_t(record.process_date);
            std::string date = std::string(std::ctime(&time)).substr(0, 10);
            
            daily_stats[date].first += record.recovery_efficiency;
            daily_stats[date].second++;
        }
        
        for (const auto& [date, stats] : daily_stats) {
            trends.push_back({
                date,
                stats.second > 0 ? stats.first / stats.second : 0.0
            });
        }
        
        std::sort(trends.begin(), trends.end(),
                 [](const EfficiencyPoint& a, const EfficiencyPoint& b) {
                     return a.date < b.date;
                 });
        
        return trends;
    }

    std::vector<MaterialData> getMaterialsRecovered() {
        std::vector<MaterialData> materials;
        std::map<std::string, double> totals;
        
        for (const auto& [id, record] : recycling_records_) {
            for (const auto& [material, amount] : record.recovered_materials) {
                totals[material] += amount;
            }
        }
        
        for (const auto& [material, amount] : totals) {
            materials.push_back({material, amount});
        }
        
        std::sort(materials.begin(), materials.end(),
                 [](const MaterialData& a, const MaterialData& b) {
                     return a.quantity > b.quantity;
                 });
        
        return materials;
    }

    std::vector<std::string> getKeyMetrics(
        std::chrono::system_clock::time_point start_date,
        std::chrono::system_clock::time_point end_date) {
        
        std::vector<std::string> metrics;
        auto efficiency_data = getEfficiencyData(start_date, end_date);
        auto materials = getMaterialsRecovered();
        auto top_ops = getTopOperators(3);
        
        metrics.push_back("Overall efficiency: " + 
                         std::to_string(efficiency_data.overall_efficiency) + "%");
        metrics.push_back("Total components processed: " + 
                         std::to_string(efficiency_data.total_processed));
        metrics.push_back("Success rate: " + 
                         std::to_string(efficiency_data.success_rate) + "%");
        
        if (!materials.empty()) {
            metrics.push_back("Most recovered material: " + materials[0].type + 
                            " (" + std::to_string(materials[0].quantity) + " kg)");
        }
        
        if (!top_ops.empty()) {
            metrics.push_back("Top performer: " + top_ops[0].name + 
                            " (Efficiency: " + 
                            std::to_string(top_ops[0].efficiency_rating) + "%)");
        }
        
        return metrics;
    }

private:
    std::map<std::string, ComponentRecord> components_;
    std::map<std::string, RecyclingRecord> recycling_records_;
    std::map<std::string, OperatorRecord> operators_;
};

} // namespace circuit
