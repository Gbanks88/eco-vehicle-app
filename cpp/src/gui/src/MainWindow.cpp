#include "MainWindow.hpp"
#include "DashboardWidget.hpp"
#include "MonitoringTab.hpp"
#include "MLModelTab.hpp"
#include "SecurityTab.hpp"
#include "BackupTab.hpp"

#include <QMenuBar>
#include <QStatusBar>
#include <QMessageBox>
#include <QSettings>
#include <QTabWidget>
#include <QVBoxLayout>
#include <QApplication>
#include <QStyle>

struct MainWindow::Private {
    QTabWidget* tabWidget{nullptr};
    DashboardWidget* dashboard{nullptr};
    MonitoringTab* monitoringTab{nullptr};
    MLModelTab* mlModelTab{nullptr};
    SecurityTab* securityTab{nullptr};
    BackupTab* backupTab{nullptr};
    
    // Core components
    std::unique_ptr<SystemMonitor> systemMonitor;
    std::unique_ptr<MLModelManager> modelManager;
    std::unique_ptr<SecurityManager> securityManager;
    std::unique_ptr<BackupManager> backupManager;
};

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
    , d(std::make_unique<Private>())
{
    // Setup translations
    setupTranslations();
    
    // Initialize UI and components
    try {
        setupUi();
        setupConnections();
        setupMenus();
        setupAccessibility();
        loadSettings();
        initializeComponents();
        
        // Set window properties
        setWindowTitle(tr("Eco-Vehicle Monitoring System"));
        setMinimumSize(1200, 800);
        
        // Load last session state if available
        restoreState();
        
    } catch (const std::exception& e) {
        QMessageBox::critical(this, tr("Initialization Error"),
            tr("Failed to initialize application: %1").arg(e.what()));
        QTimer::singleShot(0, qApp, &QApplication::quit);
    }
}

MainWindow::~MainWindow() = default;

void MainWindow::setupUi()
{
    // Create central widget and layout
    auto* centralWidget = new QWidget(this);
    auto* layout = new QVBoxLayout(centralWidget);
    setCentralWidget(centralWidget);

    // Create tab widget
    d->tabWidget = new QTabWidget(this);
    layout->addWidget(d->tabWidget);

    // Create and add tabs
    d->dashboard = new DashboardWidget(this);
    d->monitoringTab = new MonitoringTab(this);
    d->mlModelTab = new MLModelTab(this);
    d->securityTab = new SecurityTab(this);
    d->backupTab = new BackupTab(this);

    d->tabWidget->addTab(d->dashboard, tr("Dashboard"));
    d->tabWidget->addTab(d->monitoringTab, tr("Monitoring"));
    d->tabWidget->addTab(d->mlModelTab, tr("ML Models"));
    d->tabWidget->addTab(d->securityTab, tr("Security"));
    d->tabWidget->addTab(d->backupTab, tr("Backup & Restore"));

    // Set up status bar
    statusBar()->showMessage(tr("System Ready"));
}

void MainWindow::setupConnections()
{
    // Connect monitoring signals
    connect(d->systemMonitor.get(), &SystemMonitor::metricsUpdated,
            this, &MainWindow::onMetricsUpdate);
    connect(d->systemMonitor.get(), &SystemMonitor::alertTriggered,
            this, &MainWindow::onAlertTriggered);

    // Connect ML model signals
    connect(d->modelManager.get(), &MLModelManager::predictionReady,
            this, &MainWindow::onModelPrediction);

    // Connect security signals
    connect(d->securityManager.get(), &SecurityManager::securityAlert,
            this, &MainWindow::onSecurityAlert);
    connect(d->securityManager.get(), &SecurityManager::authenticationRequired,
            this, &MainWindow::onAuthenticationRequired);

    // Connect backup signals
    connect(d->backupManager.get(), &BackupManager::backupStarted,
            this, &MainWindow::onBackupStarted);
    connect(d->backupManager.get(), &BackupManager::backupCompleted,
            this, &MainWindow::onBackupCompleted);
}

