#include "automation_bot.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>

AutomationBot::AutomationBot() {
    // Initialize default workflow stages
    workflow_stages_ = {
        WorkflowStage{
            "Planning",
            {"requirements_reviewed", "dependencies_checked"},
            [](const Task& t) { return !t.description.empty(); }
        },
        WorkflowStage{
            "Implementation",
            {"planning_complete", "resources_available"},
            [](const Task& t) { return t.assignee != ""; }
        },
        WorkflowStage{
            "Testing",
            {"implementation_complete", "tests_written"},
            [](const Task& t) { return true; }
        },
        WorkflowStage{
            "Review",
            {"testing_complete", "documentation_updated"},
            [](const Task& t) { return true; }
        }
    };
}

std::vector<AutomationBot::Task> AutomationBot::createTasksFromRequirements(
    const std::vector<RequirementsGenerator::Requirement>& requirements) {
    
    std::vector<Task> new_tasks;
    for (const auto& req : requirements) {
        Task task;
        task.id = "TASK-" + req.id;
        task.requirement_id = req.id;
        task.title = req.category + ": " + req.type;
        task.description = generateTaskDescription(req);
        task.estimated_hours = estimateTaskDuration(req);
        task.status = "Planning";
        task.dependencies = req.dependencies;
        
        // Set due date based on complexity and dependencies
        auto now = std::chrono::system_clock::now();
        task.due_date = now + std::chrono::hours(static_cast<int>(task.estimated_hours * 2));
        
        new_tasks.push_back(task);
    }
    
    tasks_.insert(tasks_.end(), new_tasks.begin(), new_tasks.end());
    prioritizeTasks();
    return new_tasks;
}

void AutomationBot::prioritizeTasks() {
    // Clear existing queue
    task_queue_ = std::priority_queue<Task, std::vector<Task>, TaskPriority>();
    
    // Add all non-completed tasks to queue
    for (const auto& task : tasks_) {
        if (task.status != "Completed") {
            task_queue_.push(task);
        }
    }
}

std::vector<AutomationBot::Task> AutomationBot::getNextTasks(int count) {
    std::vector<Task> next_tasks;
    while (!task_queue_.empty() && next_tasks.size() < static_cast<size_t>(count)) {
        Task task = task_queue_.top();
        if (checkDependencies(task)) {
            next_tasks.push_back(task);
        }
        task_queue_.pop();
    }
    return next_tasks;
}

void AutomationBot::updateTaskStatus(const std::string& task_id, const std::string& new_status) {
    auto it = std::find_if(tasks_.begin(), tasks_.end(),
                          [&](const Task& t) { return t.id == task_id; });
    
    if (it != tasks_.end()) {
        it->status = new_status;
        if (new_status == "Completed") {
            updateDependentTasks(task_id);
        }
        prioritizeTasks();
    }
}

void AutomationBot::addTeamMember(const std::string& name, 
                                 const std::vector<std::string>& skills) {
    team_skills_[name] = skills;
    assigned_tasks_[name] = std::vector<Task>();
}

void AutomationBot::assignTask(const std::string& task_id, const std::string& assignee) {
    if (team_skills_.find(assignee) == team_skills_.end()) {
        throw std::runtime_error("Team member not found");
    }
    
    auto task_it = std::find_if(tasks_.begin(), tasks_.end(),
                               [&](const Task& t) { return t.id == task_id; });
    
    if (task_it != tasks_.end()) {
        task_it->assignee = assignee;
        assigned_tasks_[assignee].push_back(*task_it);
    }
}

double AutomationBot::calculateWorkload(const std::string& team_member) const {
    auto it = assigned_tasks_.find(team_member);
    if (it == assigned_tasks_.end()) {
        return 0.0;
    }
    
    double total_hours = 0.0;
    for (const auto& task : it->second) {
        if (task.status != "Completed") {
            total_hours += task.estimated_hours;
        }
    }
    return total_hours;
}

AutomationBot::ProjectMetrics AutomationBot::getProjectMetrics() const {
    ProjectMetrics metrics;
    metrics.total_tasks = tasks_.size();
    metrics.completed_tasks = std::count_if(tasks_.begin(), tasks_.end(),
        [](const Task& t) { return t.status == "Completed"; });
    
    metrics.completion_percentage = metrics.total_tasks > 0 ?
        (static_cast<double>(metrics.completed_tasks) / metrics.total_tasks) * 100.0 : 0.0;
    
    double total_duration = 0.0;
    for (const auto& task : tasks_) {
        total_duration += task.estimated_hours;
        metrics.tasks_by_status[task.status]++;
    }
    
    metrics.average_task_duration = metrics.total_tasks > 0 ?
        total_duration / metrics.total_tasks : 0.0;
    
    for (const auto& pair : assigned_tasks_) {
        metrics.team_workload[pair.first] = calculateWorkload(pair.first);
    }
    
    return metrics;
}

bool AutomationBot::checkDependencies(const Task& task) const {
    for (const auto& dep_id : task.dependencies) {
        auto it = std::find_if(tasks_.begin(), tasks_.end(),
            [&](const Task& t) { return t.requirement_id == dep_id; });
        
        if (it == tasks_.end() || it->status != "Completed") {
            return false;
        }
    }
    return true;
}

double AutomationBot::estimateTaskDuration(const RequirementsGenerator::Requirement& req) const {
    // Base estimation on complexity and type
    double base_hours = req.complexity * 2.0;
    
    // Adjust based on requirement type
    if (req.type == "Technical" || req.type == "Integration") {
        base_hours *= 1.5;
    }
    
    // Add time for dependencies
    base_hours += req.dependencies.size() * 2.0;
    
    return base_hours;
}

std::string AutomationBot::generateTaskDescription(const RequirementsGenerator::Requirement& req) const {
    return "Implementation task for " + req.description + "\n\n" +
           "Category: " + req.category + "\n" +
           "Type: " + req.type + "\n" +
           "Area: " + req.area + "\n" +
           "Complexity: " + std::to_string(req.complexity) + "\n" +
           "Dependencies: " + std::to_string(req.dependencies.size());
}

void AutomationBot::updateDependentTasks(const std::string& completed_task_id) {
    for (auto& task : tasks_) {
        auto it = std::find(task.dependencies.begin(), task.dependencies.end(), completed_task_id);
        if (it != task.dependencies.end()) {
            task.dependencies.erase(it);
        }
    }
}
