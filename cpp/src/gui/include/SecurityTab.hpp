#pragma once

#include <QWidget>
#include <QString>
#include <memory>

class SecurityTab : public QWidget {
    Q_OBJECT

public:
    explicit SecurityTab(QWidget* parent = nullptr);
    ~SecurityTab() override;

public slots:
    void addSecurityAlert(const QString& alert);
    void updateSecurityStatus(const QString& status);
    void showAccessLog();
    void configurePermissions();
    void manageUsers();
    void backupSecuritySettings();
    void restoreSecuritySettings();

signals:
    void securitySettingsChanged();
    void userAdded(const QString& username);
    void userRemoved(const QString& username);
    void permissionsChanged(const QString& username, const QStringList& permissions);

private:
    void setupUi();
    void setupAlertList();
    void setupSecurityControls();
    void setupUserManagement();
    void updateSecurityMetrics();
    void loadSecurityConfig();
    void saveSecurityConfig();

    struct Private;
    std::unique_ptr<Private> d;
};
