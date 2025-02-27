#pragma once

#include <QObject>
#include <QString>
#include <QVector3D>
#include <QMatrix4x4>
#include <QColor>
#include <memory>
#include <Qt3DCore>
#include <Qt3DRender>
#include <Qt3DExtras>

class VisualizationEngine : public QObject {
    Q_OBJECT

public:
    static VisualizationEngine& instance();

    // Visualization types
    enum class VisType {
        Model3D,
        FlowDiagram,
        Graph,
        Heatmap,
        Timeline,
        Dashboard
    };

    // Visualization configuration
    struct VisConfig {
        VisType type;
        QString title;
        QMap<QString, QVariant> parameters;
        bool interactive{true};
        bool animated{true};
        float quality{1.0f};
    };

    // Scene management
    void createScene(const QString& sceneId, const VisConfig& config);
    void updateScene(const QString& sceneId, const QMap<QString, QVariant>& data);
    void removeScene(const QString& sceneId);
    
    // Camera control
    void setCamera(const QString& sceneId, const QVector3D& position, const QVector3D& target);
    void animateCamera(const QString& sceneId, const QVector3D& endPosition, const QVector3D& endTarget, float duration);
    
    // Lighting
    void setLighting(const QString& sceneId, const QVector<Qt3DCore::QEntity*>& lights);
    void setAmbientLight(const QString& sceneId, const QColor& color, float intensity);
    
    // Material management
    Qt3DRender::QMaterial* createMaterial(const QString& name);
    void updateMaterial(Qt3DRender::QMaterial* material, const QMap<QString, QVariant>& properties);
    
    // Animation
    void addAnimation(const QString& sceneId, const QString& targetId, const QMap<QString, QVariant>& keyframes);
    void playAnimation(const QString& sceneId, const QString& animationId);
    void stopAnimation(const QString& sceneId, const QString& animationId);
    
    // Interaction
    void enableInteraction(const QString& sceneId, bool enable);
    void setInteractionMode(const QString& sceneId, const QString& mode);
    void registerInteractionCallback(const QString& sceneId, std::function<void(const QString&, const QVariant&)> callback);
    
    // Effects
    void addPostProcessingEffect(const QString& sceneId, const QString& effectType);
    void setEffectParameter(const QString& sceneId, const QString& effectId, const QString& param, const QVariant& value);
    
    // Export
    void exportScene(const QString& sceneId, const QString& filePath, const QString& format);
    QImage captureScene(const QString& sceneId, const QSize& size);
    
    // Performance
    void setQualityLevel(const QString& sceneId, float level);
    void enableGPUAcceleration(bool enable);
    QMap<QString, QVariant> getPerformanceMetrics(const QString& sceneId);

signals:
    void sceneCreated(const QString& sceneId);
    void sceneUpdated(const QString& sceneId);
    void sceneRemoved(const QString& sceneId);
    void cameraChanged(const QString& sceneId, const QVector3D& position, const QVector3D& target);
    void animationStarted(const QString& sceneId, const QString& animationId);
    void animationFinished(const QString& sceneId, const QString& animationId);
    void interactionOccurred(const QString& sceneId, const QString& type, const QVariant& data);
    void renderingError(const QString& sceneId, const QString& error);
    void performanceWarning(const QString& sceneId, const QString& warning);

private:
    VisualizationEngine(QObject* parent = nullptr);
    ~VisualizationEngine() = default;
    VisualizationEngine(const VisualizationEngine&) = delete;
    VisualizationEngine& operator=(const VisualizationEngine&) = delete;

    struct Scene {
        Qt3DCore::QEntity* root;
        Qt3DRender::QCamera* camera;
        QVector<Qt3DCore::QEntity*> lights;
        QMap<QString, Qt3DCore::QEntity*> objects;
        QMap<QString, Qt3DCore::QEntity*> animations;
        VisConfig config;
    };

    // Internal methods
    Scene* getScene(const QString& sceneId);
    void setupDefaultLighting(Scene* scene);
    void setupPostProcessing(Scene* scene);
    void optimizeScene(Scene* scene);
    void updateSceneGraph(Scene* scene);
    
    // State
    QMap<QString, std::unique_ptr<Scene>> scenes_;
    Qt3DCore::QAspectEngine* aspectEngine_;
    Qt3DRender::QRenderSettings* renderSettings_;
    bool gpuAcceleration_{true};
};
