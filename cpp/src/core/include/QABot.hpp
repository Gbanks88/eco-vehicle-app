#pragma once

#include <QObject>
#include <QString>
#include <QMap>
#include <QSet>
#include <QDateTime>
#include <functional>
#include <memory>

class QABot : public QObject {
    Q_OBJECT

public:
    static QABot& instance();

    // Register components for monitoring
    void registerComponent(const QString& name, 
                         const QString& type,
                         const QStringList& dependencies = QStringList());

    // Verify component implementation
    bool verifyComponent(const QString& name);

    // Add validation rule
    void addValidationRule(const QString& componentName,
                          const QString& ruleName,
                          std::function<bool()> validationFunc);

    // Check Qt requirements
    bool checkQtRequirements();

    // Monitor build status
    bool monitorBuildStatus();

    // Analyze code quality
    void analyzeCodeQuality(const QString& filePath);

    // Get component status
    QString getComponentStatus(const QString& name) const;

    // Get validation report
    QString generateValidationReport() const;

signals:
    void validationFailed(const QString& component, const QString& reason);
    void validationPassed(const QString& component);
    void buildError(const QString& error);
    void codeQualityIssue(const QString& file, const QString& issue);
    void dependencyMissing(const QString& component, const QString& dependency);

private:
    QABot(QObject* parent = nullptr);
    ~QABot() = default;
    QABot(const QABot&) = delete;
    QABot& operator=(const QABot&) = delete;

    struct ComponentInfo {
        QString type;
        QStringList dependencies;
        QMap<QString, std::function<bool()>> validationRules;
        bool isValid{false};
        QString status;
        QDateTime lastValidated;
    };

    QMap<QString, ComponentInfo> components_;
    QSet<QString> requiredQtModules_;
    
    // Internal validation methods
    bool validateQtIntegration();
    bool validateDatabaseSchema();
    bool validateResourceFiles();
    bool validateTranslations();
    bool validateModelImplementation();
    bool validateUIComponents();
    bool checkCodingStandards(const QString& filePath);
    bool checkMemoryManagement(const QString& filePath);
    bool checkThreadSafety(const QString& filePath);
};
