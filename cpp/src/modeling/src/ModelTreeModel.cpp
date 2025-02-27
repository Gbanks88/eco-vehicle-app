#include "ModelTreeModel.hpp"
#include <QApplication>
#include <QStyle>
#include <QDateTime>
#include <QMimeData>
#include <QIcon>

ModelTreeItem::ModelTreeItem(const ModelMetadata& data, ModelTreeItem* parentItem)
    : modelData(data)
    , parent(parentItem)
{
}

ModelTreeItem::~ModelTreeItem()
{
    qDeleteAll(childItems);
}

void ModelTreeItem::appendChild(ModelTreeItem* child)
{
    childItems.push_back(child);
}

ModelTreeItem* ModelTreeItem::child(int row)
{
    if (row < 0 || row >= static_cast<int>(childItems.size()))
        return nullptr;
    return childItems[row];
}

int ModelTreeItem::childCount() const
{
    return static_cast<int>(childItems.size());
}

int ModelTreeItem::columnCount() const
{
    return 7; // Name, Type, Status, Version, Author, Created, Modified
}

QVariant ModelTreeItem::data(int column) const
{
    switch (column) {
        case 0: return modelData.name;
        case 1: return modelData.type;
        case 2: return modelData.status;
        case 3: return modelData.version;
        case 4: return modelData.author;
        case 5: return modelData.created.toString("yyyy-MM-dd hh:mm:ss");
        case 6: return modelData.modified.toString("yyyy-MM-dd hh:mm:ss");
        default: return QVariant();
    }
}

ModelTreeItem* ModelTreeItem::parentItem()
{
    return parent;
}

int ModelTreeItem::row() const
{
    if (parent) {
        auto it = std::find(parent->childItems.begin(), parent->childItems.end(), this);
        if (it != parent->childItems.end()) {
            return static_cast<int>(std::distance(parent->childItems.begin(), it));
        }
    }
    return 0;
}

ModelTreeModel::ModelTreeModel(QObject* parent)
    : QAbstractItemModel(parent)
    , rootItem(std::make_unique<ModelTreeItem>(ModelMetadata()))
    , sortColumn(0)
    , sortOrder(Qt::AscendingOrder)
{
    setupModelData();
}

ModelTreeModel::~ModelTreeModel() = default;

QVariant ModelTreeModel::data(const QModelIndex& index, int role) const
{
    if (!index.isValid())
        return QVariant();

    ModelTreeItem* item = getItem(index);
    if (!item)
        return QVariant();

    switch (role) {
        case Qt::DisplayRole:
            return item->data(index.column());
            
        case Qt::DecorationRole:
            if (index.column() == 0) {
                // Return appropriate icon based on model type
                QString iconName;
                if (item->metadata().type == "Assembly")
                    iconName = ":/icons/assembly.png";
                else if (item->metadata().type == "Component")
                    iconName = ":/icons/component.png";
                else if (item->metadata().type == "Drawing")
                    iconName = ":/icons/drawing.png";
                return QIcon(iconName);
            }
            return QVariant();
            
        case Qt::ToolTipRole:
            return tr("%1\nType: %2\nStatus: %3\nVersion: %4")
                .arg(item->metadata().name)
                .arg(item->metadata().type)
                .arg(item->metadata().status)
                .arg(item->metadata().version);
            
        default:
            return QVariant();
    }
}

Qt::ItemFlags ModelTreeModel::flags(const QModelIndex& index) const
{
    if (!index.isValid())
        return Qt::NoItemFlags;

    return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsDragEnabled;
}

QVariant ModelTreeModel::headerData(int section, Qt::Orientation orientation, int role) const
{
    if (orientation == Qt::Horizontal && role == Qt::DisplayRole) {
        switch (section) {
            case 0: return tr("Name");
            case 1: return tr("Type");
            case 2: return tr("Status");
            case 3: return tr("Version");
            case 4: return tr("Author");
            case 5: return tr("Created");
            case 6: return tr("Modified");
            default: return QVariant();
        }
    }
    return QVariant();
}

QModelIndex ModelTreeModel::index(int row, int column, const QModelIndex& parent) const
{
    if (!hasIndex(row, column, parent))
        return QModelIndex();

    ModelTreeItem* parentItem = getItem(parent);
    if (!parentItem)
        return QModelIndex();

    ModelTreeItem* childItem = parentItem->child(row);
    if (childItem)
        return createIndex(row, column, childItem);
    return QModelIndex();
}

QModelIndex ModelTreeModel::parent(const QModelIndex& index) const
{
    if (!index.isValid())
        return QModelIndex();

    ModelTreeItem* childItem = getItem(index);
    if (!childItem)
        return QModelIndex();

    ModelTreeItem* parentItem = childItem->parentItem();
    if (parentItem == rootItem.get())
        return QModelIndex();

    return createIndex(parentItem->row(), 0, parentItem);
}

int ModelTreeModel::rowCount(const QModelIndex& parent) const
{
    ModelTreeItem* parentItem = getItem(parent);
    return parentItem ? parentItem->childCount() : 0;
}

int ModelTreeModel::columnCount(const QModelIndex& parent) const
{
    Q_UNUSED(parent)
    return 7;
}

