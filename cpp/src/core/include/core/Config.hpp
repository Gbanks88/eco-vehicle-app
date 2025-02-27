#pragma once

#include <QObject>
#include <QVariantMap>
#include <QString>
#include <memory>

class Config : public QObject {
    Q_OBJECT

public:
    static Config& instance();

    bool load(const QString& filename);
    void save(const QString& filename) const;

    // Configuration getters
    QString getString(const QString& key, const QString& defaultValue = QString()) const;
    int getInt(const QString& key, int defaultValue = 0) const;
    double getDouble(const QString& key, double defaultValue = 0.0) const;
    bool getBool(const QString& key, bool defaultValue = false) const;
    QVariantMap getMap(const QString& key) const;

    // Configuration setters
    void setString(const QString& key, const QString& value);
    void setInt(const QString& key, int value);
    void setDouble(const QString& key, double value);
    void setBool(const QString& key, bool value);
    void setMap(const QString& key, const QVariantMap& value);

signals:
    void configChanged(const QString& key);

private:
    Config(QObject* parent = nullptr);
    ~Config() override = default;

    Config(const Config&) = delete;
    Config& operator=(const Config&) = delete;

    struct Private;
    std::unique_ptr<Private> d;
};
