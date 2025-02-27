#include "VehicleVisualizerTab.hpp"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QSplitter>
#include <QTreeView>
#include <QToolBar>
#include <QComboBox>
#include <QPushButton>
#include <QLabel>
#include <QProgressDialog>
#include <QMessageBox>

// Fusion 360 API includes
#include "fusion360/ModelViewer.hpp"
#include "fusion360/ComponentTree.hpp"
#include "fusion360/MaterialManager.hpp"

struct VehicleVisualizerTab::Private {
    // Fusion 360 Components
    std::unique_ptr<Fusion360::ModelViewer> modelViewer;
    std::unique_ptr<Fusion360::ComponentTree> componentTree;
    std::unique_ptr<Fusion360::MaterialManager> materialManager;
    
    // UI Components
    QTreeView* componentTreeView{nullptr};
    QToolBar* viewToolBar{nullptr};
    QComboBox* viewModeCombo{nullptr};
    QPushButton* explodedViewBtn{nullptr};
    QPushButton* crossSectionBtn{nullptr};
    QLabel* statusLabel{nullptr};
    
    // State
    QString currentModelPath;
    bool isExplodedView{false};
    bool isCrossSectionView{false};
    float explodeFactor{1.0f};
    QVector3D sectionPlane{1,0,0};
    
    // Component Status Cache
    QMap<QString, QString> componentStatus;
    QMap<QString, QColor> componentColors;
};

VehicleVisualizerTab::VehicleVisualizerTab(QWidget* parent)
    : QWidget(parent)
    , d(std::make_unique<Private>())
{
    setupUi();
    initializeFusion360();
    connectFusionAPIs();
    loadMaterials();
    setupLighting();
}

VehicleVisualizerTab::~VehicleVisualizerTab() = default;

void VehicleVisualizerTab::setupUi()
{
    auto* mainLayout = new QHBoxLayout(this);
    auto* splitter = new QSplitter(Qt::Horizontal, this);
    mainLayout->addWidget(splitter);

    // Left side - Component Tree
    auto* leftWidget = new QWidget(splitter);
    auto* leftLayout = new QVBoxLayout(leftWidget);
    
    d->componentTreeView = new QTreeView(leftWidget);
    leftLayout->addWidget(new QLabel(tr("Components")));
    leftLayout->addWidget(d->componentTreeView);

    // Right side - 3D Viewer and Controls
    auto* rightWidget = new QWidget(splitter);
    auto* rightLayout = new QVBoxLayout(rightWidget);

    // Toolbar
    d->viewToolBar = new QToolBar(rightWidget);
    d->viewModeCombo = new QComboBox(d->viewToolBar);
    d->viewModeCombo->addItems({tr("3D View"), tr("Wireframe"), tr("X-Ray"), tr("Technical")});
    
    d->explodedViewBtn = new QPushButton(tr("Exploded View"), d->viewToolBar);
    d->explodedViewBtn->setCheckable(true);
    
    d->crossSectionBtn = new QPushButton(tr("Cross Section"), d->viewToolBar);
    d->crossSectionBtn->setCheckable(true);
    
    d->viewToolBar->addWidget(new QLabel(tr("View Mode: ")));
    d->viewToolBar->addWidget(d->viewModeCombo);
    d->viewToolBar->addSeparator();
    d->viewToolBar->addWidget(d->explodedViewBtn);
    d->viewToolBar->addWidget(d->crossSectionBtn);
    
    rightLayout->addWidget(d->viewToolBar);

    // Create the Fusion 360 model viewer
    d->modelViewer = std::make_unique<Fusion360::ModelViewer>(rightWidget);
    rightLayout->addWidget(d->modelViewer.get());

    // Status bar
    d->statusLabel = new QLabel(rightWidget);
    rightLayout->addWidget(d->statusLabel);

    // Set initial splitter sizes
    splitter->setSizes({200, 800});

    setupControlPanel();
    setupContextMenu();
}

void VehicleVisualizerTab::initializeFusion360()
{
    try {
        // Initialize Fusion 360 API
        d->modelViewer->initialize();
        d->componentTree = std::make_unique<Fusion360::ComponentTree>();
        d->materialManager = std::make_unique<Fusion360::MaterialManager>();
        
        // Set up default rendering settings
        d->modelViewer->setRenderingQuality(RenderingQuality::High);
        d->modelViewer->setAmbientOcclusion(true);
        d->modelViewer->setShadowQuality(ShadowQuality::High);
        
    } catch (const std::exception& e) {
        QMessageBox::critical(this, tr("Initialization Error"),
            tr("Failed to initialize Fusion 360 API: %1").arg(e.what()));
    }
}

