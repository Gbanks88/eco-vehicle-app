#pragma once

#include <QWidget>
#include <QOpenGLWidget>
#include <QOpenGLFunctions>
#include <memory>

namespace Fusion360 {
    class ModelViewer;
    class ComponentTree;
    class MaterialManager;
}

class VehicleVisualizerTab : public QWidget {
    Q_OBJECT

public:
    explicit VehicleVisualizerTab(QWidget* parent = nullptr);
    ~VehicleVisualizerTab() override;

public slots:
    // Model Management
    void loadVehicleModel(const QString& modelPath);
    void updateComponentStatus(const QString& componentId, const QString& status);
    void highlightComponent(const QString& componentId, const QColor& color);
    
    // View Controls
    void setViewMode(ViewMode mode);
    void setExplodedView(bool enabled, float factor = 1.0f);
    void setCrossSectionView(bool enabled, const QVector3D& plane = QVector3D(1,0,0));
    
    // Component Interaction
    void selectComponent(const QString& componentId);
    void showComponentDetails(const QString& componentId);
    void showComponentMetrics(const QString& componentId);
    
    // Animation
    void startAnimation(const QString& animationName);
    void stopAnimation();
    void setAnimationSpeed(float speed);

signals:
    void componentSelected(const QString& componentId);
    void componentStatusChanged(const QString& componentId, const QString& status);
    void viewModeChanged(ViewMode mode);
    void modelLoadingProgress(int percent);
    void modelLoadingComplete();

private:
    void setupUi();
    void setupModelViewer();
    void setupComponentTree();
    void setupControlPanel();
    void setupContextMenu();
    
    // Fusion 360 Integration
    void initializeFusion360();
    void connectFusionAPIs();
    void loadMaterials();
    void setupLighting();
    
    // Component Management
    void updateComponentTree();
    void updateComponentColors();
    void calculateComponentHealth();
    
    // Rendering
    void updateRenderingSettings();
    void optimizePerformance();
    void handleViewportResize();

    struct Private;
    std::unique_ptr<Private> d;
};
