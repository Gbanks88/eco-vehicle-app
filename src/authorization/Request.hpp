#pragma once

#include <string>
#include <map>
#include <any>
#include <chrono>
#include <vector>

namespace ja {
namespace auth {

enum class RequestType {
    FILE_ACCESS,
    SYSTEM_MODIFICATION,
    CONFIGURATION_CHANGE,
    RESOURCE_ALLOCATION,
    SECURITY_OVERRIDE
};

struct Metadata {
    std::string userId;
    std::string resourceId;
    std::chrono::system_clock::time_point timestamp;
    std::vector<std::string> tags;
};

class Request {
public:
    Request(std::string id, RequestType type)
        : requestId_(std::move(id))
        , type_(type) {
        metadata_.timestamp = std::chrono::system_clock::now();
    }

    bool validate() const {
        // Basic validation
        if (requestId_.empty()) return false;
        if (metadata_.userId.empty()) return false;
        
        // Type-specific validation
        switch (type_) {
            case RequestType::FILE_ACCESS:
                return validateFileAccess();
            case RequestType::SYSTEM_MODIFICATION:
                return validateSystemMod();
            default:
                return true;
        }
    }

    void addData(const std::string& key, const std::any& value) {
        data_[key] = value;
    }

    const Metadata& getMetadata() const { return metadata_; }
    const std::string& getRequestId() const { return requestId_; }
    RequestType getType() const { return type_; }

private:
    bool validateFileAccess() const {
        try {
            auto path = std::any_cast<std::string>(data_.at("path"));
            return !path.empty();
        } catch (...) {
            return false;
        }
    }

    bool validateSystemMod() const {
        try {
            auto component = std::any_cast<std::string>(data_.at("component"));
            auto action = std::any_cast<std::string>(data_.at("action"));
            return !component.empty() && !action.empty();
        } catch (...) {
            return false;
        }
    }

    std::string requestId_;
    RequestType type_;
    Metadata metadata_;
    std::map<std::string, std::any> data_;
};

} // namespace auth
} // namespace ja
