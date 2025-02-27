#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "automation_bot.hpp"

namespace py = pybind11;

PYBIND11_MODULE(automation_bot_cpp, m) {
    m.doc() = "C++ Automation Bot for Managing Software Requirements";

    py::class_<AutomationBot::Task>(m, "Task")
        .def(py::init<>())
        .def_readwrite("id", &AutomationBot::Task::id)
        .def_readwrite("requirement_id", &AutomationBot::Task::requirement_id)
        .def_readwrite("title", &AutomationBot::Task::title)
        .def_readwrite("description", &AutomationBot::Task::description)
        .def_readwrite("assignee", &AutomationBot::Task::assignee)
        .def_readwrite("estimated_hours", &AutomationBot::Task::estimated_hours)
        .def_readwrite("status", &AutomationBot::Task::status)
        .def_readwrite("dependencies", &AutomationBot::Task::dependencies)
        .def_readwrite("due_date", &AutomationBot::Task::due_date);

    py::class_<AutomationBot::ProjectMetrics>(m, "ProjectMetrics")
        .def(py::init<>())
        .def_readwrite("total_tasks", &AutomationBot::ProjectMetrics::total_tasks)
        .def_readwrite("completed_tasks", &AutomationBot::ProjectMetrics::completed_tasks)
        .def_readwrite("completion_percentage", &AutomationBot::ProjectMetrics::completion_percentage)
        .def_readwrite("average_task_duration", &AutomationBot::ProjectMetrics::average_task_duration)
        .def_readwrite("tasks_by_status", &AutomationBot::ProjectMetrics::tasks_by_status)
        .def_readwrite("team_workload", &AutomationBot::ProjectMetrics::team_workload);

    py::class_<AutomationBot>(m, "AutomationBot")
        .def(py::init<>())
        .def("create_tasks_from_requirements", &AutomationBot::createTasksFromRequirements)
        .def("prioritize_tasks", &AutomationBot::prioritizeTasks)
        .def("get_next_tasks", &AutomationBot::getNextTasks)
        .def("update_task_status", &AutomationBot::updateTaskStatus)
        .def("add_team_member", &AutomationBot::addTeamMember)
        .def("assign_task", &AutomationBot::assignTask)
        .def("calculate_workload", &AutomationBot::calculateWorkload)
        .def("get_project_metrics", &AutomationBot::getProjectMetrics);
}