void ModelTreeModel::addModel(const ModelMetadata& model)
{
    beginInsertRows(QModelIndex(), rootItem->childCount(), rootItem->childCount());
    rootItem->appendChild(new ModelTreeItem(model, rootItem.get()));
    endInsertRows();
    
    emit modelAdded(model.id);
}

void ModelTreeModel::updateModel(const ModelMetadata& model)
{
    QModelIndex modelIndex = findModel(model.id);
    if (!modelIndex.isValid())
        return;
        
    ModelTreeItem* item = getItem(modelIndex);
    if (!item)
        return;
        
    // Update the item's data
    item->modelData = model;
    
    // Notify views of the change
    emit dataChanged(modelIndex, modelIndex.siblingAtColumn(columnCount() - 1));
    emit modelUpdated(model.id);
}

void ModelTreeModel::removeModel(const QString& modelId)
{
    QModelIndex modelIndex = findModel(modelId);
    if (!modelIndex.isValid())
        return;
        
    ModelTreeItem* item = getItem(modelIndex);
    if (!item || item->parentItem() != rootItem.get())
        return;
        
    // Remove the item
    beginRemoveRows(QModelIndex(), modelIndex.row(), modelIndex.row());
    rootItem->childItems.erase(
        rootItem->childItems.begin() + modelIndex.row()
    );
    endRemoveRows();
    
    emit modelRemoved(modelId);
}

void ModelTreeModel::clear()
{
    beginResetModel();
    rootItem = std::make_unique<ModelTreeItem>(ModelMetadata());
    endResetModel();
}

ModelMetadata ModelTreeModel::getModel(const QString& modelId) const
{
    QModelIndex index = findModel(modelId);
    if (!index.isValid())
        return ModelMetadata();
        
    ModelTreeItem* item = getItem(index);
    return item ? item->metadata() : ModelMetadata();
}

QModelIndex ModelTreeModel::findModel(const QString& modelId) const
{
    // Search through all items
    for (int i = 0; i < rootItem->childCount(); ++i) {
        ModelTreeItem* item = rootItem->child(i);
        if (item && item->metadata().id == modelId) {
            return createIndex(i, 0, item);
        }
    }
    return QModelIndex();
}

QList<ModelMetadata> ModelTreeModel::getAllModels() const
{
    QList<ModelMetadata> models;
    for (int i = 0; i < rootItem->childCount(); ++i) {
        ModelTreeItem* item = rootItem->child(i);
        if (item) {
            models.append(item->metadata());
        }
    }
    return models;
}

void ModelTreeModel::setFilterType(const QString& type)
{
    if (filterType != type) {
        filterType = type;
        updateFilterAndSort();
    }
}

void ModelTreeModel::setFilterStatus(const QString& status)
{
    if (filterStatus != status) {
        filterStatus = status;
        updateFilterAndSort();
    }
}

void ModelTreeModel::setFilterText(const QString& text)
{
    if (filterText != text) {
        filterText = text;
        updateFilterAndSort();
    }
}

void ModelTreeModel::setSortColumn(int column)
{
    if (sortColumn != column) {
        sortColumn = column;
        updateFilterAndSort();
    }
}

void ModelTreeModel::setSortOrder(Qt::SortOrder order)
{
    if (sortOrder != order) {
        sortOrder = order;
        updateFilterAndSort();
    }
}

ModelTreeItem* ModelTreeModel::getItem(const QModelIndex& index) const
{
    if (index.isValid()) {
        ModelTreeItem* item = static_cast<ModelTreeItem*>(index.internalPointer());
        if (item)
            return item;
    }
    return rootItem.get();
}

void ModelTreeModel::setupModelData()
{
    // This would typically load data from a database or file
    // For now, it's empty as data will be added through addModel()
}

void ModelTreeModel::updateFilterAndSort()
{
    beginResetModel();
    
    // Store current models
    QList<ModelMetadata> models = getAllModels();
    
    // Clear current items
    rootItem = std::make_unique<ModelTreeItem>(ModelMetadata());
    
    // Filter models
    QList<ModelMetadata> filteredModels;
    for (const auto& model : models) {
        bool matchesType = filterType.isEmpty() || model.type == filterType;
        bool matchesStatus = filterStatus.isEmpty() || model.status == filterStatus;
        bool matchesText = filterText.isEmpty() || 
                          model.name.contains(filterText, Qt::CaseInsensitive) ||
                          model.description.contains(filterText, Qt::CaseInsensitive);
                          
        if (matchesType && matchesStatus && matchesText) {
            filteredModels.append(model);
        }
    }
    
    // Sort models
    std::sort(filteredModels.begin(), filteredModels.end(),
        [this](const ModelMetadata& a, const ModelMetadata& b) {
            int result = 0;
            switch (sortColumn) {
                case 0: result = a.name.compare(b.name); break;
                case 1: result = a.type.compare(b.type); break;
                case 2: result = a.status.compare(b.status); break;
                case 3: result = a.version.compare(b.version); break;
                case 4: result = a.author.compare(b.author); break;
                case 5: result = a.created.compare(b.created); break;
                case 6: result = a.modified.compare(b.modified); break;
            }
            return sortOrder == Qt::AscendingOrder ? result < 0 : result > 0;
        });
    
    // Add filtered and sorted models back to the tree
    for (const auto& model : filteredModels) {
        rootItem->appendChild(new ModelTreeItem(model, rootItem.get()));
    }
    
    endResetModel();
}
