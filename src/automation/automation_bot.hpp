#pragma once

#include <vector>
#include <string>
#include <unordered_map>
#include <queue>
#include <memory>
#include <functional>
#include <chrono>
#include "../requirements_gen/requirements_generator.hpp"

class AutomationBot {
public:
    struct Task {
        std::string id;
        std::string requirement_id;
        std::string title;
        std::string description;
        std::string assignee;
        double estimated_hours;
        std::string status;
        std::vector<std::string> dependencies;
        std::chrono::system_clock::time_point due_date;
    };

    struct WorkflowStage {
        std::string name;
        std::vector<std::string> required_checks;
        std::function<bool(const Task&)> validation_func;
    };

    AutomationBot();

    // Task Management
    std::vector<Task> createTasksFromRequirements(
        const std::vector<RequirementsGenerator::Requirement>& requirements);
    void prioritizeTasks();
    std::vector<Task> getNextTasks(int count);
    void updateTaskStatus(const std::string& task_id, const std::string& new_status);
    
    // Workflow Management
    void addWorkflowStage(const WorkflowStage& stage);
    bool validateTaskForStage(const Task& task, const std::string& stage);
    std::vector<std::string> getTaskValidationErrors(const Task& task);

    // Resource Management
    void addTeamMember(const std::string& name, const std::vector<std::string>& skills);
    void assignTask(const std::string& task_id, const std::string& assignee);
    double calculateWorkload(const std::string& team_member) const;

    // Analytics
    struct ProjectMetrics {
        double completion_rate;
        double efficiency;
        int total_tasks;
        int completed_tasks;
        std::vector<std::string> bottlenecks;
    };

    struct PerformanceMetrics {
        double task_completion_rate;
        double resource_utilization;
        double workflow_efficiency;
        std::string status;
        std::vector<std::string> optimization_suggestions;
    };

    ProjectMetrics getProjectMetrics() const;
    PerformanceMetrics getPerformanceMetrics() const;

    // System Control
    void initialize();
    void start();
    void stop();
    bool isOperational() const;
    void updateTaskPriorities();

private:
    std::vector<Task> tasks_;
    std::vector<WorkflowStage> workflow_;
    std::unordered_map<std::string, std::vector<std::string>> team_skills_;
    std::priority_queue<Task, std::vector<Task>, TaskPriority> task_queue_;
    
    // Performance tracking
    double task_completion_rate_;
    double resource_utilization_;
    double workflow_efficiency_;
    bool system_active_;
    
    // Logging
    std::shared_ptr<spdlog::logger> logger_;

    // Priority queue for task scheduling
    struct TaskPriority {
        bool operator()(const Task& a, const Task& b) const {
            // Complex priority calculation based on multiple factors
            double a_score = calculatePriorityScore(a);
            double b_score = calculatePriorityScore(b);
            return a_score < b_score;
        }

        static double calculatePriorityScore(const Task& task) {
            double score = 0.0;
            
            // Base priority from estimated hours (higher hours = higher priority)
            score += task.estimated_hours * 0.3;
            
            // Priority based on dependencies (more dependencies = higher priority)
            score += task.dependencies.size() * 10.0;
            
            // Priority based on due date (closer = higher priority)
            auto now = std::chrono::system_clock::now();
            auto time_until_due = std::chrono::duration_cast<std::chrono::hours>(
                task.due_date - now).count();
            if (time_until_due < 0) {
                // Overdue tasks get highest priority
                score += 1000.0;
            } else {
                // Exponential decay for future tasks
                score += 100.0 * std::exp(-time_until_due / 168.0); // 168 hours = 1 week
            }
            
            // Status-based priority
            if (task.status == "blocked") {
                score -= 50.0;
            } else if (task.status == "in_progress") {
                score += 20.0;
            } else if (task.status == "ready") {
                score += 10.0;
            }
            
            return score;
        }
    };

    // Helper functions
    bool checkDependencies(const Task& task) const;
    double estimateTaskDuration(const RequirementsGenerator::Requirement& req) const;
    std::string generateTaskDescription(const RequirementsGenerator::Requirement& req) const;
    void updateDependentTasks(const std::string& completed_task_id);
};
