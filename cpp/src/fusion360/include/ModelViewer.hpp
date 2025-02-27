#pragma once

#include <QOpenGLWidget>
#include <QOpenGLFunctions>
#include <QString>
#include <QVector3D>
#include <functional>
#include <memory>

namespace Fusion360 {

enum class ViewMode {
    Standard,
    Wireframe,
    XRay,
    Technical
};

enum class RenderingQuality {
    Low,
    Medium,
    High,
    Ultra
};

enum class ShadowQuality {
    None,
    Low,
    Medium,
    High
};

struct ComponentDetails {
    QString name;
    QString type;
    QString material;
    double volume;
    double mass;
    QVector3D dimensions;
};

struct ComponentMetrics {
    double temperature;
    double stress;
    double wear;
    double efficiency;
    double performance;
};

class ModelViewer : public QOpenGLWidget, protected QOpenGLFunctions {
    Q_OBJECT

public:
    explicit ModelViewer(QWidget* parent = nullptr);
    ~ModelViewer() override;

    // Initialization
    void initialize();
    bool loadModel(const QString& path, std::function<void(int)> progressCallback = nullptr);
    void setRenderingQuality(RenderingQuality quality);
    void setShadowQuality(ShadowQuality quality);
    void setAmbientOcclusion(bool enabled);

    // View Control
    void setViewMode(ViewMode mode);
    void setExplodedView(bool enabled, float factor = 1.0f);
    void setCrossSectionView(bool enabled, const QVector3D& plane = QVector3D(1,0,0));
    void resetView();
    void focusOnComponent(const QString& componentId);

    // Component Management
    QStringList getComponentHierarchy() const;
    ComponentDetails getComponentDetails(const QString& componentId) const;
    ComponentMetrics getComponentMetrics(const QString& componentId) const;
    void setComponentColor(const QString& componentId, const QColor& color);
    void setComponentVisibility(const QString& componentId, bool visible);
    void setComponentTransparency(const QString& componentId, float alpha);

    // Animation
    void startAnimation(const QString& name);
    void stopAnimation();
    void setAnimationSpeed(float speed);

signals:
    void modelLoaded();
    void renderingError(const QString& error);
    void componentSelected(const QString& componentId);
    void viewChanged();
    void animationFinished();

protected:
    void initializeGL() override;
    void resizeGL(int w, int h) override;
    void paintGL() override;

    void mousePressEvent(QMouseEvent* event) override;
    void mouseMoveEvent(QMouseEvent* event) override;
    void mouseReleaseEvent(QMouseEvent* event) override;
    void wheelEvent(QWheelEvent* event) override;

private:
    void setupShaders();
    void setupLighting();
    void updateMatrices();
    void renderScene();
    void renderComponent(const QString& componentId);
    void handleSelection(const QPoint& pos);
    void updateComponentTransforms();
    
    QString getComponentAtPosition(const QPoint& pos);
    void calculateBoundingBox();
    void optimizeRendering();
    void updateShadowMaps();

    struct Private;
    std::unique_ptr<Private> d;
};
