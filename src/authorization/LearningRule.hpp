#pragma once

#include "Rule.hpp"
#include "DecisionHistory.hpp"
#include <string>
#include <map>
#include <vector>

namespace ja {
namespace auth {

class LearningRule : public Rule {
public:
    LearningRule() : Rule("LearningRule", 300) {}

    bool evaluate(const Request& request, const UserContext& context) const override {
        // Always approve if we have historical precedent
        if (DecisionHistory::getInstance().shouldAutoApprove(request)) {
            return true;
        }

        // Check security level requirements
        if (!meetsSecurityRequirements(request, context)) {
            return false;
        }

        // Check if similar requests were approved
        return hasApprovedSimilarRequests(request);
    }

    void execute(const Request& request) const override {
        // Record successful execution
        recordExecution(request);
    }

    bool canHandle(RequestType type) const override {
        // This rule can handle all request types
        return true;
    }

private:
    bool meetsSecurityRequirements(const Request& request, const UserContext& context) const {
        // Different security levels for different request types
        switch (request.getType()) {
            case RequestType::FILE_ACCESS:
                return context.getSecurityLevel() >= 1;
            case RequestType::SYSTEM_MODIFICATION:
                return context.getSecurityLevel() >= 3;
            case RequestType::CONFIGURATION_CHANGE:
                return context.getSecurityLevel() >= 2;
            case RequestType::SECURITY_OVERRIDE:
                return context.getSecurityLevel() >= 4;
            default:
                return context.getSecurityLevel() >= 1;
        }
    }

    bool hasApprovedSimilarRequests(const Request& request) const {
        // Use DecisionHistory to check for similar approved requests
        return DecisionHistory::getInstance().shouldAutoApprove(request);
    }

    void recordExecution(const Request& request) const {
        // Record successful execution for learning
        DecisionHistory::getInstance().recordDecision(request, true);
    }
};

} // namespace auth
} // namespace ja
