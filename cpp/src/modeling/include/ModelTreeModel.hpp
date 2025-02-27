#pragma once

#include "ModelMetadata.hpp"
#include <QAbstractItemModel>
#include <QSortFilterProxyModel>
#include <memory>
#include <vector>

class ModelTreeItem {
public:
    explicit ModelTreeItem(const ModelMetadata& data, ModelTreeItem* parent = nullptr);
    ~ModelTreeItem();

    void appendChild(ModelTreeItem* child);
    ModelTreeItem* child(int row);
    int childCount() const;
    int columnCount() const;
    QVariant data(int column) const;
    int row() const;
    ModelTreeItem* parentItem();
    const ModelMetadata& metadata() const { return modelData; }

private:
    std::vector<ModelTreeItem*> childItems;
    ModelMetadata modelData;
    ModelTreeItem* parent;
};

class ModelTreeModel : public QAbstractItemModel {
    Q_OBJECT

public:
    explicit ModelTreeModel(QObject* parent = nullptr);
    ~ModelTreeModel() override;

    // Basic functionality
    QVariant data(const QModelIndex& index, int role) const override;
    Qt::ItemFlags flags(const QModelIndex& index) const override;
    QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const override;
    QModelIndex index(int row, int column, const QModelIndex& parent = QModelIndex()) const override;
    QModelIndex parent(const QModelIndex& index) const override;
    int rowCount(const QModelIndex& parent = QModelIndex()) const override;
    int columnCount(const QModelIndex& parent = QModelIndex()) const override;

    // Model management
    void addModel(const ModelMetadata& model);
    void updateModel(const ModelMetadata& model);
    void removeModel(const QString& modelId);
    void clear();

    // Model queries
    ModelMetadata getModel(const QString& modelId) const;
    QModelIndex findModel(const QString& modelId) const;
    QList<ModelMetadata> getAllModels() const;

    // Filtering and sorting
    void setFilterType(const QString& type);
    void setFilterStatus(const QString& status);
    void setFilterText(const QString& text);
    void setSortColumn(int column);
    void setSortOrder(Qt::SortOrder order);

signals:
    void modelAdded(const QString& modelId);
    void modelUpdated(const QString& modelId);
    void modelRemoved(const QString& modelId);

private:
    ModelTreeItem* getItem(const QModelIndex& index) const;
    void setupModelData();
    void updateFilterAndSort();

    std::unique_ptr<ModelTreeItem> rootItem;
    QString filterType;
    QString filterStatus;
    QString filterText;
    int sortColumn;
    Qt::SortOrder sortOrder;
};
