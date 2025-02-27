#pragma once

#include <string>
#include <map>
#include <vector>
#include <chrono>
#include <mutex>
#include <shared_mutex>
#include "Request.hpp"

namespace ja {
namespace auth {

struct HistoricalDecision {
    std::string requestPattern;
    bool approved;
    std::chrono::system_clock::time_point timestamp;
    std::map<std::string, std::string> context;
};

class DecisionHistory {
public:
    static DecisionHistory& getInstance() {
        static DecisionHistory instance;
        return instance;
    }

    void recordDecision(const Request& request, bool approved) {
        std::unique_lock lock(mutex_);
        
        // Create pattern from request
        std::string pattern = createPattern(request);
        
        // Record the decision
        history_.push_back({
            pattern,
            approved,
            std::chrono::system_clock::now(),
            extractContext(request)
        });

        // Update pattern statistics
        auto& stats = patternStats_[pattern];
        stats.totalDecisions++;
        if (approved) {
            stats.approvals++;
        }
    }

    bool shouldAutoApprove(const Request& request) const {
        std::shared_lock lock(mutex_);
        
        std::string pattern = createPattern(request);
        auto it = patternStats_.find(pattern);
        
        if (it != patternStats_.end()) {
            const auto& stats = it->second;
            // Auto-approve if we have seen this pattern before and it was always approved
            if (stats.totalDecisions >= 3 && stats.approvals == stats.totalDecisions) {
                return true;
            }
        }
        
        // Check similar patterns
        return checkSimilarPatterns(request);
    }

private:
    DecisionHistory() = default;

    struct PatternStats {
        int totalDecisions = 0;
        int approvals = 0;
    };

    std::string createPattern(const Request& request) const {
        std::string pattern = std::to_string(static_cast<int>(request.getType()));
        
        // Add key characteristics to pattern
        for (const auto& [key, value] : request.getData()) {
            try {
                if (auto str = std::any_cast<std::string>(&value)) {
                    pattern += "|" + key + ":" + *str;
                }
            } catch (...) {}
        }
        
        return pattern;
    }

    std::map<std::string, std::string> extractContext(const Request& request) const {
        std::map<std::string, std::string> context;
        const auto& metadata = request.getMetadata();
        
        context["userId"] = metadata.userId;
        context["resourceId"] = metadata.resourceId;
        for (const auto& tag : metadata.tags) {
            context["tag:" + tag] = "true";
        }
        
        return context;
    }

    bool checkSimilarPatterns(const Request& request) const {
        std::string currentPattern = createPattern(request);
        std::map<std::string, int> similarPatternApprovals;
        
        for (const auto& decision : history_) {
            if (isSimilarPattern(currentPattern, decision.requestPattern)) {
                if (decision.approved) {
                    similarPatternApprovals[decision.requestPattern]++;
                }
            }
        }
        
        // If we have similar patterns that were consistently approved
        for (const auto& [pattern, approvals] : similarPatternApprovals) {
            if (approvals >= 3) {  // Require at least 3 similar approved patterns
                return true;
            }
        }
        
        return false;
    }

    bool isSimilarPattern(const std::string& pattern1, const std::string& pattern2) const {
        // Simple similarity check - patterns share the same request type
        return pattern1.substr(0, pattern1.find('|')) == pattern2.substr(0, pattern2.find('|'));
    }

    mutable std::shared_mutex mutex_;
    std::vector<HistoricalDecision> history_;
    std::map<std::string, PatternStats> patternStats_;
};

} // namespace auth
} // namespace ja
