#pragma once

#include "Diagram.hpp"
#include <memory>
#include <vector>
#include <string>

namespace uml {

enum class ActivityNodeType {
    INITIAL,
    FINAL,
    ACTION,
    DECISION,
    MERGE,
    FORK,
    JOIN,
    OBJECT
};

class ActivityNode : public Element {
public:
    ActivityNode(const std::string& name, ActivityNodeType type)
        : Element(name, ElementType::COMPONENT),
          nodeType_(type) {}

    ActivityNodeType getNodeType() const { return nodeType_; }

private:
    ActivityNodeType nodeType_;
};

class ActivityEdge : public Element {
public:
    ActivityEdge(const std::string& name,
                std::shared_ptr<ActivityNode> source,
                std::shared_ptr<ActivityNode> target)
        : Element(name, ElementType::RELATIONSHIP),
          source_(source),
          target_(target) {}

    void setGuard(const std::string& guard) { guard_ = guard; }
    const std::string& getGuard() const { return guard_; }

    std::shared_ptr<ActivityNode> getSource() const { return source_; }
    std::shared_ptr<ActivityNode> getTarget() const { return target_; }

private:
    std::shared_ptr<ActivityNode> source_;
    std::shared_ptr<ActivityNode> target_;
    std::string guard_;
};

class ActivityPartition : public Element {
public:
    ActivityPartition(const std::string& name)
        : Element(name, ElementType::PACKAGE) {}

    void addNode(std::shared_ptr<ActivityNode> node) {
        nodes_.push_back(node);
    }

    const std::vector<std::shared_ptr<ActivityNode>>& getNodes() const {
        return nodes_;
    }

private:
    std::vector<std::shared_ptr<ActivityNode>> nodes_;
};

class ActivityDiagram : public Diagram {
public:
    ActivityDiagram(const std::string& name)
        : Diagram(name, DiagramType::ACTIVITY) {}

    void addNode(std::shared_ptr<ActivityNode> node) {
        nodes_.push_back(node);
        addElement(node);
    }

    void addEdge(std::shared_ptr<ActivityEdge> edge) {
        edges_.push_back(edge);
        addElement(edge);
    }

    void addPartition(std::shared_ptr<ActivityPartition> partition) {
        partitions_.push_back(partition);
        addElement(partition);
    }

    std::shared_ptr<ActivityNode> getInitialNode() const {
        for (const auto& node : nodes_) {
            if (node->getNodeType() == ActivityNodeType::INITIAL) {
                return node;
            }
        }
        return nullptr;
    }

    std::vector<std::shared_ptr<ActivityNode>> getFinalNodes() const {
        std::vector<std::shared_ptr<ActivityNode>> finals;
        for (const auto& node : nodes_) {
            if (node->getNodeType() == ActivityNodeType::FINAL) {
                finals.push_back(node);
            }
        }
        return finals;
    }

    const std::vector<std::shared_ptr<ActivityNode>>& getNodes() const {
        return nodes_;
    }

    const std::vector<std::shared_ptr<ActivityEdge>>& getEdges() const {
        return edges_;
    }

    const std::vector<std::shared_ptr<ActivityPartition>>& getPartitions() const {
        return partitions_;
    }

private:
    std::vector<std::shared_ptr<ActivityNode>> nodes_;
    std::vector<std::shared_ptr<ActivityEdge>> edges_;
    std::vector<std::shared_ptr<ActivityPartition>> partitions_;
};

} // namespace uml
