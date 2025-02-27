#pragma once

#include <QString>
#include <QDateTime>
#include <QStringList>
#include <QVariantMap>

struct ModelMetadata {
    QString id;                  // Unique identifier
    QString name;               // Model name
    QString type;               // Model type (Component, Assembly, System)
    QString description;        // Model description
    QString version;            // Version string (semantic versioning)
    QString author;             // Author name
    QDateTime created;          // Creation timestamp
    QDateTime modified;         // Last modification timestamp
    QStringList tags;          // Associated tags
    QString status;            // Model status (Draft, Review, Released)
    QString location;          // File system location
    qint64 size;              // File size in bytes
    QString format;            // File format (STEP, IGES, etc.)
    QString checksum;          // File checksum for integrity
    QVariantMap properties;    // Additional custom properties
    QStringList dependencies;  // Related model dependencies
    QString parentId;          // Parent model ID (if part of assembly)
    
    // Validation methods
    bool isValid() const {
        return !name.isEmpty() && !type.isEmpty() && !version.isEmpty();
    }
    
    // Version comparison
    bool isNewerThan(const QString& otherVersion) const;
    
    // Serialization
    QVariantMap toMap() const;
    static ModelMetadata fromMap(const QVariantMap& map);
    
    // File operations
    bool save(const QString& filePath) const;
    static ModelMetadata load(const QString& filePath);
};
