#pragma once

#include <vector>
#include <memory>
#include "Rule.hpp"
#include "Request.hpp"
#include "UserContext.hpp"
#include "DecisionHistory.hpp"

namespace ja {
namespace auth {

struct Decision {
    bool approved;
    std::string reason;
    std::chrono::system_clock::time_point timestamp;
};

class AutomatedBot {
public:
    AutomatedBot() = default;

    Decision processRequest(const Request& request) {
        Decision decision{false, "", std::chrono::system_clock::now()};

        // First check decision history for auto-approval
        if (DecisionHistory::getInstance().shouldAutoApprove(request)) {
            decision.approved = true;
            decision.reason = "Auto-approved based on historical decisions";
            logDecision(request, decision);
            return decision;
        }

        // Sort rules by priority
        std::sort(rules_.begin(), rules_.end(),
            [](const auto& a, const auto& b) {
                return a->getPriority() > b->getPriority();
            });

        // Evaluate rules in priority order
        for (const auto& rule : rules_) {
            if (rule->evaluate(request, context_)) {
                decision.approved = true;
                decision.reason = "Approved by rule: " + rule->getName();
                rule->execute(request);
                break;
            }
        }

        // Record the decision for future reference
        DecisionHistory::getInstance().recordDecision(request, decision.approved);

        // Log decision
        logDecision(request, decision);
        return decision;
    }

    bool canHandle(const Request& request) const {
        // Auto-approve if we have historical precedent
        if (DecisionHistory::getInstance().shouldAutoApprove(request)) {
            return true;
        }

        // Check if we have rules that can handle this type of request
        return std::any_of(rules_.begin(), rules_.end(),
            [&request](const auto& rule) {
                return rule->canHandle(request.getType());
            });
    }

    void addRule(std::shared_ptr<Rule> rule) {
        rules_.push_back(std::move(rule));
    }

    void updateContext(const UserContext& context) {
        context_ = context;
    }

private:
    void logDecision(const Request& request, const Decision& decision) {
        // TODO: Implement comprehensive logging
        // Log format: timestamp | requestId | type | decision | reason
    }

    std::vector<std::shared_ptr<Rule>> rules_;
    UserContext context_;
};

} // namespace auth
} // namespace ja
