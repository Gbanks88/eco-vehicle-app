#include <QApplication>
#include <QCommandLineParser>
#include <QDebug>
#include <QLoggingCategory>
#include <QSplashScreen>
#include <QThread>

#include "ui/MainWindow.hpp"
#include "core/Config.hpp"
#include "core/Logger.hpp"

int main(int argc, char *argv[]) {
    // Set application metadata
    QApplication::setApplicationName("EcoVehicle Monitor");
    QApplication::setApplicationVersion("1.0.0");
    QApplication::setOrganizationName("EcoVehicle");
    QApplication::setOrganizationDomain("ecovehicle.com");
    
    // Create application
    QApplication app(argc, argv);
    
    // Parse command line arguments
    QCommandLineParser parser;
    parser.setApplicationDescription("EcoVehicle Monitoring System");
    parser.addHelpOption();
    parser.addVersionOption();
    
    // Add custom options
    QCommandLineOption configOption(QStringList() << "c" << "config",
        "Load configuration file.", "config", "config/default.json");
    parser.addOption(configOption);
    
    parser.process(app);
    
    // Initialize logging
    Logger::init();
    
    // Load configuration
    QString configFile = parser.value(configOption);
    if (!Config::instance().load(configFile)) {
        qCritical() << "Failed to load configuration file:" << configFile;
        return 1;
    }
    
    // Show splash screen
    QPixmap pixmap(":/images/splash.png");
    QSplashScreen splash(pixmap);
    splash.show();
    app.processEvents();
    
    // Create and show main window
    MainWindow mainWindow;
    mainWindow.show();
    
    // Close splash screen
    splash.finish(&mainWindow);
    
    return app.exec();
}
