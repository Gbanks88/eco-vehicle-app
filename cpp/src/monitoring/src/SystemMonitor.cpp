#include "monitoring/SystemMonitor.hpp"
#include <QProcess>
#include <QDateTime>
#include <QDebug>
#include <QTimer>
#include <QThread>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QHostInfo>

#ifdef Q_OS_UNIX
#include <sys/sysinfo.h>
#include <sys/statvfs.h>
#include <fstream>
#endif

struct SystemMonitor::Private {
    // Thresholds
    double cpuThreshold{80.0};
    double memoryThreshold{90.0};
    double batteryThreshold{20.0};
    double latencyThreshold{100.0};
    double environmentalThreshold{70.0};

    // Current values
    double cpuUsage{0.0};
    double memoryUsage{0.0};
    double batteryLevel{100.0};
    double networkLatency{0.0};
    double environmentalScore{100.0};

    // System state
    bool healthy{true};
    QString status{"Operational"};

    // Update timer
    QTimer* updateTimer{nullptr};

    // Network manager for latency checks
    QNetworkAccessManager* networkManager{nullptr};

    // Previous CPU measurements for delta calculation
    unsigned long long prevIdle{0};
    unsigned long long prevTotal{0};

    // Historical data for trend analysis
    struct MetricHistory {
        std::vector<double> values;
        size_t maxSize{100};
    };
    std::map<QString, MetricHistory> history;
};

SystemMonitor::SystemMonitor(QObject* parent)
    : QObject(parent)
    , d(std::make_unique<Private>())
{
    // Initialize network manager
    d->networkManager = new QNetworkAccessManager(this);

    // Setup update timer
    d->updateTimer = new QTimer(this);
    connect(d->updateTimer, &QTimer::timeout, this, &SystemMonitor::updateMetrics);
    d->updateTimer->start(1000); // Update every second
}

SystemMonitor::~SystemMonitor() = default;

QVariantMap SystemMonitor::collectMetrics() {
    QVariantMap metrics;
    metrics["cpu_usage"] = d->cpuUsage;
    metrics["memory_usage"] = d->memoryUsage;
    metrics["battery_level"] = d->batteryLevel;
    metrics["network_latency"] = d->networkLatency;
    metrics["environmental_score"] = d->environmentalScore;
    return metrics;
}

double SystemMonitor::calculateCpuUsage() {
#ifdef Q_OS_UNIX
    std::ifstream statFile("/proc/stat");
    if (!statFile.is_open()) {
        qWarning() << "Failed to open /proc/stat";
        return 0.0;
    }

    std::string line;
    std::getline(statFile, line);
    statFile.close();

    unsigned long long user, nice, system, idle, iowait, irq, softirq, steal;
    sscanf(line.c_str(), "cpu %llu %llu %llu %llu %llu %llu %llu %llu",
           &user, &nice, &system, &idle, &iowait, &irq, &softirq, &steal);

    unsigned long long idleAllTime = idle + iowait;
    unsigned long long systemAllTime = system + irq + softirq;
    unsigned long long totalTime = user + nice + systemAllTime + idleAllTime + steal;

    double percent = 0.0;
    if (d->prevTotal != 0) {
        unsigned long long totalDelta = totalTime - d->prevTotal;
        unsigned long long idleDelta = idleAllTime - d->prevIdle;
        percent = (1.0 - static_cast<double>(idleDelta) / totalDelta) * 100.0;
    }

    d->prevIdle = idleAllTime;
    d->prevTotal = totalTime;

    return percent;
#else
    // Implement for other platforms
    return 0.0;
#endif
}

double SystemMonitor::calculateMemoryUsage() {
#ifdef Q_OS_UNIX
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        unsigned long totalRam = si.totalram;
        unsigned long freeRam = si.freeram;
        return (1.0 - static_cast<double>(freeRam) / totalRam) * 100.0;
    }
#endif
    return 0.0;
}

