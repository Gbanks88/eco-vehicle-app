#pragma once

#include "Model.hpp"
#include <memory>

namespace uml {

enum class RelationType {
    ASSOCIATION,
    AGGREGATION,
    COMPOSITION,
    INHERITANCE,
    REALIZATION,
    DEPENDENCY
};

class Relationship : public Element {
public:
    Relationship(const std::string& name, 
                std::shared_ptr<Element> source,
                std::shared_ptr<Element> target,
                RelationType type)
        : Element(name, ElementType::RELATIONSHIP),
          source_(source),
          target_(target),
          type_(type) {}

    std::shared_ptr<Element> getSource() const { return source_; }
    std::shared_ptr<Element> getTarget() const { return target_; }
    RelationType getRelationType() const { return type_; }

    void setMultiplicitySource(const std::string& mult) { multiplicitySource_ = mult; }
    void setMultiplicityTarget(const std::string& mult) { multiplicityTarget_ = mult; }
    
    const std::string& getMultiplicitySource() const { return multiplicitySource_; }
    const std::string& getMultiplicityTarget() const { return multiplicityTarget_; }

private:
    std::shared_ptr<Element> source_;
    std::shared_ptr<Element> target_;
    RelationType type_;
    std::string multiplicitySource_;
    std::string multiplicityTarget_;
};

} // namespace uml
