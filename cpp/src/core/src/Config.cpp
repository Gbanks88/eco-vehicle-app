#include "core/Config.hpp"
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QDebug>

struct Config::Private {
    QVariantMap config;
};

Config& Config::instance() {
    static Config instance;
    return instance;
}

Config::Config(QObject* parent)
    : QObject(parent)
    , d(std::make_unique<Private>())
{}

bool Config::load(const QString& filename) {
    QFile file(filename);
    if (!file.open(QIODevice::ReadOnly)) {
        qWarning() << "Failed to open config file:" << filename;
        return false;
    }

    QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    if (doc.isNull()) {
        qWarning() << "Failed to parse config file:" << filename;
        return false;
    }

    d->config = doc.object().toVariantMap();
    return true;
}

void Config::save(const QString& filename) const {
    QFile file(filename);
    if (!file.open(QIODevice::WriteOnly)) {
        qWarning() << "Failed to open config file for writing:" << filename;
        return;
    }

    QJsonDocument doc(QJsonObject::fromVariantMap(d->config));
    file.write(doc.toJson(QJsonDocument::Indented));
}

QString Config::getString(const QString& key, const QString& defaultValue) const {
    return d->config.value(key, defaultValue).toString();
}

int Config::getInt(const QString& key, int defaultValue) const {
    return d->config.value(key, defaultValue).toInt();
}

double Config::getDouble(const QString& key, double defaultValue) const {
    return d->config.value(key, defaultValue).toDouble();
}

bool Config::getBool(const QString& key, bool defaultValue) const {
    return d->config.value(key, defaultValue).toBool();
}

QVariantMap Config::getMap(const QString& key) const {
    return d->config.value(key).toMap();
}

void Config::setString(const QString& key, const QString& value) {
    d->config[key] = value;
    emit configChanged(key);
}

void Config::setInt(const QString& key, int value) {
    d->config[key] = value;
    emit configChanged(key);
}

void Config::setDouble(const QString& key, double value) {
    d->config[key] = value;
    emit configChanged(key);
}

void Config::setBool(const QString& key, bool value) {
    d->config[key] = value;
    emit configChanged(key);
}

void Config::setMap(const QString& key, const QVariantMap& value) {
    d->config[key] = value;
    emit configChanged(key);
}