double SystemMonitor::measureNetworkLatency() {
    // Ping multiple endpoints and average
    QStringList hosts = {"8.8.8.8", "1.1.1.1"};
    double totalLatency = 0.0;
    int successfulPings = 0;

    for (const QString& host : hosts) {
        QProcess ping;
        ping.start("ping", {"-c", "1", "-W", "1", host});
        if (ping.waitForFinished(1500)) {
            QString output = ping.readAllStandardOutput();
            QRegExp rx("time=([0-9.]+)");
            if (rx.indexIn(output) != -1) {
                totalLatency += rx.cap(1).toDouble();
                successfulPings++;
            }
        }
    }

    return successfulPings > 0 ? totalLatency / successfulPings : 999.9;
}

double SystemMonitor::calculateEnvironmentalImpact() {
    // Calculate environmental score based on system metrics
    double cpuImpact = d->cpuUsage * 0.4;  // 40% weight
    double memoryImpact = d->memoryUsage * 0.3;  // 30% weight
    double networkImpact = (d->networkLatency / 100.0) * 0.3;  // 30% weight

    return 100.0 - (cpuImpact + memoryImpact + networkImpact);
}

void SystemMonitor::updateMetrics() {
    // Update all metrics
    d->cpuUsage = calculateCpuUsage();
    d->memoryUsage = calculateMemoryUsage();
    d->networkLatency = measureNetworkLatency();
    d->environmentalScore = calculateEnvironmentalImpact();

    // Update history
    auto updateHistory = [this](const QString& metric, double value) {
        auto& history = d->history[metric];
        history.values.push_back(value);
        if (history.values.size() > history.maxSize) {
            history.values.erase(history.values.begin());
        }
    };

    updateHistory("cpu_usage", d->cpuUsage);
    updateHistory("memory_usage", d->memoryUsage);
    updateHistory("network_latency", d->networkLatency);
    updateHistory("environmental_score", d->environmentalScore);

    // Check thresholds and emit signals
    checkThresholds();
    emit metricsUpdated(collectMetrics());
}

void SystemMonitor::checkThresholds() {
    bool wasHealthy = d->healthy;
    d->healthy = true;

    auto checkMetric = [this](double value, double threshold, 
                             const QString& component, const QString& unit,
                             bool higherIsBad = true) {
        if ((higherIsBad && value > threshold) || 
            (!higherIsBad && value < threshold)) {
            d->healthy = false;
            emit alertTriggered(component,
                QString("%1 is at %2%3 (threshold: %4%3)")
                    .arg(component)
                    .arg(value, 0, 'f', 1)
                    .arg(unit)
                    .arg(threshold, 0, 'f', 1),
                "warning");
        }
    };

    checkMetric(d->cpuUsage, d->cpuThreshold, "CPU Usage", "%");
    checkMetric(d->memoryUsage, d->memoryThreshold, "Memory Usage", "%");
    checkMetric(d->batteryLevel, d->batteryThreshold, "Battery Level", "%", false);
    checkMetric(d->networkLatency, d->latencyThreshold, "Network Latency", "ms");
    checkMetric(d->environmentalScore, d->environmentalThreshold, 
                "Environmental Score", "%", false);

    if (d->healthy != wasHealthy) {
        emit healthChanged(d->healthy);
        d->status = d->healthy ? "Operational" : "Warning";
        emit statusChanged(d->status);
    }
}

// Getter implementations
double SystemMonitor::getCpuUsage() const { return d->cpuUsage; }
double SystemMonitor::getMemoryUsage() const { return d->memoryUsage; }
double SystemMonitor::getBatteryLevel() const { return d->batteryLevel; }
double SystemMonitor::getNetworkLatency() const { return d->networkLatency; }
double SystemMonitor::getEnvironmentalScore() const { return d->environmentalScore; }
bool SystemMonitor::isHealthy() const { return d->healthy; }
QString SystemMonitor::getStatus() const { return d->status; }

// Threshold setters
void SystemMonitor::setCpuThreshold(double threshold) { d->cpuThreshold = threshold; }
void SystemMonitor::setMemoryThreshold(double threshold) { d->memoryThreshold = threshold; }
void SystemMonitor::setBatteryThreshold(double threshold) { d->batteryThreshold = threshold; }
void SystemMonitor::setLatencyThreshold(double threshold) { d->latencyThreshold = threshold; }
void SystemMonitor::setEnvironmentalThreshold(double threshold) { d->environmentalThreshold = threshold; }
