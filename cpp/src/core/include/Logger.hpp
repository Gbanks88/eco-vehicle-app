#pragma once

#include <QObject>
#include <QString>
#include <QFile>
#include <QTextStream>
#include <QDateTime>
#include <QMutex>
#include <memory>

enum class LogLevel {
    Debug,
    Info,
    Warning,
    Error,
    Critical
};

class Logger : public QObject {
    Q_OBJECT

public:
    static Logger& instance();

    // Logging methods
    void debug(const QString& message, const QString& component = QString());
    void info(const QString& message, const QString& component = QString());
    void warning(const QString& message, const QString& component = QString());
    void error(const QString& message, const QString& component = QString());
    void critical(const QString& message, const QString& component = QString());

    // Configuration
    void setLogFile(const QString& filePath);
    void setLogLevel(LogLevel level);
    void setConsoleOutput(bool enabled);
    void setFileOutput(bool enabled);
    void setMaxFileSize(qint64 bytes);
    void setMaxBackupCount(int count);

    // Utility methods
    QString getLogFilePath() const;
    LogLevel getLogLevel() const;
    bool isConsoleOutputEnabled() const;
    bool isFileOutputEnabled() const;

signals:
    void logMessageReceived(LogLevel level, const QString& message, const QString& component);
    void logFileRotated(const QString& oldFile, const QString& newFile);

private:
    Logger(QObject* parent = nullptr);
    ~Logger();
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    void log(LogLevel level, const QString& message, const QString& component);
    void checkFileSize();
    void rotateLogFiles();
    QString formatMessage(LogLevel level, const QString& message, const QString& component) const;
    static QString levelToString(LogLevel level);

    QFile logFile_;
    QTextStream fileStream_;
    QString logFilePath_;
    LogLevel logLevel_;
    bool consoleOutput_;
    bool fileOutput_;
    qint64 maxFileSize_;
    int maxBackupCount_;
    QMutex mutex_;
};
