#pragma once

#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <pdfcpp/pdf.hpp>
#include <xlsxwriter.h>
#include "DatabaseManager.hpp"
#include "AutodeskIntegration.hpp"

namespace circuit {

class ReportGenerator {
public:
    struct ReportConfig {
        std::string title;
        std::string author;
        std::string company;
        std::vector<std::string> sections;
        std::chrono::system_clock::time_point start_date;
        std::chrono::system_clock::time_point end_date;
        std::string output_format; // "pdf" or "xlsx"
        bool include_3d_models;    // Whether to include Autodesk Viewer links
    };

    struct ChartData {
        std::string type; // "line", "bar", "pie"
        std::string title;
        std::vector<std::string> labels;
        std::vector<double> values;
        std::map<std::string, std::vector<double>> series;
    };

    ReportGenerator(std::shared_ptr<DatabaseManager> db,
                   std::shared_ptr<AutodeskIntegration> autodesk = nullptr)
        : db_(db), autodesk_(autodesk) {}

    bool generateReport(const ReportConfig& config,
                       const std::string& output_path) {
        if (config.output_format == "pdf") {
            return generatePdfReport(config, output_path);
        }
        else if (config.output_format == "xlsx") {
            return generateExcelReport(config, output_path);
        }
        return false;
    }

private:
    std::shared_ptr<DatabaseManager> db_;
    std::shared_ptr<AutodeskIntegration> autodesk_;

    bool generatePdfReport(const ReportConfig& config,
                          const std::string& output_path) {
        try {
            PDF pdf;
            
            // Add header
            pdf.set_font("Helvetica-Bold", 24);
            pdf.add_text(config.title);
            
            pdf.set_font("Helvetica", 12);
            pdf.add_text("Generated: " + getCurrentDateTime());
            pdf.add_text("Author: " + config.author);
            pdf.add_text("Company: " + config.company);
            
            // Add sections
            for (const auto& section : config.sections) {
                addReportSection(pdf, section, config);
            }
            
            // Add charts
            auto efficiency_data = generateEfficiencyChart();
            addChart(pdf, efficiency_data);
            
            auto materials_data = generateMaterialsChart();
            addChart(pdf, materials_data);
            
            // Add 3D model viewer if enabled
            if (config.include_3d_models) {
                add3DModelViewer(pdf, "model_urn");
            }
            
            // Add summary
            addSummary(pdf, config);
            
            // Save PDF
            pdf.save(output_path);
            return true;
        }
        catch (const std::exception& e) {
            return false;
        }
    }

    bool generateExcelReport(const ReportConfig& config,
                            const std::string& output_path) {
        lxw_workbook* workbook = workbook_new(output_path.c_str());
        lxw_worksheet* worksheet = workbook_add_worksheet(workbook, NULL);
        
        // Add header
        lxw_format* header_format = workbook_add_format(workbook);
        format_set_bold(header_format);
        format_set_font_size(header_format, 14);
        
        worksheet_write_string(worksheet, 0, 0, config.title.c_str(), 
                             header_format);
        worksheet_write_string(worksheet, 1, 0, 
                             ("Generated: " + getCurrentDateTime()).c_str(), 
                             NULL);
        
        // Add data
        int row = 3;
        for (const auto& section : config.sections) {
            row = addExcelSection(worksheet, section, row, config);
        }
        
        // Add charts
        lxw_chart* efficiency_chart = workbook_add_chart(workbook, LXW_CHART_LINE);
        addExcelChart(worksheet, efficiency_chart, 
                     generateEfficiencyChart(), row);
        row += 15;
        
        lxw_chart* materials_chart = workbook_add_chart(workbook, LXW_CHART_PIE);
        addExcelChart(worksheet, materials_chart, 
                     generateMaterialsChart(), row);
        
        // Add 3D model metadata if enabled
        if (config.include_3d_models) {
            addExcelModelMetadata(worksheet, "object_id", row);
        }
        
        workbook_close(workbook);
        return true;
    }

