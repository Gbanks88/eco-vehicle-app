#pragma once

#include <QObject>
#include <QString>
#include <QVariant>
#include <QVector>
#include <QImage>
#include <QColor>
#include <memory>

class DesignSystem : public QObject {
    Q_OBJECT

public:
    static DesignSystem& instance();

    // Design tokens
    struct DesignTokens {
        // Colors
        struct Colors {
            QColor primary;
            QColor secondary;
            QColor accent;
            QColor success;
            QColor warning;
            QColor error;
            QVector<QColor> neutrals;
            QVector<QColor> primaryShades;
            QVector<QColor> secondaryShades;
        } colors;

        // Typography
        struct Typography {
            QString headingFont;
            QString bodyFont;
            QString monoFont;
            QVector<int> fontSizes;
            QVector<float> lineHeights;
            QVector<int> fontWeights;
            QMap<QString, QString> textStyles;
        } typography;

        // Spacing
        struct Spacing {
            QVector<int> space;
            QVector<int> size;
            QVector<int> radius;
            QVector<int> border;
        } spacing;

        // Animation
        struct Animation {
            QVector<int> duration;
            QMap<QString, QString> easing;
            QMap<QString, QVariant> transitions;
        } animation;
    };

    // Component library
    struct Component {
        QString name;
        QString category;
        QString description;
        QVector<QString> variants;
        QMap<QString, QVariant> properties;
        QImage preview;
        QString usage;
        QString code;
    };

    // Theme management
    void setTheme(const QString& theme);
    QString currentTheme() const;
    QStringList availableThemes() const;
    void customizeTheme(const QString& theme, const DesignTokens& tokens);
    
    // Component management
    void registerComponent(const Component& component);
    Component getComponent(const QString& name) const;
    QStringList getComponentCategories() const;
    QVector<Component> getComponentsByCategory(const QString& category) const;
    
    // Design token access
    DesignTokens getTokens() const;
    QVariant getToken(const QString& path) const;
    void setToken(const QString& path, const QVariant& value);
    
    // Style generation
    QString generateStyleSheet() const;
    QString generateComponentStyle(const QString& component) const;
    
    // Design system documentation
    QString generateStyleGuide() const;
    QString generateComponentDocs() const;
    QImage generateTokenVisuals() const;

    // Design validation
    bool validateDesign(const QString& componentName);
    QStringList checkAccessibility();
    QStringList checkConsistency();

signals:
    void themeChanged(const QString& theme);
    void tokenChanged(const QString& path, const QVariant& value);
    void componentAdded(const QString& name);
    void componentUpdated(const QString& name);
    void designValidated(const QString& component, bool valid);
    void accessibilityIssueFound(const QString& component, const QString& issue);
    void consistencyIssueFound(const QString& component, const QString& issue);

private:
    DesignSystem(QObject* parent = nullptr);
    ~DesignSystem() = default;
    DesignSystem(const DesignSystem&) = delete;
    DesignSystem& operator=(const DesignSystem&) = delete;

    // Internal methods
    void loadTheme(const QString& theme);
    void applyTokens(const DesignTokens& tokens);
    void validateTokens(const DesignTokens& tokens);
    void generateColorPalette();
    void updateStyleSheets();
    
    // State
    QString currentThemeName_;
    DesignTokens currentTokens_;
    QMap<QString, Component> components_;
    QMap<QString, DesignTokens> themes_;
};
