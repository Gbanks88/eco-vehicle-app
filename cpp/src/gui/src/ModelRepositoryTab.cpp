#include "ModelRepositoryTab.hpp"
#include "ui_ModelRepositoryForm.h"
#include <QVBoxLayout>
#include <QToolBar>
#include <QTreeView>
#include <QStandardItemModel>
#include <QMenu>
#include <QAction>
#include <QMessageBox>
#include <QFileDialog>
#include <QDateTime>
#include <Qt3DCore>
#include <Qt3DRender>
#include <Qt3DExtras>
#include <QtDataVisualization>

struct ModelRepositoryTab::Private {
    std::unique_ptr<Ui::ModelRepositoryForm> ui;
    QStandardItemModel* modelTreeModel;
    Qt3DCore::QEntity* rootEntity;
    Qt3DRender::QCamera* camera;
    Qt3DExtras::QOrbitCameraController* cameraController;
    QString currentModelId;
    
    Private() : ui(std::make_unique<Ui::ModelRepositoryForm>()),
                modelTreeModel(new QStandardItemModel) {}
};

ModelRepositoryTab::ModelRepositoryTab(QWidget* parent)
    : QWidget(parent), d(std::make_unique<Private>()) {
    d->ui->setupUi(this);
    setupUi();
    setupModelTree();
    setupPreviewArea();
    setupToolbar();
    setupContextMenu();
    setupSearchFilters();
    
    // Connect signals/slots
    connect(d->ui->searchBox, &QLineEdit::textChanged,
            this, &ModelRepositoryTab::searchModels);
    connect(d->ui->modelTree->selectionModel(), &QItemSelectionModel::selectionChanged,
            this, [this](const QItemSelection& selected) {
                if (!selected.indexes().isEmpty()) {
                    QString modelId = selected.indexes().first().data(Qt::UserRole).toString();
                    updatePreview(modelId);
                    updateMetadata(modelId);
                }
            });
            
    // Connect actions
    connect(d->ui->actionNew, &QAction::triggered, this, &ModelRepositoryTab::createNewModel);
    connect(d->ui->actionOpen, &QAction::triggered, this, &ModelRepositoryTab::importModel);
    connect(d->ui->actionSave, &QAction::triggered, this, &ModelRepositoryTab::exportModel);
    connect(d->ui->actionCheckout, &QAction::triggered, this, &ModelRepositoryTab::checkoutModel);
    connect(d->ui->actionCheckin, &QAction::triggered, this, &ModelRepositoryTab::checkinModel);
    connect(d->ui->actionVersion, &QAction::triggered, this, &ModelRepositoryTab::createVersion);
    connect(d->ui->actionCompare, &QAction::triggered, this, &ModelRepositoryTab::compareVersions);
    
    refreshModelList();
}

ModelRepositoryTab::~ModelRepositoryTab() = default;

bool ModelRepositoryTab::validateModelForm(const QString& name, const QString& type,
                                         const QString& description, const QString& version)
{
    if (!isValidModelName(name)) {
        showError(tr("Validation Error"),
            tr("Invalid model name. Name must be between 3 and 50 characters and contain only letters, numbers, and underscores."));
        return false;
    }
    
    if (!isValidVersion(version)) {
        showError(tr("Validation Error"),
            tr("Invalid version format. Version must follow semantic versioning (e.g., 1.0.0)."));
        return false;
    }
    
    if (description.isEmpty()) {
        showError(tr("Validation Error"),
            tr("Description is required."));
        return false;
    }
    
    return true;
}

bool ModelRepositoryTab::validateModelFile(const QString& filePath)
{
    if (!QFile::exists(filePath)) {
        showError(tr("Validation Error"),
            tr("File does not exist: %1").arg(filePath));
        return false;
    }
    
    if (!isValidFileFormat(filePath)) {
        showError(tr("Validation Error"),
            tr("Unsupported file format. Supported formats: STEP, IGES"));
        return false;
    }
    
    QFileInfo fileInfo(filePath);
    if (!checkDiskSpace(fileInfo.path(), fileInfo.size() * 2)) {
        showError(tr("Validation Error"),
            tr("Insufficient disk space for importing model."));
        return false;
    }
    
    return true;
}

bool ModelRepositoryTab::isValidModelName(const QString& name)
{
    static QRegularExpression nameRegex("^[a-zA-Z][a-zA-Z0-9_]{2,49}$");
    return nameRegex.match(name).hasMatch();
}

bool ModelRepositoryTab::isValidVersion(const QString& version)
{
    static QRegularExpression versionRegex("^\\d+\\.\\d+\\.\\d+$");
    return versionRegex.match(version).hasMatch();
}

bool ModelRepositoryTab::isValidFileFormat(const QString& filePath)
{
    QString extension = QFileInfo(filePath).suffix().toLower();
    return extension == "step" || extension == "stp" ||
           extension == "iges" || extension == "igs";
}

