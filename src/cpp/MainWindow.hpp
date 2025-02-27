#pragma once

#include <QMainWindow>
#include <QTimer>
#include <QLabel>
#include <memory>
#include <unordered_map>
#include "monitoring/SystemMonitor.hpp"
#include "visualization/DashboardWidget.hpp"

class QVBoxLayout;
class QTabWidget;
class QCustomPlot;

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget* parent = nullptr);
    ~MainWindow() override;

private slots:
    void updateMetrics();
    void updateComponentStatus();
    void handleSystemAlert(const QString& component, const QString& message);

private:
    void setupUi();
    void setupMonitoring();
    void createStatusPanel();
    void createVisualizationPanel();
    void setupStyles();

    // Core components
    std::unique_ptr<SystemMonitor> monitor_;
    std::unique_ptr<DashboardWidget> dashboard_;
    QTimer* updateTimer_;

    // UI components
    QWidget* centralWidget_;
    QTabWidget* tabWidget_;
    std::unordered_map<QString, QLabel*> componentLabels_;
    std::unordered_map<QString, QCustomPlot*> metricPlots_;

    // Constants
    static constexpr int UPDATE_INTERVAL_MS = 1000;
    static constexpr int MAX_HISTORY_POINTS = 100;
};
