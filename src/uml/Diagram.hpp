#pragma once

#include "Model.hpp"
#include "Relationship.hpp"
#include <string>
#include <vector>
#include <memory>
#include <map>

namespace uml {

enum class DiagramType {
    CLASS,
    SEQUENCE,
    USE_CASE,
    ACTIVITY,
    COMPONENT,
    DEPLOYMENT
};

class Diagram {
public:
    Diagram(const std::string& name, DiagramType type)
        : name_(name), type_(type) {}

    void addElement(std::shared_ptr<Element> element) {
        elements_[element->getName()] = element;
    }

    void addRelationship(std::shared_ptr<Relationship> rel) {
        relationships_.push_back(rel);
    }

    std::shared_ptr<Element> getElement(const std::string& name) const {
        auto it = elements_.find(name);
        return (it != elements_.end()) ? it->second : nullptr;
    }

    const std::map<std::string, std::shared_ptr<Element>>& getElements() const {
        return elements_;
    }

    const std::vector<std::shared_ptr<Relationship>>& getRelationships() const {
        return relationships_;
    }

    const std::string& getName() const { return name_; }
    DiagramType getType() const { return type_; }

    void setDescription(const std::string& desc) { description_ = desc; }
    const std::string& getDescription() const { return description_; }

private:
    std::string name_;
    DiagramType type_;
    std::string description_;
    std::map<std::string, std::shared_ptr<Element>> elements_;
    std::vector<std::shared_ptr<Relationship>> relationships_;
};

} // namespace uml
