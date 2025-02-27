#pragma once

#include <memory>
#include <map>
#include <queue>
#include <string>
#include <functional>
#include "Request.hpp"
#include "Rule.hpp"
#include "AutomatedBot.hpp"

namespace ja {
namespace auth {

class AuthorizationSystem {
public:
    static AuthorizationSystem& getInstance() {
        static AuthorizationSystem instance;
        return instance;
    }

    bool authorize(const Request& request) {
        if (!request.validate()) {
            return false;
        }

        // Check if request can be handled by automated rules
        if (automatedBot_->canHandle(request)) {
            return automatedBot_->processRequest(request).approved;
        }

        // Add to approval queue if manual review needed
        approvalQueue_.push(request);
        return false;
    }

    void addAutomatedRule(std::shared_ptr<Rule> rule) {
        automatedBot_->addRule(rule);
    }

    void setUserContext(const UserContext& context) {
        automatedBot_->updateContext(context);
    }

private:
    AuthorizationSystem() 
        : automatedBot_(std::make_unique<AutomatedBot>()) {}
    
    AuthorizationSystem(const AuthorizationSystem&) = delete;
    AuthorizationSystem& operator=(const AuthorizationSystem&) = delete;

    std::unique_ptr<AutomatedBot> automatedBot_;
    std::queue<Request> approvalQueue_;
    std::map<std::string, Role> userRoles_;
};

} // namespace auth
} // namespace ja
