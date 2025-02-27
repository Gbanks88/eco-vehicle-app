#pragma once

#include <QObject>
#include <QString>
#include <QVariant>
#include <QFuture>
#include <QMap>
#include <memory>

// Fusion 360 API includes
#include "adsk/core/Application.h"
#include "adsk/core/UserInterface.h"
#include "adsk/fusion/Design.h"
#include "adsk/fusion/Component.h"
#include "adsk/fusion/BRepBody.h"
#include "adsk/fusion/Sketch.h"

class Fusion360Integration : public QObject {
    Q_OBJECT

public:
    static Fusion360Integration& instance();

    // Connection management
    bool connect();
    void disconnect();
    bool isConnected() const;

    // Document management
    bool openDocument(const QString& path);
    bool saveDocument(const QString& path);
    bool closeDocument(bool save = true);

    // Model operations
    struct ModelConfig {
        QString name;
        QString type;
        QMap<QString, QVariant> parameters;
        bool parametric{true};
        bool history{true};
    };

    QFuture<QString> createModel(const ModelConfig& config);
    QFuture<bool> updateModel(const QString& modelId, const ModelConfig& config);
    QFuture<bool> exportModel(const QString& modelId, const QString& format, const QString& path);

    // Component management
    QStringList getComponents() const;
    bool activateComponent(const QString& componentId);
    QVariantMap getComponentProperties(const QString& componentId) const;
    bool updateComponentProperties(const QString& componentId, const QVariantMap& properties);

    // Parameter management
    QMap<QString, QVariant> getParameters() const;
    bool setParameter(const QString& name, const QVariant& value);
    bool updateParameters(const QMap<QString, QVariant>& parameters);

    // Analysis and simulation
    struct AnalysisConfig {
        QString type;
        QMap<QString, QVariant> settings;
        bool generateReport{true};
    };

    QFuture<QVariantMap> runAnalysis(const QString& modelId, const AnalysisConfig& config);
    QFuture<QString> generateReport(const QString& analysisId);

    // Version control
    QString createVersion(const QString& name, const QString& description);
    bool switchVersion(const QString& versionId);
    QStringList getVersionHistory() const;
    QVariantMap compareVersions(const QString& version1, const QString& version2);

    // Automation
    bool runScript(const QString& scriptPath);
    bool recordMacro(const QString& name);
    bool stopMacro();
    bool playMacro(const QString& name);

    // Event handling
    void registerEventHandler(const QString& eventType, std::function<void(const QVariantMap&)> handler);
    void unregisterEventHandler(const QString& eventType);

signals:
    void connected();
    void disconnected();
    void documentOpened(const QString& path);
    void documentSaved(const QString& path);
    void documentClosed();
    void modelCreated(const QString& modelId);
    void modelUpdated(const QString& modelId);
    void modelExported(const QString& path);
    void componentActivated(const QString& componentId);
    void parametersChanged(const QMap<QString, QVariant>& parameters);
    void analysisStarted(const QString& analysisId);
    void analysisCompleted(const QString& analysisId, const QVariantMap& results);
    void versionCreated(const QString& versionId);
    void versionSwitched(const QString& versionId);
    void scriptExecuted(const QString& scriptPath, bool success);
    void macroRecorded(const QString& name);
    void macroPlayed(const QString& name);
    void error(const QString& message);

private:
    Fusion360Integration(QObject* parent = nullptr);
    ~Fusion360Integration();
    Fusion360Integration(const Fusion360Integration&) = delete;
    Fusion360Integration& operator=(const Fusion360Integration&) = delete;

    // Internal methods
    bool initializeAPI();
    void setupEventHandlers();
    void cleanupAPI();
    QString generateUniqueId() const;
    void handleAPIError(const QString& context);

    // Fusion 360 API objects
    adsk::core::Application* app_{nullptr};
    adsk::core::UserInterface* ui_{nullptr};
    adsk::fusion::Design* activeDesign_{nullptr};

    // State
    bool connected_{false};
    QMap<QString, std::function<void(const QVariantMap&)>> eventHandlers_;
    QMap<QString, QString> modelIdMap_;
    QStringList macros_;
};