bool ModelRepositoryTab::checkDiskSpace(const QString& path, qint64 requiredSpace)
{
    QStorageInfo storage(path);
    return storage.bytesAvailable() >= requiredSpace;
}

void ModelRepositoryTab::showProgress(const QString& title, const QString& text,
                                    int minimum, int maximum)
{
    if (!d->progressDialog) {
        d->progressDialog = new QProgressDialog(text, tr("Cancel"), minimum, maximum, this);
        d->progressDialog->setWindowModality(Qt::WindowModal);
        d->progressDialog->setWindowTitle(title);
        
        connect(d->progressDialog, &QProgressDialog::canceled, this, [this]() {
            emit errorOccurred(tr("Operation cancelled by user"));
        });
    } else {
        d->progressDialog->setLabelText(text);
        d->progressDialog->setRange(minimum, maximum);
    }
    
    d->progressDialog->show();
}

void ModelRepositoryTab::updateProgress(int value, const QString& message)
{
    if (d->progressDialog) {
        d->progressDialog->setValue(value);
        d->progressDialog->setLabelText(message);
        emit progressUpdated(value, message);
    }
}

void ModelRepositoryTab::hideProgress()
{
    if (d->progressDialog) {
        d->progressDialog->hide();
    }
}

void ModelRepositoryTab::handleError(const QString& operation, const std::exception& e)
{
    QString errorMessage = tr("%1 failed: %2").arg(operation).arg(e.what());
    showError(tr("Error"), errorMessage);
    emit errorOccurred(errorMessage);
    
    // Update accessibility for screen readers
    updateAccessibilityInfo(errorMessage);
}

void ModelRepositoryTab::showError(const QString& title, const QString& message)
{
    QMessageBox::critical(this, title, message);
}

void ModelRepositoryTab::setupAccessibility()
{
    setAccessibleName(tr("Model Repository"));
    setAccessibleDescription(tr("Interface for managing CAD models and their metadata"));
    
    // Set accessibility properties for child widgets
    if (d->ui) {
        d->ui->searchBox->setAccessibleName(tr("Model Search"));
        d->ui->searchBox->setAccessibleDescription(tr("Search for models by name or metadata"));
        
        d->ui->modelTree->setAccessibleName(tr("Model List"));
        d->ui->modelTree->setAccessibleDescription(tr("List of available models in the repository"));
        
        d->ui->toolBar->setAccessibleName(tr("Model Operations"));
        d->ui->toolBar->setAccessibleDescription(tr("Tools for managing models"));
    }
}

void ModelRepositoryTab::updateAccessibilityInfo(const QString& status)
{
    setAccessibleDescription(tr("Model Repository - %1").arg(status));
    QAccessible::updateAccessibility(this);
}

void ModelRepositoryTab::setupUi() {
    d->ui->typeCombo->addItems({"Assembly", "Component", "Drawing", "Simulation", "Analysis", "Manufacturing"});
    d->ui->statusCombo->addItems({"Draft", "InReview", "Approved", "Released", "Obsolete", "Archived"});
}

void ModelRepositoryTab::setupModelTree() {
    d->modelTreeModel->setHorizontalHeaderLabels({"Models"});
    d->ui->modelTree->setModel(d->modelTreeModel);
    d->ui->modelTree->setContextMenuPolicy(Qt::CustomContextMenu);
    
    connect(d->ui->modelTree, &QTreeView::customContextMenuRequested,
            this, [this](const QPoint& pos) {
                QMenu menu;
                menu.addAction(d->ui->actionNew);
                menu.addAction(d->ui->actionOpen);
                menu.addAction(d->ui->actionSave);
                menu.addSeparator();
                menu.addAction(d->ui->actionCheckout);
                menu.addAction(d->ui->actionCheckin);
                menu.addSeparator();
                menu.addAction(d->ui->actionVersion);
                menu.addAction(d->ui->actionCompare);
                menu.exec(d->ui->modelTree->mapToGlobal(pos));
            });
}

void ModelRepositoryTab::setupPreviewArea() {
    auto view = new Qt3DExtras::Qt3DWindow();
    auto container = QWidget::createWindowContainer(view);
    d->ui->previewLayout->addWidget(container);
    
    // Root entity
    d->rootEntity = new Qt3DCore::QEntity();
    
    // Camera
    d->camera = view->camera();
    d->camera->setPosition(QVector3D(0, 0, 20.0f));
    d->camera->setViewCenter(QVector3D(0, 0, 0));
    
    // Camera controller
    d->cameraController = new Qt3DExtras::QOrbitCameraController(d->rootEntity);
    d->cameraController->setCamera(d->camera);
    
    // Lighting
    auto light = new Qt3DCore::QEntity(d->rootEntity);
    auto pointLight = new Qt3DRender::QPointLight(light);
    pointLight->setColor(Qt::white);
    pointLight->setIntensity(1);
    auto lightTransform = new Qt3DCore::QTransform(light);
    lightTransform->setTranslation(QVector3D(20, 20, 20));
    light->addComponent(pointLight);
    light->addComponent(lightTransform);
    
    view->setRootEntity(d->rootEntity);
}

