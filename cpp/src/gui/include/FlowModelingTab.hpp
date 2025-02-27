#pragma once

#include <QWidget>
#include <memory>
#include "FlowModelingSystem.hpp"

class FlowModelingTab : public QWidget {
    Q_OBJECT

public:
    explicit FlowModelingTab(QWidget* parent = nullptr);
    ~FlowModelingTab() override;

public slots:
    // Activity Management
    void createActivity();
    void editActivity();
    void deleteActivity();
    void executeActivity();
    
    // Flow Management
    void createObjectFlow();
    void createControlFlow();
    void createEventFlow();
    void deleteFlow();
    
    // Control Node Management
    void addInitialNode();
    void addFinalNode();
    void addForkNode();
    void addJoinNode();
    void addDecisionNode();
    void addMergeNode();
    
    // Parameter Management
    void createParameterSet();
    void editParameters();
    void linkParameters();
    
    // Data Management
    void createDataSource();
    void createBuffer();
    void configureDataFlow();
    
    // Signal Management
    void createSignalHandler();
    void configureSignals();
    void emitSignal();
    
    // Model Management
    void saveModel();
    void loadModel();
    void validateModel();
    void executeModel();
    
    // View Management
    void zoomIn();
    void zoomOut();
    void fitToView();
    void showGrid(bool show);
    void snapToGrid(bool snap);
    
signals:
    void modelModified();
    void executionStarted();
    void executionCompleted();
    void executionError(const QString& error);
    void flowActivated(const QString& flowId);
    void nodeActivated(const QString& nodeId);
    void signalEmitted(const QString& signalName);

private:
    void setupUi();
    void setupToolbar();
    void setupPalette();
    void setupPropertyEditor();
    void setupCanvas();
    void setupConnections();
    
    void updateActivityProperties(const std::shared_ptr<FlowModeling::Activity>& activity);
    void updateFlowProperties(const std::shared_ptr<FlowModeling::ObjectFlow>& flow);
    void updateNodeProperties(const std::shared_ptr<FlowModeling::ControlNode>& node);
    
    struct Private;
    std::unique_ptr<Private> d;
};
