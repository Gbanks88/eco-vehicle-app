#pragma once

#include "ManualRecycling.hpp"
#include "RecyclingSystem.hpp"
#include <memory>
#include <string>
#include <vector>
#include <map>

namespace circuit {

class RecyclingApp {
public:
    struct UserCredentials {
        std::string username;
        std::string role;  // admin, operator, inspector
        std::string access_level;
        bool is_authenticated;
    };

    struct SystemStatus {
        bool is_initialized;
        int active_operators;
        int pending_tasks;
        std::vector<std::string> active_stations;
        std::map<std::string, std::string> station_status;
    };

    RecyclingApp() {
        manual_system_ = std::make_unique<ManualRecyclingSystem>();
        automated_system_ = std::make_unique<RecyclingSystem>();
        initializeSystem();
    }

    bool login(const std::string& username, const std::string& password) {
        // Implement secure authentication
        current_user_.username = username;
        current_user_.is_authenticated = true;
        return true;
    }

    bool startShift(const std::string& station_id) {
        if (!current_user_.is_authenticated) return false;
        
        status_.active_operators++;
        status_.active_stations.push_back(station_id);
        status_.station_status[station_id] = "active";
        return true;
    }

    bool endShift(const std::string& station_id) {
        if (!current_user_.is_authenticated) return false;
        
        status_.active_operators--;
        auto it = std::find(status_.active_stations.begin(), 
                           status_.active_stations.end(), 
                           station_id);
        if (it != status_.active_stations.end()) {
            status_.active_stations.erase(it);
        }
        status_.station_status[station_id] = "inactive";
        return true;
    }

    bool assignTask(const std::string& operator_id, 
                   const std::string& task_id) {
        if (!current_user_.is_authenticated) return false;
        
        status_.pending_tasks++;
        return true;
    }

    bool completeTask(const std::string& task_id) {
        if (!current_user_.is_authenticated) return false;
        
        status_.pending_tasks--;
        return true;
    }

    const SystemStatus& getSystemStatus() const {
        return status_;
    }

private:
    void initializeSystem() {
        status_.is_initialized = true;
        status_.active_operators = 0;
        status_.pending_tasks = 0;
    }

    std::unique_ptr<ManualRecyclingSystem> manual_system_;
    std::unique_ptr<RecyclingSystem> automated_system_;
    UserCredentials current_user_;
    SystemStatus status_;
};

} // namespace circuit