    void addReportSection(PDF& pdf, 
                         const std::string& section,
                         const ReportConfig& config) {
        pdf.set_font("Helvetica-Bold", 16);
        pdf.add_text(section);
        
        pdf.set_font("Helvetica", 12);
        
        if (section == "Efficiency Analysis") {
            addEfficiencyAnalysis(pdf, config);
        }
        else if (section == "Material Recovery") {
            addMaterialRecovery(pdf, config);
        }
        else if (section == "Operator Performance") {
            addOperatorPerformance(pdf, config);
        }
        else if (section == "Environmental Impact") {
            addEnvironmentalImpact(pdf, config);
        }
    }

    int addExcelSection(lxw_worksheet* worksheet,
                       const std::string& section,
                       int start_row,
                       const ReportConfig& config) {
        lxw_format* section_format = workbook_add_format(worksheet->workbook);
        format_set_bold(section_format);
        
        worksheet_write_string(worksheet, start_row, 0, 
                             section.c_str(), section_format);
        start_row++;
        
        if (section == "Efficiency Analysis") {
            return addExcelEfficiencyAnalysis(worksheet, start_row, config);
        }
        else if (section == "Material Recovery") {
            return addExcelMaterialRecovery(worksheet, start_row, config);
        }
        else if (section == "Operator Performance") {
            return addExcelOperatorPerformance(worksheet, start_row, config);
        }
        else if (section == "Environmental Impact") {
            return addExcelEnvironmentalImpact(worksheet, start_row, config);
        }
        
        return start_row;
    }

    void addEfficiencyAnalysis(PDF& pdf, const ReportConfig& config) {
        auto efficiency_data = db_->getEfficiencyData(
            config.start_date, config.end_date);
        
        pdf.add_text("Overall Efficiency: " + 
                    std::to_string(efficiency_data.overall_efficiency) + "%");
        pdf.add_text("Total Components Processed: " + 
                    std::to_string(efficiency_data.total_processed));
        pdf.add_text("Success Rate: " + 
                    std::to_string(efficiency_data.success_rate) + "%");
    }

    int addExcelEfficiencyAnalysis(lxw_worksheet* worksheet,
                                  int start_row,
                                  const ReportConfig& config) {
        auto efficiency_data = db_->getEfficiencyData(
            config.start_date, config.end_date);
        
        worksheet_write_string(worksheet, start_row, 0, 
                             "Overall Efficiency", NULL);
        worksheet_write_number(worksheet, start_row, 1, 
                             efficiency_data.overall_efficiency, NULL);
        start_row++;
        
        worksheet_write_string(worksheet, start_row, 0, 
                             "Total Components Processed", NULL);
        worksheet_write_number(worksheet, start_row, 1, 
                             efficiency_data.total_processed, NULL);
        start_row++;
        
        worksheet_write_string(worksheet, start_row, 0, 
                             "Success Rate", NULL);
        worksheet_write_number(worksheet, start_row, 1, 
                             efficiency_data.success_rate, NULL);
        start_row++;
        
        return start_row;
    }

    ChartData generateEfficiencyChart() {
        ChartData data;
        data.type = "line";
        data.title = "Efficiency Over Time";
        
        // Get efficiency data from database
        auto efficiency_trends = db_->getEfficiencyTrends();
        
        for (const auto& point : efficiency_trends) {
            data.labels.push_back(point.date);
            data.values.push_back(point.efficiency);
        }
        
        return data;
    }

    ChartData generateMaterialsChart() {
        ChartData data;
        data.type = "pie";
        data.title = "Material Recovery Distribution";
        
        // Get materials data from database
        auto materials = db_->getMaterialsRecovered();
        
        for (const auto& material : materials) {
            data.labels.push_back(material.type);
            data.values.push_back(material.quantity);
        }
        
        return data;
    }

    void addChart(PDF& pdf, const ChartData& data) {
        // Add chart title
        pdf.set_font("Helvetica-Bold", 14);
        pdf.add_text(data.title);
        
        // Add chart (implementation depends on PDF library capabilities)
        // This is a placeholder for actual chart rendering
        pdf.add_text("Chart data points: " + 
                    std::to_string(data.values.size()));
    }

