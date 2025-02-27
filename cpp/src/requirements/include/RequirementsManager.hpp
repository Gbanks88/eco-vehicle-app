#pragma once

#include <QString>
#include <QVariantMap>
#include <QVector>
#include <memory>

class RequirementsManager {
public:
    // Requirement Types
    enum class RequirementType {
        Functional,
        Performance,
        Interface,
        Security,
        Safety,
        Environmental,
        Regulatory,
        UserInterface
    };

    // Requirement Status
    enum class Status {
        Draft,
        Review,
        Approved,
        Implemented,
        Verified,
        Validated,
        Rejected,
        Obsolete
    };

    // Requirement Priority
    enum class Priority {
        Critical,
        High,
        Medium,
        Low
    };

    // Requirement Structure
    struct Requirement {
        QString id;
        QString title;
        QString description;
        RequirementType type;
        Priority priority;
        Status status;
        QString rationale;
        QString source;
        QString version;
        QDateTime createdDate;
        QDateTime modifiedDate;
        QString createdBy;
        QString modifiedBy;
        QVector<QString> dependencies;
        QVector<QString> linkedComponents;
        QVector<QString> linkedTestCases;
        QVector<QString> linkedUseCases;
        QVector<QString> linkedSystemVDocs;
        QVariantMap verificationStatus;
        QVariantMap validationStatus;
        QVariantMap customFields;
    };

    // Traceability Matrix
    struct TraceabilityMatrix {
        QVector<QString> requirements;
        QVector<QString> components;
        QVector<QString> testCases;
        QVector<QString> useCases;
        QVector<QString> systemVDocs;
        QVector<QVector<bool>> relationships;
    };

    // System V Document
    struct SystemVDocument {
        QString id;
        QString title;
        QString type;
        QString content;
        QString phase;
        QVector<QString> linkedRequirements;
        QDateTime createdDate;
        QDateTime modifiedDate;
    };

public:
    RequirementsManager();
    ~RequirementsManager();

    // Requirements CRUD
    QString addRequirement(const Requirement& req);
    bool updateRequirement(const QString& reqId, const Requirement& req);
    bool deleteRequirement(const QString& reqId);
    Requirement getRequirement(const QString& reqId) const;
    QVector<Requirement> getAllRequirements() const;
    QVector<Requirement> filterRequirements(const QVariantMap& filters) const;

    // Traceability Management
    bool linkRequirementToComponent(const QString& reqId, const QString& componentId);
    bool linkRequirementToTestCase(const QString& reqId, const QString& testCaseId);
    bool linkRequirementToUseCase(const QString& reqId, const QString& useCaseId);
    bool linkRequirementToSystemVDoc(const QString& reqId, const QString& docId);
    TraceabilityMatrix generateTraceabilityMatrix() const;
    QVector<QString> getLinkedItems(const QString& reqId, const QString& itemType) const;

    // Verification & Validation
    bool updateVerificationStatus(const QString& reqId, const QVariantMap& status);
    bool updateValidationStatus(const QString& reqId, const QVariantMap& status);
    QVariantMap getVerificationStatus(const QString& reqId) const;
    QVariantMap getValidationStatus(const QString& reqId) const;

    // System V Documentation
    QString addSystemVDoc(const SystemVDocument& doc);
    bool updateSystemVDoc(const QString& docId, const SystemVDocument& doc);
    bool deleteSystemVDoc(const QString& docId);
    SystemVDocument getSystemVDoc(const QString& docId) const;
    QVector<SystemVDocument> getAllSystemVDocs() const;

    // Import/Export
    bool importRequirements(const QString& filePath, const QString& format);
    bool exportRequirements(const QString& filePath, const QString& format);
    bool generateTraceabilityReport(const QString& filePath, const QString& format);
    bool generateSystemVReport(const QString& filePath, const QString& format);

    // Validation
    bool validateRequirement(const Requirement& req) const;
    QVector<QString> validateDependencies(const QString& reqId) const;
    bool checkCircularDependencies(const QString& reqId) const;

private:
    struct Private;
    std::unique_ptr<Private> d;
};
