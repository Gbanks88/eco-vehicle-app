#include "MainWindow.hpp"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QSplitter>
#include <QTabWidget>
#include <QCustomPlot>
#include <QFrame>
#include <QStyleFactory>
#include <QPalette>

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
    , monitor_(std::make_unique<SystemMonitor>())
    , dashboard_(std::make_unique<DashboardWidget>())
    , updateTimer_(new QTimer(this))
{
    setupUi();
    setupMonitoring();
    setupStyles();

    // Configure window
    setWindowTitle(tr("Eco-Vehicle Monitoring System"));
    setMinimumSize(1200, 800);

    // Start updates
    connect(updateTimer_, &QTimer::timeout, this, &MainWindow::updateMetrics);
    updateTimer_->start(UPDATE_INTERVAL_MS);
}

MainWindow::~MainWindow() = default;

void MainWindow::setupUi() {
    // Create central widget
    centralWidget_ = new QWidget(this);
    setCentralWidget(centralWidget_);
    
    // Create main layout with splitter
    auto* mainLayout = new QHBoxLayout(centralWidget_);
    auto* splitter = new QSplitter(Qt::Horizontal, centralWidget_);
    mainLayout->addWidget(splitter);

    // Create left panel (status)
    auto* leftPanel = new QWidget(splitter);
    createStatusPanel();
    splitter->addWidget(leftPanel);

    // Create right panel (visualizations)
    auto* rightPanel = new QWidget(splitter);
    createVisualizationPanel();
    splitter->addWidget(rightPanel);

    // Set splitter proportions
    splitter->setStretchFactor(0, 1);
    splitter->setStretchFactor(1, 3);
}

void MainWindow::setupStyles() {
    // Set fusion style for modern look
    qApp->setStyle(QStyleFactory::create("Fusion"));

    // Configure dark theme
    QPalette darkPalette;
    darkPalette.setColor(QPalette::Window, QColor(53, 53, 53));
    darkPalette.setColor(QPalette::WindowText, Qt::white);
    darkPalette.setColor(QPalette::Base, QColor(25, 25, 25));
    darkPalette.setColor(QPalette::AlternateBase, QColor(53, 53, 53));
    darkPalette.setColor(QPalette::ToolTipBase, Qt::white);
    darkPalette.setColor(QPalette::ToolTipText, Qt::white);
    darkPalette.setColor(QPalette::Text, Qt::white);
    darkPalette.setColor(QPalette::Button, QColor(53, 53, 53));
    darkPalette.setColor(QPalette::ButtonText, Qt::white);
    darkPalette.setColor(QPalette::BrightText, Qt::red);
    darkPalette.setColor(QPalette::Link, QColor(42, 130, 218));
    darkPalette.setColor(QPalette::Highlight, QColor(42, 130, 218));
    darkPalette.setColor(QPalette::HighlightedText, Qt::black);

    qApp->setPalette(darkPalette);
}

void MainWindow::updateMetrics() {
    const auto metrics = monitor_->collectMetrics();
    dashboard_->updateMetrics(metrics);

    // Update plots
    for (const auto& [metric, plot] : metricPlots_) {
        const auto& history = dashboard_->getMetricHistory(metric);
        if (!history.empty()) {
            QVector<double> x(history.size()), y(history.size());
            for (int i = 0; i < history.size(); ++i) {
                x[i] = i;
                y[i] = history[i].second;
            }
            plot->graph(0)->setData(x, y);
            plot->replot();
        }
    }

    updateComponentStatus();
}

void MainWindow::updateComponentStatus() {
    const auto status = monitor_->getComponentStatus();
    for (const auto& [component, healthy] : status) {
        if (auto it = componentLabels_.find(component); it != componentLabels_.end()) {
            auto* label = it->second;
            if (healthy) {
                label->setText(QString("● %1: Operational").arg(component));
                label->setStyleSheet("color: #2ecc71"); // Green
            } else {
                label->setText(QString("● %1: Warning").arg(component));
                label->setStyleSheet("color: #e74c3c"); // Red
            }
        }
    }
}

void MainWindow::handleSystemAlert(const QString& component, const QString& message) {
    // Handle system alerts (implement notification system)
    dashboard_->addAlert(component, message);
}