void ModelRepositoryTab::createNewModel() {
    // TODO: Implement model creation dialog
    QMessageBox::information(this, "Create Model", "Model creation dialog will be implemented here");
}

void ModelRepositoryTab::importModel() {
    QString fileName = QFileDialog::getOpenFileName(this,
        "Import Model", QString(),
        "CAD Files (*.step *.stp *.iges *.igs *.stl);;All Files (*)");
        
    if (!fileName.isEmpty()) {
        // TODO: Implement model import
        QMessageBox::information(this, "Import Model", 
            QString("Model import from %1 will be implemented").arg(fileName));
    }
}

void ModelRepositoryTab::exportModel() {
    if (d->currentModelId.isEmpty()) {
        QMessageBox::warning(this, "Export Model", "Please select a model first");
        return;
    }
    
    QString fileName = QFileDialog::getSaveFileName(this,
        "Export Model", QString(),
        "STEP Files (*.step);;IGES Files (*.iges);;STL Files (*.stl)");
        
    if (!fileName.isEmpty()) {
        // TODO: Implement model export
        QMessageBox::information(this, "Export Model",
            QString("Model export to %1 will be implemented").arg(fileName));
    }
}

void ModelRepositoryTab::checkoutModel() {
    if (d->currentModelId.isEmpty()) {
        QMessageBox::warning(this, "Checkout Model", "Please select a model first");
        return;
    }
    
    // TODO: Implement checkout logic
    bool success = true; // Replace with actual checkout implementation
    emit checkoutCompleted(d->currentModelId, success);
    
    if (success) {
        QMessageBox::information(this, "Checkout Model",
            "Model has been checked out successfully");
    }
}

void ModelRepositoryTab::checkinModel() {
    if (d->currentModelId.isEmpty()) {
        QMessageBox::warning(this, "Checkin Model", "Please select a model first");
        return;
    }
    
    // TODO: Implement checkin logic
    bool success = true; // Replace with actual checkin implementation
    emit checkinCompleted(d->currentModelId, success);
    
    if (success) {
        QMessageBox::information(this, "Checkin Model",
            "Model has been checked in successfully");
    }
}

void ModelRepositoryTab::createVersion() {
    if (d->currentModelId.isEmpty()) {
        QMessageBox::warning(this, "Create Version", "Please select a model first");
        return;
    }
    
    // TODO: Implement version creation dialog
    QString version = "1.0.0"; // Replace with actual version from dialog
    emit versionCreated(d->currentModelId, version);
}

void ModelRepositoryTab::compareVersions() {
    if (d->currentModelId.isEmpty()) {
        QMessageBox::warning(this, "Compare Versions", "Please select a model first");
        return;
    }
    
    // TODO: Implement version comparison dialog
    QMessageBox::information(this, "Compare Versions",
        "Version comparison dialog will be implemented here");
}

void ModelRepositoryTab::searchModels(const QString& query) {
    // TODO: Implement model search
    // This is a placeholder implementation
    for (int i = 0; i < d->modelTreeModel->rowCount(); ++i) {
        QStandardItem* item = d->modelTreeModel->item(i);
        bool matches = item->text().contains(query, Qt::CaseInsensitive);
        d->ui->modelTree->setRowHidden(i, QModelIndex(), !matches);
    }
}

void ModelRepositoryTab::refreshModelList() {
    d->modelTreeModel->clear();
    d->modelTreeModel->setHorizontalHeaderLabels({"Models"});
    
    // TODO: Implement actual model list retrieval
    // This is placeholder data
    QStringList demoModels = {
        "Engine Assembly",
        "Transmission",
        "Suspension System",
        "Brake System",
        "Steering Mechanism"
    };
    
    for (const QString& model : demoModels) {
        QStandardItem* item = new QStandardItem(model);
        item->setData(QUuid::createUuid().toString(), Qt::UserRole); // Model ID
        d->modelTreeModel->appendRow(item);
    }
}

void ModelRepositoryTab::updatePreview(const QString& modelId) {
    d->currentModelId = modelId;
    // TODO: Implement 3D model loading and preview
}

void ModelRepositoryTab::updateMetadata(const QString& modelId) {
    // TODO: Implement metadata retrieval and display
    // This is placeholder data
    d->ui->nameEdit->setText("Sample Model");
    d->ui->typeCombo->setCurrentText("Assembly");
    d->ui->statusCombo->setCurrentText("Draft");
    d->ui->versionEdit->setText("1.0.0");
    d->ui->descriptionEdit->setText("Sample model description");
}

void ModelRepositoryTab::checkPermissions() {
    // TODO: Implement permission checking
    bool canEdit = true;
    d->ui->actionCheckout->setEnabled(canEdit);
    d->ui->actionCheckin->setEnabled(canEdit);
    d->ui->actionVersion->setEnabled(canEdit);
}
