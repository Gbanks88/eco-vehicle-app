#pragma once

#include <QObject>
#include <QString>
#include <QVariant>
#include <QFuture>
#include <QMap>
#include <memory>

// Autodesk Platform Services (APS) includes
#include "aps/auth/OAuth.h"
#include "aps/data/DataManagement.h"
#include "aps/model/ModelDerivative.h"
#include "aps/viewer/Viewer.h"
#include "aps/webhook/WebHooks.h"

class AutodeskIntegration : public QObject {
    Q_OBJECT

public:
    static AutodeskIntegration& instance();

    // Authentication
    bool authenticate(const QString& clientId, const QString& clientSecret);
    bool refreshToken();
    bool isAuthenticated() const;
    QString getAccessToken() const;

    // Project management
    struct Project {
        QString id;
        QString name;
        QString description;
        QStringList members;
        QDateTime created;
        QDateTime modified;
    };

    QFuture<QString> createProject(const Project& project);
    QFuture<bool> updateProject(const QString& projectId, const Project& project);
    QFuture<bool> deleteProject(const QString& projectId);
    QFuture<Project> getProject(const QString& projectId);
    QFuture<QList<Project>> listProjects();

    // File management
    struct FileMetadata {
        QString id;
        QString name;
        QString type;
        qint64 size;
        QString version;
        QString status;
        QDateTime created;
        QDateTime modified;
    };

    QFuture<QString> uploadFile(const QString& projectId, const QString& filePath);
    QFuture<bool> downloadFile(const QString& fileId, const QString& destinationPath);
    QFuture<FileMetadata> getFileMetadata(const QString& fileId);
    QFuture<QList<FileMetadata>> listFiles(const QString& projectId);

    // Model derivative
    struct DerivativeJob {
        QString type;
        QStringList formats;
        bool compressed{true};
        QMap<QString, QVariant> settings;
    };

    QFuture<QString> translateModel(const QString& fileId, const DerivativeJob& job);
    QFuture<QVariantMap> getTranslationStatus(const QString& jobId);
    QFuture<QStringList> getAvailableFormats(const QString& fileId);

    // Viewer integration
    struct ViewerConfig {
        QString container;
        QString theme{"light"};
        bool toolbar{true};
        bool propertyPanel{true};
        QMap<QString, QVariant> extensions;
    };

    QString initializeViewer(const ViewerConfig& config);
    bool loadModel(const QString& fileId);
    bool unloadModel();
    bool setViewerState(const QVariantMap& state);
    QVariantMap getViewerState() const;

    // Collaboration
    bool shareProject(const QString& projectId, const QStringList& emails, const QString& role);
    bool revokeAccess(const QString& projectId, const QStringList& emails);
    QStringList getProjectMembers(const QString& projectId) const;

    // Webhooks
    struct WebhookConfig {
        QString event;
        QString callbackUrl;
        QString scope;
        QMap<QString, QVariant> filters;
    };

    QString createWebhook(const WebhookConfig& config);
    bool deleteWebhook(const QString& webhookId);
    QList<WebhookConfig> listWebhooks() const;

signals:
    void authenticated();
    void authenticationFailed(const QString& error);
    void tokenRefreshed();
    void projectCreated(const QString& projectId);
    void projectUpdated(const QString& projectId);
    void projectDeleted(const QString& projectId);
    void fileUploaded(const QString& fileId);
    void fileDownloaded(const QString& fileId);
    void translationStarted(const QString& jobId);
    void translationCompleted(const QString& jobId);
    void translationFailed(const QString& jobId, const QString& error);
    void viewerInitialized();
    void modelLoaded(const QString& fileId);
    void modelUnloaded();
    void viewerStateChanged(const QVariantMap& state);
    void webhookTriggered(const QString& webhookId, const QVariantMap& data);
    void error(const QString& message);

private:
    AutodeskIntegration(QObject* parent = nullptr);
    ~AutodeskIntegration();
    AutodeskIntegration(const AutodeskIntegration&) = delete;
    AutodeskIntegration& operator=(const AutodeskIntegration&) = delete;

    // Internal methods
    bool initializeAPI();
    void setupEventHandlers();
    void handleAPIError(const QString& context);
    QString generateUniqueId() const;

    // APS API objects
    std::unique_ptr<aps::auth::OAuth> oauth_;
    std::unique_ptr<aps::data::DataManagement> dataManagement_;
    std::unique_ptr<aps::model::ModelDerivative> modelDerivative_;
    std::unique_ptr<aps::viewer::Viewer> viewer_;
    std::unique_ptr<aps::webhook::WebHooks> webhooks_;

    // State
    bool authenticated_{false};
    QString accessToken_;
    QMap<QString, Project> projects_;
    QMap<QString, FileMetadata> files_;
    QMap<QString, QString> translationJobs_;
};
