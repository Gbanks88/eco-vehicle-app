#pragma once

#include <QWidget>
#include <QTableView>
#include <memory>

class RequirementsTab : public QWidget {
    Q_OBJECT

public:
    explicit RequirementsTab(QWidget* parent = nullptr);
    ~RequirementsTab() override;

public slots:
    // Requirements Management
    void addRequirement();
    void editRequirement();
    void deleteRequirement();
    void importRequirements(const QString& filePath);
    void exportRequirements(const QString& filePath);
    
    // Traceability
    void linkToComponent(const QString& reqId, const QString& componentId);
    void linkToTestCase(const QString& reqId, const QString& testCaseId);
    void linkToUseCase(const QString& reqId, const QString& useCaseId);
    void showTraceabilityMatrix();
    void generateTraceabilityReport();
    
    // Verification & Validation
    void updateVerificationStatus(const QString& reqId, const QString& status);
    void updateValidationStatus(const QString& reqId, const QString& status);
    void showVVMatrix();
    
    // System V Documents
    void linkToSystemVDoc(const QString& reqId, const QString& docId);
    void showSystemVDiagram();
    void generateSystemVReport();

signals:
    void requirementAdded(const QString& reqId);
    void requirementUpdated(const QString& reqId);
    void requirementDeleted(const QString& reqId);
    void traceabilityUpdated();
    void verificationStatusChanged(const QString& reqId, const QString& status);
    void validationStatusChanged(const QString& reqId, const QString& status);

private:
    void setupUi();
    void setupRequirementsTable();
    void setupTraceabilityView();
    void setupSystemVView();
    void setupToolbar();
    void setupContextMenu();
    
    void loadRequirements();
    void saveRequirements();
    void updateFilters();
    void refreshViews();
    
    struct Private;
    std::unique_ptr<Private> d;
};
