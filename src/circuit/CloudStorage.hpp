#pragma once

#include <string>
#include <vector>
#include <memory>
#include <filesystem>
#include <megaapi.h>
#include <digitalocean/digitalocean.hpp>
#include "SecurityManager.hpp"

namespace circuit {

class CloudStorage {
public:
    struct StorageConfig {
        // MEGA configuration
        struct MegaConfig {
            std::string email;
            std::string password;
            std::string app_key;
            std::string base_path;
            size_t quota_limit;  // in bytes
        };

        // DigitalOcean Spaces configuration
        struct DOSpacesConfig {
            std::string access_key;
            std::string secret_key;
            std::string region;
            std::string bucket_name;
            std::string endpoint;
        };

        MegaConfig mega;
        DOSpacesConfig spaces;
    };

    struct StorageMetrics {
        size_t total_space;
        size_t used_space;
        size_t available_space;
        std::vector<std::string> active_buckets;
        std::string primary_storage;
        double sync_status;  // percentage
    };

    CloudStorage(std::shared_ptr<SecurityManager> security_manager,
                const StorageConfig& config)
        : security_manager_(security_manager),
          config_(config) {
        
        initializeMega();
        initializeDigitalOcean();
    }

    ~CloudStorage() {
        if (mega_api_) {
            mega_api_->logout();
            delete mega_api_;
        }
    }

    bool uploadFile(const std::string& local_path,
                   const std::string& remote_path,
                   bool use_mega = true) {
        if (use_mega) {
            return uploadToMega(local_path, remote_path);
        } else {
            return uploadToSpaces(local_path, remote_path);
        }
    }

    bool downloadFile(const std::string& remote_path,
                     const std::string& local_path,
                     bool use_mega = true) {
        if (use_mega) {
            return downloadFromMega(remote_path, local_path);
        } else {
            return downloadFromSpaces(remote_path, local_path);
        }
    }

    bool syncDirectory(const std::string& local_dir,
                      const std::string& remote_dir) {
        try {
            if (!mega_api_) return false;

            // Set up sync
            mega_api_->syncFolder(local_dir.c_str(),
                                remote_dir.c_str(),
                                MegaSync::TYPE_TWOWAY);

            return true;
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
            return false;
        }
    }

    StorageMetrics getMetrics() {
        StorageMetrics metrics;
        
        if (mega_api_) {
            metrics.total_space = mega_api_->getTotalSpace();
            metrics.used_space = mega_api_->getUsedSpace();
            metrics.available_space = metrics.total_space - metrics.used_space;
            metrics.primary_storage = "MEGA";
            
            auto nodes = mega_api_->getChildren(mega_api_->getRootNode());
            for (int i = 0; i < nodes->size(); i++) {
                auto node = nodes->get(i);
                if (node->isFolder()) {
                    metrics.active_buckets.push_back(node->getName());
                }
            }
            
            metrics.sync_status = calculateSyncStatus();
        }
        
        return metrics;
    }

    std::string getLastError() const {
        return last_error_;
    }

private:
    std::shared_ptr<SecurityManager> security_manager_;
    StorageConfig config_;
    mega::MegaApi* mega_api_ = nullptr;
    std::unique_ptr<digitalocean::Client> do_client_;
    std::string last_error_;

    void initializeMega() {
        try {
            mega_api_ = new mega::MegaApi(config_.mega.app_key.c_str());
            
            // Login
            mega_api_->login(config_.mega.email.c_str(),
                           config_.mega.password.c_str());
            
            // Set base path
            if (!config_.mega.base_path.empty()) {
                mega_api_->setDefaultWorkingDirectory(
                    config_.mega.base_path.c_str());
            }
        }
        catch (const std::exception& e) {
            last_error_ = "MEGA initialization failed: " + std::string(e.what());
        }
    }

    void initializeDigitalOcean() {
        try {
            do_client_ = std::make_unique<digitalocean::Client>(
                config_.spaces.access_key,
                config_.spaces.secret_key,
                config_.spaces.region
            );
        }
        catch (const std::exception& e) {
            last_error_ = "DigitalOcean initialization failed: " + 
                         std::string(e.what());
        }
    }

    bool uploadToMega(const std::string& local_path,
                     const std::string& remote_path) {
        try {
            if (!mega_api_) return false;

            auto parent_node = mega_api_->getNodeByPath(
                std::filesystem::path(remote_path)
                    .parent_path().string().c_str());

            if (!parent_node) {
                last_error_ = "Remote parent directory not found";
                return false;
            }

            mega_api_->startUpload(local_path.c_str(),
                                 parent_node,
                                 std::filesystem::path(remote_path)
                                     .filename().string().c_str());

            return true;
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
            return false;
        }
    }

    bool uploadToSpaces(const std::string& local_path,
                       const std::string& remote_path) {
        try {
            if (!do_client_) return false;

            auto request = do_client_->storage()
                .uploadObject(config_.spaces.bucket_name,
                            remote_path,
                            local_path);

            auto response = request.execute();
            return response.isSuccessful();
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
            return false;
        }
    }

    bool downloadFromMega(const std::string& remote_path,
                         const std::string& local_path) {
        try {
            if (!mega_api_) return false;

            auto node = mega_api_->getNodeByPath(remote_path.c_str());
            if (!node) {
                last_error_ = "Remote file not found";
                return false;
            }

            mega_api_->startDownload(node,
                                   local_path.c_str());

            return true;
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
            return false;
        }
    }

    bool downloadFromSpaces(const std::string& remote_path,
                          const std::string& local_path) {
        try {
            if (!do_client_) return false;

            auto request = do_client_->storage()
                .downloadObject(config_.spaces.bucket_name,
                              remote_path,
                              local_path);

            auto response = request.execute();
            return response.isSuccessful();
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
            return false;
        }
    }

    double calculateSyncStatus() {
        if (!mega_api_) return 0.0;

        auto syncs = mega_api_->getSyncs();
        if (!syncs || syncs->size() == 0) return 100.0;

        int total_syncs = syncs->size();
        int completed_syncs = 0;

        for (int i = 0; i < total_syncs; i++) {
            auto sync = syncs->get(i);
            if (sync->getState() == MegaSync::SYNC_STATE_SYNCED) {
                completed_syncs++;
            }
        }

        return (static_cast<double>(completed_syncs) / total_syncs) * 100.0;
    }
};

} // namespace circuit
