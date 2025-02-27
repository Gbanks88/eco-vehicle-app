#pragma once

#include <QObject>
#include <QString>
#include <QWidget>
#include <QMap>
#include <QVector>
#include <memory>
#include <functional>

class DashboardSystem : public QObject {
    Q_OBJECT

public:
    static DashboardSystem& instance();

    // Widget types
    enum class WidgetType {
        Chart,
        Table,
        Gauge,
        Status,
        Timeline,
        KPI,
        ModelViewer,
        FlowViewer,
        DataGrid,
        Map
    };

    // Widget configuration
    struct WidgetConfig {
        QString title;
        WidgetType type;
        QSize size;
        QMap<QString, QVariant> parameters;
        bool refreshable{true};
        int refreshInterval{0};
        bool exportable{true};
        QStringList actions;
    };

    // Dashboard configuration
    struct DashboardConfig {
        QString name;
        QString description;
        QStringList tags;
        QVector<WidgetConfig> widgets;
        QString layout;
        QMap<QString, QVariant> settings;
    };

    // Dashboard management
    void createDashboard(const QString& id, const DashboardConfig& config);
    void updateDashboard(const QString& id, const DashboardConfig& config);
    void removeDashboard(const QString& id);
    QWidget* getDashboardWidget(const QString& id);
    
    // Widget management
    void addWidget(const QString& dashboardId, const WidgetConfig& config);
    void updateWidget(const QString& dashboardId, const QString& widgetId, const QMap<QString, QVariant>& data);
    void removeWidget(const QString& dashboardId, const QString& widgetId);
    
    // Data binding
    void bindData(const QString& dashboardId, const QString& widgetId, std::function<QVariant()> dataProvider);
    void bindAction(const QString& dashboardId, const QString& widgetId, const QString& action, std::function<void()> callback);
    
    // Layout management
    void setLayout(const QString& dashboardId, const QString& layout);
    void saveLayout(const QString& dashboardId);
    void resetLayout(const QString& dashboardId);
    
    // Theming
    void setTheme(const QString& theme);
    void customizeWidget(const QString& dashboardId, const QString& widgetId, const QMap<QString, QVariant>& style);
    
    // Interaction
    void enableInteraction(const QString& dashboardId, bool enable);
    void setRefreshInterval(const QString& dashboardId, const QString& widgetId, int seconds);
    
    // Export
    void exportDashboard(const QString& dashboardId, const QString& format, const QString& path);
    void exportWidget(const QString& dashboardId, const QString& widgetId, const QString& format, const QString& path);
    
    // State management
    void saveDashboardState(const QString& dashboardId);
    void loadDashboardState(const QString& dashboardId);
    void resetDashboardState(const QString& dashboardId);

signals:
    void dashboardCreated(const QString& id);
    void dashboardUpdated(const QString& id);
    void dashboardRemoved(const QString& id);
    void widgetAdded(const QString& dashboardId, const QString& widgetId);
    void widgetUpdated(const QString& dashboardId, const QString& widgetId);
    void widgetRemoved(const QString& dashboardId, const QString& widgetId);
    void dataUpdated(const QString& dashboardId, const QString& widgetId);
    void actionTriggered(const QString& dashboardId, const QString& widgetId, const QString& action);
    void layoutChanged(const QString& dashboardId);
    void themeChanged(const QString& theme);
    void interactionStateChanged(const QString& dashboardId, bool enabled);
    void exportCompleted(const QString& path);
    void stateChanged(const QString& dashboardId);
    void error(const QString& dashboardId, const QString& error);

private:
    DashboardSystem(QObject* parent = nullptr);
    ~DashboardSystem() = default;
    DashboardSystem(const DashboardSystem&) = delete;
    DashboardSystem& operator=(const DashboardSystem&) = delete;

    struct Dashboard {
        DashboardConfig config;
        QWidget* widget;
        QMap<QString, QWidget*> widgets;
        QMap<QString, std::function<QVariant()>> dataProviders;
        QMap<QString, QMap<QString, std::function<void()>>> actions;
        QTimer* refreshTimer;
    };

    // Internal methods
    Dashboard* getDashboard(const QString& id);
    QWidget* createWidget(const WidgetConfig& config);
    void setupWidget(QWidget* widget, const WidgetConfig& config);
    void updateWidgetData(Dashboard* dashboard, const QString& widgetId);
    void applyTheme(Dashboard* dashboard);
    void saveState(Dashboard* dashboard);
    
    // State
    QMap<QString, std::unique_ptr<Dashboard>> dashboards_;
    QString currentTheme_;
};
