#pragma once

#include <QWidget>
#include <QString>
#include <memory>

class BackupTab : public QWidget {
    Q_OBJECT

public:
    explicit BackupTab(QWidget* parent = nullptr);
    ~BackupTab() override;

public slots:
    void startBackup();
    void startRestore();
    void showBackupHistory();
    void configureBackup();
    void scheduleBackup();
    void verifyBackup();
    void exportBackupLog();

signals:
    void backupStarted();
    void backupCompleted(bool success);
    void restoreStarted();
    void restoreCompleted(bool success);
    void backupConfigChanged();
    void scheduleChanged();

private:
    void setupUi();
    void setupBackupControls();
    void setupRestoreControls();
    void setupScheduleConfig();
    void updateBackupStatus();
    void loadBackupConfig();
    void saveBackupConfig();
    void validateBackupLocation();
    void checkDiskSpace();

    struct Private;
    std::unique_ptr<Private> d;
};