void VehicleVisualizerTab::loadVehicleModel(const QString& modelPath)
{
    QProgressDialog progress(tr("Loading vehicle model..."), tr("Cancel"), 0, 100, this);
    progress.setWindowModality(Qt::WindowModal);

    try {
        // Load the Fusion 360 model
        d->modelViewer->loadModel(modelPath,
            [&progress](int percent) {
                progress.setValue(percent);
                QApplication::processEvents();
            }
        );

        // Update component tree
        auto components = d->modelViewer->getComponentHierarchy();
        d->componentTree->setComponents(components);
        d->componentTreeView->setModel(d->componentTree.get());

        // Store current model path
        d->currentModelPath = modelPath;
        
        // Update status
        d->statusLabel->setText(tr("Model loaded successfully"));
        
        emit modelLoadingComplete();
        
    } catch (const std::exception& e) {
        QMessageBox::critical(this, tr("Loading Error"),
            tr("Failed to load model: %1").arg(e.what()));
    }
}

void VehicleVisualizerTab::updateComponentStatus(const QString& componentId, const QString& status)
{
    d->componentStatus[componentId] = status;
    
    // Update component color based on status
    QColor color;
    if (status == "normal") {
        color = Qt::green;
    } else if (status == "warning") {
        color = Qt::yellow;
    } else if (status == "critical") {
        color = Qt::red;
    }
    
    highlightComponent(componentId, color);
    d->componentTree->updateComponentStatus(componentId, status);
}

void VehicleVisualizerTab::highlightComponent(const QString& componentId, const QColor& color)
{
    d->componentColors[componentId] = color;
    d->modelViewer->setComponentColor(componentId, color);
}

void VehicleVisualizerTab::setViewMode(ViewMode mode)
{
    d->modelViewer->setViewMode(mode);
    emit viewModeChanged(mode);
}

void VehicleVisualizerTab::setExplodedView(bool enabled, float factor)
{
    d->isExplodedView = enabled;
    d->explodeFactor = factor;
    d->modelViewer->setExplodedView(enabled, factor);
    d->explodedViewBtn->setChecked(enabled);
}

void VehicleVisualizerTab::setCrossSectionView(bool enabled, const QVector3D& plane)
{
    d->isCrossSectionView = enabled;
    d->sectionPlane = plane;
    d->modelViewer->setCrossSectionView(enabled, plane);
    d->crossSectionBtn->setChecked(enabled);
}

void VehicleVisualizerTab::showComponentDetails(const QString& componentId)
{
    auto details = d->modelViewer->getComponentDetails(componentId);
    
    // Create and show details dialog
    QDialog dialog(this);
    dialog.setWindowTitle(tr("Component Details"));
    
    auto* layout = new QVBoxLayout(&dialog);
    
    // Add component information
    layout->addWidget(new QLabel(tr("ID: %1").arg(componentId)));
    layout->addWidget(new QLabel(tr("Name: %1").arg(details.name)));
    layout->addWidget(new QLabel(tr("Type: %1").arg(details.type)));
    layout->addWidget(new QLabel(tr("Material: %1").arg(details.material)));
    layout->addWidget(new QLabel(tr("Status: %1").arg(d->componentStatus.value(componentId))));
    
    // Add metrics if available
    if (auto metrics = d->modelViewer->getComponentMetrics(componentId)) {
        layout->addWidget(new QLabel(tr("Temperature: %1°C").arg(metrics.temperature)));
        layout->addWidget(new QLabel(tr("Stress: %1 MPa").arg(metrics.stress)));
        layout->addWidget(new QLabel(tr("Wear: %1%").arg(metrics.wear)));
    }
    
    dialog.exec();
}

void VehicleVisualizerTab::setupControlPanel()
{
    // Connect signals
    connect(d->viewModeCombo, QOverload<int>::of(&QComboBox::currentIndexChanged),
            [this](int index) {
                setViewMode(static_cast<ViewMode>(index));
            });
            
    connect(d->explodedViewBtn, &QPushButton::toggled,
            [this](bool checked) {
                setExplodedView(checked);
            });
            
    connect(d->crossSectionBtn, &QPushButton::toggled,
            [this](bool checked) {
                setCrossSectionView(checked);
            });
            
    connect(d->componentTreeView, &QTreeView::clicked,
            [this](const QModelIndex& index) {
                auto componentId = d->componentTree->getComponentId(index);
                selectComponent(componentId);
            });
}

void VehicleVisualizerTab::setupContextMenu()
{
    d->componentTreeView->setContextMenuPolicy(Qt::CustomContextMenu);
    
    connect(d->componentTreeView, &QTreeView::customContextMenuRequested,
            [this](const QPoint& pos) {
                auto index = d->componentTreeView->indexAt(pos);
                if (!index.isValid()) return;
                
                auto componentId = d->componentTree->getComponentId(index);
                
                QMenu menu(this);
                menu.addAction(tr("Show Details"), [this, componentId]() {
                    showComponentDetails(componentId);
                });
                menu.addAction(tr("Show Metrics"), [this, componentId]() {
                    showComponentMetrics(componentId);
                });
                menu.addAction(tr("Focus View"), [this, componentId]() {
                    d->modelViewer->focusOnComponent(componentId);
                });
                
                menu.exec(d->componentTreeView->viewport()->mapToGlobal(pos));
            });
}
