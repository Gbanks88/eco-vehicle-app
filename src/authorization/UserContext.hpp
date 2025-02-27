#pragma once

#include <string>
#include <vector>
#include <set>

namespace ja {
namespace auth {

class UserContext {
public:
    UserContext(std::string userId, int securityLevel)
        : userId_(std::move(userId))
        , securityLevel_(securityLevel) {}

    void addPermission(const std::string& permission) {
        permissions_.insert(permission);
    }

    bool hasPermission(const std::string& permission) const {
        return permissions_.find(permission) != permissions_.end();
    }

    int getSecurityLevel() const { return securityLevel_; }
    const std::string& getUserId() const { return userId_; }

private:
    std::string userId_;
    int securityLevel_;
    std::set<std::string> permissions_;
};

} // namespace auth
} // namespace ja
