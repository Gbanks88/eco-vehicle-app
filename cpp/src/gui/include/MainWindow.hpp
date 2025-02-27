#pragma once

#include <QMainWindow>
#include <QTabWidget>
#include <memory>

class SystemMonitor;
class DashboardWidget;
class MLModelManager;
class SecurityManager;
class BackupManager;

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget* parent = nullptr);
    ~MainWindow() override;

private slots:
    // Dashboard Actions
    void onMetricsUpdate(const QVariantMap& metrics);
    void onAlertTriggered(const QString& alert, const QString& severity);
    void onModelPrediction(const QString& model, const QVariantMap& prediction);
    
    // Security Actions
    void onSecurityAlert(const QString& alert);
    void onAuthenticationRequired();
    void onAccessDenied(const QString& resource);
    
    // Backup Actions
    void onBackupStarted();
    void onBackupCompleted(bool success);
    void onRestoreStarted();
    void onRestoreCompleted(bool success);

    // Settings
    void showSettings();
    void applySettings();
    void exportData();
    void importData();

private:
    void setupUi();
    void setupConnections();
    void setupMenus();
    void loadSettings();
    void saveSettings();

    struct Private;
    std::unique_ptr<Private> d;
};
