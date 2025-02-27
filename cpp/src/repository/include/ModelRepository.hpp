#pragma once

#include <QString>
#include <QDateTime>
#include <QVector>
#include <QVariantMap>
#include <memory>

namespace Fusion360 {
    class Document;
}

class ModelRepository {
public:
    // Model Types
    enum class ModelType {
        Assembly,
        Component,
        Drawing,
        Simulation,
        Analysis,
        Manufacturing
    };

    // Model Status
    enum class Status {
        Draft,
        InReview,
        Approved,
        Released,
        Obsolete,
        Archived
    };

    // Model Structure
    struct Model {
        QString id;
        QString name;
        QString description;
        ModelType type;
        Status status;
        QString version;
        QString author;
        QDateTime createdDate;
        QDateTime modifiedDate;
        QString checkedOutBy;
        QVector<QString> tags;
        QVariantMap properties;
        QVector<QString> linkedRequirements;
        QVector<QString> dependencies;
        QString fusionDocumentId;
        QString previewImage;
        bool isLocked;
    };

    // Version Info
    struct VersionInfo {
        QString version;
        QString description;
        QString author;
        QDateTime date;
        QString changeLog;
        QString parentVersion;
        bool isMajor;
    };

    // Checkout Info
    struct CheckoutInfo {
        QString modelId;
        QString userId;
        QDateTime checkoutTime;
        QString workingCopy;
        bool isExclusive;
    };

public:
    ModelRepository();
    ~ModelRepository();

    // Model Management
    QString createModel(const Model& model, const Fusion360::Document& fusionDoc);
    bool updateModel(const QString& modelId, const Model& model);
    bool deleteModel(const QString& modelId);
    Model getModel(const QString& modelId) const;
    QVector<Model> getAllModels() const;
    QVector<Model> searchModels(const QString& query) const;
    QVector<Model> filterModels(const QVariantMap& filters) const;

    // Version Control
    QString createVersion(const QString& modelId, const VersionInfo& versionInfo);
    bool switchVersion(const QString& modelId, const QString& version);
    QVector<VersionInfo> getVersionHistory(const QString& modelId) const;
    bool compareVersions(const QString& modelId, const QString& version1, const QString& version2);
    bool mergeVersions(const QString& modelId, const QString& sourceVersion, const QString& targetVersion);

    // Checkout Management
    bool checkoutModel(const QString& modelId, const QString& userId, bool exclusive = false);
    bool checkinModel(const QString& modelId, const QString& userId, const QString& comment);
    bool discardCheckout(const QString& modelId, const QString& userId);
    CheckoutInfo getCheckoutInfo(const QString& modelId) const;
    bool isCheckedOut(const QString& modelId) const;

    // File Operations
    bool exportModel(const QString& modelId, const QString& format, const QString& path);
    QString importModel(const QString& path, const QVariantMap& metadata);
    bool validateModel(const QString& modelId);
    QString generateReport(const QString& modelId, const QString& format);

    // Metadata Management
    bool updateMetadata(const QString& modelId, const QVariantMap& metadata);
    bool addTags(const QString& modelId, const QStringList& tags);
    bool removeTags(const QString& modelId, const QStringList& tags);
    bool updateProperties(const QString& modelId, const QVariantMap& properties);
    bool linkRequirement(const QString& modelId, const QString& requirementId);
    bool unlinkRequirement(const QString& modelId, const QString& requirementId);

    // Preview Management
    bool generatePreview(const QString& modelId);
    QString getPreviewPath(const QString& modelId) const;
    bool updatePreview(const QString& modelId, const QString& previewPath);

    // Dependency Management
    QVector<QString> getDependencies(const QString& modelId) const;
    bool addDependency(const QString& modelId, const QString& dependencyId);
    bool removeDependency(const QString& modelId, const QString& dependencyId);
    bool validateDependencies(const QString& modelId);

    // Storage Management
    qint64 getStorageUsage(const QString& modelId) const;
    bool cleanup(const QString& modelId);
    bool archive(const QString& modelId);
    bool restore(const QString& modelId);

private:
    struct Private;
    std::unique_ptr<Private> d;
};
