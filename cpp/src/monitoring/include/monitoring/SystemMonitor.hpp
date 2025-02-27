#pragma once

#include <QObject>
#include <QString>
#include <QVariantMap>
#include <memory>
#include <vector>

class SystemMonitor : public QObject {
    Q_OBJECT

public:
    explicit SystemMonitor(QObject* parent = nullptr);
    ~SystemMonitor() override;

    // Core monitoring functions
    QVariantMap collectMetrics();
    bool isHealthy() const;
    QString getStatus() const;

    // Component-specific monitoring
    double getCpuUsage() const;
    double getMemoryUsage() const;
    double getBatteryLevel() const;
    double getNetworkLatency() const;
    double getEnvironmentalScore() const;

    // Alert thresholds
    void setCpuThreshold(double threshold);
    void setMemoryThreshold(double threshold);
    void setBatteryThreshold(double threshold);
    void setLatencyThreshold(double threshold);
    void setEnvironmentalThreshold(double threshold);

signals:
    void metricsUpdated(const QVariantMap& metrics);
    void alertTriggered(const QString& component, const QString& message, const QString& severity);
    void statusChanged(const QString& status);
    void healthChanged(bool healthy);

private slots:
    void checkThresholds();
    void updateMetrics();

private:
    struct Private;
    std::unique_ptr<Private> d;

    // Monitoring functions
    double calculateCpuUsage();
    double calculateMemoryUsage();
    double measureNetworkLatency();
    double calculateEnvironmentalImpact();
    
    // Analysis functions
    void analyzePerformanceTrends();
    void detectAnomalies();
    void predictMaintenance();
    
    // Utility functions
    QString formatMetric(const QString& name, double value, const QString& unit);
    void logMetric(const QString& name, double value);
};
