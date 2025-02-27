#pragma once

#include <QWidget>
#include <QVariantMap>
#include <memory>

namespace QtCharts {
    class QChartView;
    class QLineSeries;
}

class QCustomPlot;

class MonitoringTab : public QWidget {
    Q_OBJECT

public:
    explicit MonitoringTab(QWidget* parent = nullptr);
    ~MonitoringTab() override;

public slots:
    void updateMetrics(const QVariantMap& metrics);
    void clearData();
    void exportMetrics();
    void setUpdateInterval(int msec);

signals:
    void thresholdExceeded(const QString& metric, double value);
    void anomalyDetected(const QString& metric, double value);

private:
    void setupUi();
    void setupCharts();
    void updateCharts(const QVariantMap& metrics);
    void checkThresholds(const QVariantMap& metrics);
    void detectAnomalies(const QVariantMap& metrics);

    struct Private;
    std::unique_ptr<Private> d;
};
