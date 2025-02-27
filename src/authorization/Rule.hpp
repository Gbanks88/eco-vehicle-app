#pragma once

#include <string>
#include <functional>
#include "Request.hpp"
#include "UserContext.hpp"

namespace ja {
namespace auth {

class Rule {
public:
    Rule(std::string name, int priority)
        : name_(std::move(name))
        , priority_(priority) {}

    virtual ~Rule() = default;

    virtual bool evaluate(const Request& request, const UserContext& context) const = 0;
    virtual void execute(const Request& request) const = 0;
    virtual bool canHandle(RequestType type) const = 0;

    int getPriority() const { return priority_; }
    const std::string& getName() const { return name_; }

protected:
    std::string name_;
    int priority_;
};

// Example concrete rule for file access
class FileAccessRule : public Rule {
public:
    FileAccessRule() : Rule("FileAccessRule", 100) {}

    bool evaluate(const Request& request, const UserContext& context) const override {
        if (request.getType() != RequestType::FILE_ACCESS) {
            return false;
        }

        try {
            auto path = std::any_cast<std::string>(request.getData().at("path"));
            return context.hasPermission("file_access") && 
                   isPathAllowed(path, context.getSecurityLevel());
        } catch (...) {
            return false;
        }
    }

    void execute(const Request& request) const override {
        // Log access
        // Implement any necessary actions
    }

    bool canHandle(RequestType type) const override {
        return type == RequestType::FILE_ACCESS;
    }

private:
    bool isPathAllowed(const std::string& path, int securityLevel) const {
        // Implement path validation logic
        return true;
    }
};

// Example concrete rule for system modifications
class SystemModRule : public Rule {
public:
    SystemModRule() : Rule("SystemModRule", 200) {}

    bool evaluate(const Request& request, const UserContext& context) const override {
        if (request.getType() != RequestType::SYSTEM_MODIFICATION) {
            return false;
        }

        return context.hasPermission("system_mod") && 
               context.getSecurityLevel() >= 3;
    }

    void execute(const Request& request) const override {
        // Implement system modification logic
    }

    bool canHandle(RequestType type) const override {
        return type == RequestType::SYSTEM_MODIFICATION;
    }
};

} // namespace auth
} // namespace ja