void MainWindow::setupMenus()
{
    // File menu
    auto* fileMenu = menuBar()->addMenu(tr("&File"));
    fileMenu->addAction(tr("&Settings"), this, &MainWindow::showSettings);
    fileMenu->addSeparator();
    fileMenu->addAction(tr("&Export Data"), this, &MainWindow::exportData);
    fileMenu->addAction(tr("&Import Data"), this, &MainWindow::importData);
    fileMenu->addSeparator();
    fileMenu->addAction(tr("E&xit"), qApp, &QApplication::quit);

    // View menu
    auto* viewMenu = menuBar()->addMenu(tr("&View"));
    viewMenu->addAction(tr("&Dashboard"), [this]() { d->tabWidget->setCurrentWidget(d->dashboard); });
    viewMenu->addAction(tr("&Monitoring"), [this]() { d->tabWidget->setCurrentWidget(d->monitoringTab); });
    viewMenu->addAction(tr("&ML Models"), [this]() { d->tabWidget->setCurrentWidget(d->mlModelTab); });
    viewMenu->addAction(tr("&Security"), [this]() { d->tabWidget->setCurrentWidget(d->securityTab); });
    viewMenu->addAction(tr("&Backup"), [this]() { d->tabWidget->setCurrentWidget(d->backupTab); });

    // Tools menu
    auto* toolsMenu = menuBar()->addMenu(tr("&Tools"));
    toolsMenu->addAction(tr("&Start Monitoring"), d->systemMonitor.get(), &SystemMonitor::startMonitoring);
    toolsMenu->addAction(tr("&Stop Monitoring"), d->systemMonitor.get(), &SystemMonitor::stopMonitoring);
    toolsMenu->addSeparator();
    toolsMenu->addAction(tr("&Backup Now"), d->backupManager.get(), &BackupManager::startBackup);
    toolsMenu->addAction(tr("&Restore"), d->backupManager.get(), &BackupManager::startRestore);

    // Help menu
    auto* helpMenu = menuBar()->addMenu(tr("&Help"));
    helpMenu->addAction(tr("&About"), [this]() {
        QMessageBox::about(this, tr("About Eco-Vehicle Monitor"),
            tr("Eco-Vehicle Monitoring System\n"
               "Version 1.0\n\n"
               "A comprehensive monitoring solution for eco-friendly vehicles."));
    });
}

void MainWindow::onMetricsUpdate(const QVariantMap& metrics)
{
    d->dashboard->updateMetrics(metrics);
    d->monitoringTab->updateMetrics(metrics);
    statusBar()->showMessage(tr("Metrics Updated: %1").arg(QTime::currentTime().toString()));
}

void MainWindow::onAlertTriggered(const QString& alert, const QString& severity)
{
    // Update UI with alert
    d->dashboard->addAlert(alert, severity);
    
    // Show notification based on severity
    if (severity == "critical") {
        QMessageBox::critical(this, tr("Critical Alert"), alert);
    } else if (severity == "warning") {
        QMessageBox::warning(this, tr("Warning"), alert);
    }
}

void MainWindow::onModelPrediction(const QString& model, const QVariantMap& prediction)
{
    d->mlModelTab->updatePrediction(model, prediction);
}

void MainWindow::onSecurityAlert(const QString& alert)
{
    d->securityTab->addSecurityAlert(alert);
    QMessageBox::warning(this, tr("Security Alert"), alert);
}

void MainWindow::onBackupStarted()
{
    statusBar()->showMessage(tr("Backup in progress..."));
}

void MainWindow::onBackupCompleted(bool success)
{
    if (success) {
        statusBar()->showMessage(tr("Backup completed successfully"));
    } else {
        statusBar()->showMessage(tr("Backup failed"));
        QMessageBox::critical(this, tr("Backup Error"), tr("Failed to complete backup operation"));
    }
}

void MainWindow::loadSettings()
{
    QSettings settings;
    restoreGeometry(settings.value("mainWindow/geometry").toByteArray());
    restoreState(settings.value("mainWindow/windowState").toByteArray());
}

void MainWindow::saveSettings()
{
    QSettings settings;
    settings.setValue("mainWindow/geometry", saveGeometry());
    settings.setValue("mainWindow/windowState", saveState());
}

void MainWindow::showSettings()
{
    // Show settings dialog
    // Implementation in SettingsDialog class
}

void MainWindow::exportData()
{
    // Show export dialog
    // Implementation in ExportDialog class
}

void MainWindow::importData()
{
    // Show import dialog
    // Implementation in ImportDialog class
}
