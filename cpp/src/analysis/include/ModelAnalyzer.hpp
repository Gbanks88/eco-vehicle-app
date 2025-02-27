#pragma once

#include <QObject>
#include <QString>
#include <QVariant>
#include <QVector>
#include <QFuture>
#include <memory>
#include <torch/torch.h>
#include <opencv2/opencv.hpp>

class ModelAnalyzer : public QObject {
    Q_OBJECT

public:
    static ModelAnalyzer& instance();

    struct AnalysisResult {
        QString modelId;
        QVector<float> embeddings;
        QMap<QString, float> metrics;
        QMap<QString, QString> recommendations;
        QImage visualization;
        float confidence;
    };

    struct AnalysisConfig {
        bool enableDeepLearning{true};
        bool enableOptimization{true};
        bool enableVisualization{true};
        int batchSize{32};
        float confidenceThreshold{0.85f};
    };

    // Analysis methods
    QFuture<AnalysisResult> analyzeModel(const QString& modelId, const AnalysisConfig& config = AnalysisConfig());
    QFuture<QVector<QString>> findSimilarModels(const QString& modelId, int limit = 10);
    QFuture<QMap<QString, float>> predictPerformanceMetrics(const QString& modelId);
    
    // Real-time analysis
    void startRealtimeAnalysis(const QString& modelId);
    void stopRealtimeAnalysis();

    // Model optimization
    QFuture<bool> optimizeModel(const QString& modelId);
    QFuture<QMap<QString, QVariant>> suggestImprovements(const QString& modelId);

    // Visualization
    QImage generateModelVisualization(const QString& modelId);
    QImage generateComparisonVisualization(const QStringList& modelIds);
    QImage generatePerformanceGraph(const QString& modelId);

    // Training and model management
    void trainOnHistoricalData();
    void updateModelWeights(const QString& modelType);
    void saveModelState(const QString& path);
    void loadModelState(const QString& path);

signals:
    void analysisStarted(const QString& modelId);
    void analysisProgress(const QString& modelId, int progress);
    void analysisCompleted(const QString& modelId, const AnalysisResult& result);
    void analysisError(const QString& modelId, const QString& error);
    void realtimeUpdate(const QString& modelId, const QMap<QString, QVariant>& metrics);
    void modelOptimized(const QString& modelId, bool success);
    void improvementsSuggested(const QString& modelId, const QMap<QString, QVariant>& suggestions);
    void trainingProgress(int epoch, float loss);
    void trainingCompleted(float finalLoss);

private:
    ModelAnalyzer(QObject* parent = nullptr);
    ~ModelAnalyzer() = default;
    ModelAnalyzer(const ModelAnalyzer&) = delete;
    ModelAnalyzer& operator=(const ModelAnalyzer&) = delete;

    // Neural network models
    struct Models {
        torch::jit::Module featureExtractor;
        torch::jit::Module performancePredictor;
        torch::jit::Module optimizationModel;
    } models_;

    // Internal processing methods
    torch::Tensor preprocessModel(const QString& modelId);
    QVector<float> extractFeatures(const torch::Tensor& input);
    QMap<QString, float> computeMetrics(const torch::Tensor& features);
    QMap<QString, QString> generateRecommendations(const QMap<QString, float>& metrics);
    QImage visualizeFeatures(const torch::Tensor& features);

    // Optimization methods
    torch::Tensor optimizeModelGeometry(const torch::Tensor& modelData);
    torch::Tensor optimizeModelTopology(const torch::Tensor& modelData);
    
    // Training methods
    void prepareTrainingData();
    void trainEpoch(torch::DataLoader<torch::data::datasets::MapDataset>& dataLoader);
    
    // State
    QString currentModelId_;
    bool isAnalyzing_{false};
    AnalysisConfig currentConfig_;
    QMap<QString, torch::Tensor> modelCache_;
};
