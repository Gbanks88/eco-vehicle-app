#pragma once

#include <QWidget>
#include <QVariantMap>
#include <memory>

class MLModelTab : public QWidget {
    Q_OBJECT

public:
    explicit MLModelTab(QWidget* parent = nullptr);
    ~MLModelTab() override;

public slots:
    void updatePrediction(const QString& model, const QVariantMap& prediction);
    void trainModel(const QString& model);
    void evaluateModel(const QString& model);
    void exportModel(const QString& model);
    void importModel(const QString& model);

signals:
    void modelTrained(const QString& model, bool success);
    void predictionRequested(const QString& model, const QVariantMap& data);
    void modelConfigChanged(const QString& model, const QVariantMap& config);

private:
    void setupUi();
    void setupModelList();
    void setupPredictionView();
    void setupTrainingControls();
    void updateModelStatus(const QString& model, const QString& status);
    void showModelDetails(const QString& model);

    struct Private;
    std::unique_ptr<Private> d;
};
