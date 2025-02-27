#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "eco_vehicle/analysis/survey_analyzer.hpp"

namespace py = pybind11;
using namespace eco_vehicle::analysis;

PYBIND11_MODULE(survey_analysis, m) {
    m.doc() = "Survey analysis module for eco vehicle project"; 

    py::class_<SurveyResponse>(m, "SurveyResponse")
        .def(py::init<>())
        .def_readwrite("employee_id", &SurveyResponse::employee_id)
        .def_readwrite("department", &SurveyResponse::department)
        .def_readwrite("role", &SurveyResponse::role)
        .def_readwrite("satisfaction_scores", &SurveyResponse::satisfaction_scores)
        .def_readwrite("feedback_comments", &SurveyResponse::feedback_comments)
        .def_readwrite("timestamp", &SurveyResponse::timestamp);

    py::class_<DepartmentMetrics>(m, "DepartmentMetrics")
        .def(py::init<>())
        .def_readwrite("name", &DepartmentMetrics::name)
        .def_readwrite("avg_satisfaction", &DepartmentMetrics::avg_satisfaction)
        .def_readwrite("turnover_rate", &DepartmentMetrics::turnover_rate)
        .def_readwrite("common_issues", &DepartmentMetrics::common_issues)
        .def_readwrite("improvement_suggestions", &DepartmentMetrics::improvement_suggestions);

    py::class_<SurveyAnalyzer>(m, "SurveyAnalyzer")
        .def(py::init<const Config&>())
        .def("load_survey_data", &SurveyAnalyzer::load_survey_data)
        .def("analyze_department", &SurveyAnalyzer::analyze_department)
        .def("generate_visualization", &SurveyAnalyzer::generate_visualization)
        .def("generate_organization_diagrams", &SurveyAnalyzer::generate_organization_diagrams)
        .def("export_results", &SurveyAnalyzer::export_results);
}
