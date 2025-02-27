#pragma once

#include <QWidget>
#include <QString>
#include <QVariantMap>
#include <memory>

namespace QtCharts {
    class QChartView;
    class QLineSeries;
}

class QCustomPlot;
class QLabel;

class DashboardWidget : public QWidget {
    Q_OBJECT

public:
    explicit DashboardWidget(QWidget* parent = nullptr);
    ~DashboardWidget() override;

    // Update methods
    void updateMetrics(const QVariantMap& metrics);
    void addAlert(const QString& component, const QString& message, const QString& severity = "info");
    void clearAlerts();

    // Customization
    void setUpdateInterval(int msec);
    void setMaxDataPoints(int points);
    void setTheme(const QString& theme);

public slots:
    void exportData(const QString& format = "csv");
    void saveScreenshot(const QString& filename = QString());
    void resetZoom();

signals:
    void metricClicked(const QString& metric);
    void alertClicked(const QString& alert);
    void thresholdExceeded(const QString& metric, double value, double threshold);

protected:
    void resizeEvent(QResizeEvent* event) override;
    void showEvent(QShowEvent* event) override;

private:
    struct Private;
    std::unique_ptr<Private> d;

    // UI setup
    void setupUi();
    void setupCharts();
    void setupAlerts();
    void setupLayout();
    void setupConnections();

    // Chart management
    void createMetricChart(const QString& metric, const QString& title, const QString& yAxisLabel);
    void updateMetricChart(const QString& metric, double value);
    void styleChart(QtCharts::QChartView* chart);

    // Data management
    void pruneData();
    void calculateStatistics();
    void detectAnomalies();

    // Styling
    void applyTheme(const QString& theme);
    void updateColorScheme();
    QString getMetricColor(const QString& metric, double value);

    // Utility functions
    QString formatValue(double value, const QString& metric);
    QString generateTooltip(const QString& metric, double value);
};