    void addExcelChart(lxw_worksheet* worksheet,
                      lxw_chart* chart,
                      const ChartData& data,
                      int start_row) {
        // Write data for chart
        for (size_t i = 0; i < data.labels.size(); i++) {
            worksheet_write_string(worksheet, start_row + i, 0, 
                                 data.labels[i].c_str(), NULL);
            worksheet_write_number(worksheet, start_row + i, 1, 
                                 data.values[i], NULL);
        }
        
        // Configure chart
        chart_add_series(chart, NULL, 
                        ("=Sheet1!$B$" + 
                         std::to_string(start_row + 1) + ":$B$" + 
                         std::to_string(start_row + data.labels.size())).c_str());
        
        chart_title_set_name(chart, data.title.c_str());
        
        // Insert chart into worksheet
        worksheet_insert_chart(worksheet, start_row, 3, chart);
    }

    void add3DModelViewer(PDF& pdf, const std::string& model_urn) {
        if (!autodesk_) return;

        auto viewer_config = autodesk_->getViewerConfig(model_urn);
        
        // Add viewer iframe HTML
        std::string viewer_html = 
            "<div style=\"width: 100%; height: 400px;\">\n"
            "  <iframe src=\"https://viewer.autodesk.com/viewer.html?"
            "urn=" + viewer_config.document_urn + "&"
            "token=" + viewer_config.access_token + "\"\n"
            "    style=\"width: 100%; height: 100%; border: none;\">\n"
            "  </iframe>\n"
            "</div>";

        pdf.add_html(viewer_html);
    }

    void addModelMetadata(PDF& pdf, const std::string& object_id) {
        if (!autodesk_) return;

        auto metadata = autodesk_->getModelMetadata(object_id);
        if (!metadata) return;

        pdf.set_font("Helvetica-Bold", 14);
        pdf.add_text("3D Model Information");
        
        pdf.set_font("Helvetica", 12);
        pdf.add_text("File Name: " + metadata->file_name);
        pdf.add_text("File Type: " + metadata->file_type);
        pdf.add_text("Size: " + std::to_string(metadata->file_size) + " bytes");
        pdf.add_text("Created: " + metadata->creation_date);
        pdf.add_text("Last Modified: " + metadata->last_modified_date);
    }

    void addExcelModelMetadata(lxw_worksheet* worksheet,
                             const std::string& object_id,
                             int& row) {
        if (!autodesk_) return;

        auto metadata = autodesk_->getModelMetadata(object_id);
        if (!metadata) return;

        lxw_format* header_format = workbook_add_format(worksheet->workbook);
        format_set_bold(header_format);
        
        worksheet_write_string(worksheet, row, 0, "3D Model Information", 
                             header_format);
        row++;
        
        worksheet_write_string(worksheet, row, 0, "File Name", NULL);
        worksheet_write_string(worksheet, row, 1, metadata->file_name.c_str(), 
                             NULL);
        row++;
        
        worksheet_write_string(worksheet, row, 0, "File Type", NULL);
        worksheet_write_string(worksheet, row, 1, metadata->file_type.c_str(), 
                             NULL);
        row++;
        
        worksheet_write_string(worksheet, row, 0, "Size (bytes)", NULL);
        worksheet_write_number(worksheet, row, 1, metadata->file_size, NULL);
        row++;
        
        worksheet_write_string(worksheet, row, 0, "Created", NULL);
        worksheet_write_string(worksheet, row, 1, 
                             metadata->creation_date.c_str(), NULL);
        row++;
        
        worksheet_write_string(worksheet, row, 0, "Last Modified", NULL);
        worksheet_write_string(worksheet, row, 1, 
                             metadata->last_modified_date.c_str(), NULL);
        row++;
    }

    std::string getCurrentDateTime() {
        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);
        std::string time_str = std::ctime(&time);
        time_str.pop_back(); // Remove newline
        return time_str;
    }

    void addSummary(PDF& pdf, const ReportConfig& config) {
        pdf.set_font("Helvetica-Bold", 16);
        pdf.add_text("Summary");
        
        pdf.set_font("Helvetica", 12);
        
        // Add key metrics and findings
        auto metrics = db_->getKeyMetrics(config.start_date, config.end_date);
        
        pdf.add_text("Key Findings:");
        for (const auto& metric : metrics) {
            pdf.add_text("- " + metric);
        }
    }
};

} // namespace circuit
