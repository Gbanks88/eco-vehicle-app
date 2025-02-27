#pragma once

#include <QObject>
#include <QString>
#include <QVariant>
#include <QMap>
#include <memory>

class Config : public QObject {
    Q_OBJECT

public:
    static Config& instance();

    // System paths
    QString getResourcePath() const;
    QString getDatabasePath() const;
    QString getLogPath() const;
    QString getTranslationPath() const;
    QString getIconPath() const;
    QString getStylePath() const;
    QString getTemplatePath() const;

    // Database settings
    QString getDatabaseType() const;
    QString getDatabaseHost() const;
    int getDatabasePort() const;
    QString getDatabaseName() const;
    QString getDatabaseUser() const;
    QString getDatabasePassword() const;

    // Application settings
    QString getTheme() const;
    void setTheme(const QString& theme);
    QString getLanguage() const;
    void setLanguage(const QString& language);
    bool getDebugMode() const;
    void setDebugMode(bool enabled);

    // Load and save configuration
    bool loadConfig(const QString& configFile);
    bool saveConfig(const QString& configFile) const;

    // Get/Set arbitrary configuration values
    QVariant getValue(const QString& key, const QVariant& defaultValue = QVariant()) const;
    void setValue(const QString& key, const QVariant& value);

signals:
    void configChanged(const QString& key);
    void themeChanged(const QString& theme);
    void languageChanged(const QString& language);
    void debugModeChanged(bool enabled);

private:
    Config(QObject* parent = nullptr);
    ~Config() = default;
    Config(const Config&) = delete;
    Config& operator=(const Config&) = delete;

    QMap<QString, QVariant> settings_;
    QString configFile_;

    // Initialize default settings
    void initializeDefaults();
};
