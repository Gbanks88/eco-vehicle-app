#include "Logger.hpp"
#include "Config.hpp"
#include <QDir>
#include <QDebug>
#include <QThread>

Logger::Logger(QObject* parent)
    : QObject(parent)
    , logLevel_(LogLevel::Info)
    , consoleOutput_(true)
    , fileOutput_(true)
    , maxFileSize_(1024 * 1024 * 10) // 10MB
    , maxBackupCount_(5)
{
    // Get log file path from config
    auto& config = Config::instance();
    setLogFile(config.getLogPath() + "/app.log");
}

Logger::~Logger()
{
    if (logFile_.isOpen()) {
        fileStream_.flush();
        logFile_.close();
    }
}

Logger& Logger::instance()
{
    static Logger instance;
    return instance;
}

void Logger::setLogFile(const QString& filePath)
{
    QMutexLocker locker(&mutex_);
    
    // Close existing file if open
    if (logFile_.isOpen()) {
        fileStream_.flush();
        logFile_.close();
    }
    
    // Create directory if it doesn't exist
    QDir dir = QFileInfo(filePath).dir();
    if (!dir.exists()) {
        dir.mkpath(".");
    }
    
    logFilePath_ = filePath;
    logFile_.setFileName(filePath);
    
    if (!logFile_.open(QIODevice::WriteOnly | QIODevice::Append | QIODevice::Text)) {
        qWarning() << "Failed to open log file:" << filePath;
        return;
    }
    
    fileStream_.setDevice(&logFile_);
}

void Logger::setLogLevel(LogLevel level)
{
    logLevel_ = level;
}

void Logger::setConsoleOutput(bool enabled)
{
    consoleOutput_ = enabled;
}

void Logger::setFileOutput(bool enabled)
{
    fileOutput_ = enabled;
}

void Logger::setMaxFileSize(qint64 bytes)
{
    maxFileSize_ = bytes;
}

void Logger::setMaxBackupCount(int count)
{
    maxBackupCount_ = count;
}

QString Logger::getLogFilePath() const
{
    return logFilePath_;
}

LogLevel Logger::getLogLevel() const
{
    return logLevel_;
}

bool Logger::isConsoleOutputEnabled() const
{
    return consoleOutput_;
}

bool Logger::isFileOutputEnabled() const
{
    return fileOutput_;
}

void Logger::debug(const QString& message, const QString& component)
{
    if (logLevel_ <= LogLevel::Debug) {
        log(LogLevel::Debug, message, component);
    }
}

void Logger::info(const QString& message, const QString& component)
{
    if (logLevel_ <= LogLevel::Info) {
        log(LogLevel::Info, message, component);
    }
}

void Logger::warning(const QString& message, const QString& component)
{
    if (logLevel_ <= LogLevel::Warning) {
        log(LogLevel::Warning, message, component);
    }
}

void Logger::error(const QString& message, const QString& component)
{
    if (logLevel_ <= LogLevel::Error) {
        log(LogLevel::Error, message, component);
    }
}

void Logger::critical(const QString& message, const QString& component)
{
    if (logLevel_ <= LogLevel::Critical) {
        log(LogLevel::Critical, message, component);
    }
}

void Logger::log(LogLevel level, const QString& message, const QString& component)
{
    QMutexLocker locker(&mutex_);
    
    QString formattedMessage = formatMessage(level, message, component);
    
    if (consoleOutput_) {
        switch (level) {
            case LogLevel::Debug:
                qDebug().noquote() << formattedMessage;
                break;
            case LogLevel::Info:
                qInfo().noquote() << formattedMessage;
                break;
            case LogLevel::Warning:
                qWarning().noquote() << formattedMessage;
                break;
            case LogLevel::Error:
            case LogLevel::Critical:
                qCritical().noquote() << formattedMessage;
                break;
        }
    }
    
    if (fileOutput_ && logFile_.isOpen()) {
        fileStream_ << formattedMessage << Qt::endl;
        fileStream_.flush();
        
        checkFileSize();
    }
    
    emit logMessageReceived(level, message, component);
}

void Logger::checkFileSize()
{
    if (logFile_.size() >= maxFileSize_) {
        rotateLogFiles();
    }
}

void Logger::rotateLogFiles()
{
    fileStream_.flush();
    logFile_.close();
    
    // Remove oldest backup if it exists
    QString oldestBackup = QString("%1.%2").arg(logFilePath_).arg(maxBackupCount_);
    QFile::remove(oldestBackup);
    
    // Rename existing backups
    for (int i = maxBackupCount_ - 1; i >= 1; --i) {
        QString oldName = QString("%1.%2").arg(logFilePath_).arg(i);
        QString newName = QString("%1.%2").arg(logFilePath_).arg(i + 1);
        QFile::rename(oldName, newName);
    }
    
    // Rename current log file
    QString backupName = QString("%1.1").arg(logFilePath_);
    QFile::rename(logFilePath_, backupName);
    
    // Open new log file
    logFile_.setFileName(logFilePath_);
    logFile_.open(QIODevice::WriteOnly | QIODevice::Append | QIODevice::Text);
    fileStream_.setDevice(&logFile_);
    
    emit logFileRotated(backupName, logFilePath_);
}

QString Logger::formatMessage(LogLevel level, const QString& message, const QString& component) const
{
    QString timestamp = QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss.zzz");
    QString threadId = QString("0x%1").arg(quintptr(QThread::currentThreadId()), 8, 16, QLatin1Char('0'));
    QString levelStr = levelToString(level);
    QString componentStr = component.isEmpty() ? "App" : component;
    
    return QString("[%1] [%2] [%3] [%4] %5")
        .arg(timestamp)
        .arg(threadId)
        .arg(levelStr)
        .arg(componentStr)
        .arg(message);
}

QString Logger::levelToString(LogLevel level)
{
    switch (level) {
        case LogLevel::Debug:    return "DEBUG";
        case LogLevel::Info:     return "INFO";
        case LogLevel::Warning:  return "WARN";
        case LogLevel::Error:    return "ERROR";
        case LogLevel::Critical: return "CRIT";
        default:                 return "UNKNOWN";
    }
}
