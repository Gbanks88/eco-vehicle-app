#pragma once

#include <QWidget>
#include <memory>

class ModelRepositoryTab : public QWidget {
    Q_OBJECT

public:
    explicit ModelRepositoryTab(QWidget* parent = nullptr);
    ~ModelRepositoryTab() override;

public slots:
    // Model Management
    void createNewModel();
    void importModel();
    void exportModel();
    void deleteModel();
    void checkoutModel();
    void checkinModel();
    
    // Version Control
    void createVersion();
    void switchVersion();
    void compareVersions();
    void mergeVersions();
    void showHistory();
    
    // Model Operations
    void editModel();
    void viewModel();
    void simulateModel();
    void validateModel();
    void generateReport();
    
    // Metadata Management
    void editMetadata();
    void addTags();
    void updateProperties();
    void linkRequirements();
    
    // Search and Filter
    void searchModels(const QString& query);
    void filterByType(const QString& type);
    void filterByStatus(const QString& status);
    void filterByDate(const QDate& start, const QDate& end);

signals:
    void modelCreated(const QString& modelId);
    void modelUpdated(const QString& modelId);
    void modelDeleted(const QString& modelId);
    void progressUpdated(int progress, const QString& message);
    void errorOccurred(const QString& error);

protected:
    bool validateModelForm(const QString& name, const QString& type,
                          const QString& description, const QString& version);
    bool validateModelFile(const QString& filePath);
    ModelMetadata extractModelMetadata(const QString& filePath);
    void importModelFile(const QString& filePath, const ModelMetadata& metadata);
    void updateModelDatabase(const ModelMetadata& metadata);
    void cleanupImport(const QString& filePath);
    void cleanupModelFiles(const ModelMetadata& metadata);
    void refreshModelList();
    void createModelFiles(const ModelMetadata& metadata);
    
    // Accessibility helpers
    void setupAccessibility();
    void updateAccessibilityInfo(const QString& status);
    
    // Progress tracking
    void showProgress(const QString& title, const QString& text,
                     int minimum, int maximum);
    void updateProgress(int value, const QString& message);
    void hideProgress();
    
    // Error handling
    void handleError(const QString& operation, const std::exception& e);
    void showError(const QString& title, const QString& message);
    
    // Validation helpers
    bool isValidModelName(const QString& name);
    bool isValidVersion(const QString& version);
    bool isValidFileFormat(const QString& filePath);
    bool checkDiskSpace(const QString& path, qint64 requiredSpace);
    void versionCreated(const QString& modelId, const QString& version);
    void checkoutCompleted(const QString& modelId, bool success);
    void checkinCompleted(const QString& modelId, bool success);

private:
    void setupUi();
    void setupModelTree();
    void setupPreviewArea();
    void setupToolbar();
    void setupContextMenu();
    void setupSearchFilters();
    
    void refreshModelList();
    void updatePreview(const QString& modelId);
    void updateMetadata(const QString& modelId);
    void checkPermissions();
    
    struct Private;
    std::unique_ptr<Private> d;
};
