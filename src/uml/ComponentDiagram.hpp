#pragma once

#include "Diagram.hpp"
#include <memory>
#include <vector>
#include <string>
#include <map>

namespace uml {

class Port : public Element {
public:
    enum class Direction {
        IN,
        OUT,
        INOUT
    };

    Port(const std::string& name, Direction direction)
        : Element(name, ElementType::COMPONENT),
          direction_(direction) {}

    Direction getDirection() const { return direction_; }

private:
    Direction direction_;
};

class Interface : public Element {
public:
    Interface(const std::string& name)
        : Element(name, ElementType::INTERFACE) {}

    void addOperation(const std::string& name,
                     const std::string& returnType,
                     const std::vector<std::pair<std::string, std::string>>& params) {
        operations_[name] = {returnType, params};
    }

    const std::map<std::string,
                  std::pair<std::string,
                           std::vector<std::pair<std::string, std::string>>>>& 
    getOperations() const {
        return operations_;
    }

private:
    // Map of operation name to {return type, vector of {param name, param type}}
    std::map<std::string,
             std::pair<std::string,
                      std::vector<std::pair<std::string, std::string>>>> operations_;
};

class Component : public Element {
public:
    Component(const std::string& name)
        : Element(name, ElementType::COMPONENT) {}

    void addPort(std::shared_ptr<Port> port) {
        ports_.push_back(port);
    }

    void addInterface(std::shared_ptr<Interface> interface, bool isProvided) {
        if (isProvided) {
            providedInterfaces_.push_back(interface);
        } else {
            requiredInterfaces_.push_back(interface);
        }
    }

    void addSubcomponent(std::shared_ptr<Component> component) {
        subcomponents_.push_back(component);
    }

    const std::vector<std::shared_ptr<Port>>& getPorts() const {
        return ports_;
    }

    const std::vector<std::shared_ptr<Interface>>& getProvidedInterfaces() const {
        return providedInterfaces_;
    }

    const std::vector<std::shared_ptr<Interface>>& getRequiredInterfaces() const {
        return requiredInterfaces_;
    }

    const std::vector<std::shared_ptr<Component>>& getSubcomponents() const {
        return subcomponents_;
    }

private:
    std::vector<std::shared_ptr<Port>> ports_;
    std::vector<std::shared_ptr<Interface>> providedInterfaces_;
    std::vector<std::shared_ptr<Interface>> requiredInterfaces_;
    std::vector<std::shared_ptr<Component>> subcomponents_;
};

class Connector : public Element {
public:
    enum class Type {
        ASSEMBLY,    // Connects required to provided interfaces
        DELEGATION   // Connects external to internal ports
    };

    Connector(const std::string& name,
             std::shared_ptr<Port> source,
             std::shared_ptr<Port> target,
             Type type)
        : Element(name, ElementType::RELATIONSHIP),
          source_(source),
          target_(target),
          type_(type) {}

    std::shared_ptr<Port> getSource() const { return source_; }
    std::shared_ptr<Port> getTarget() const { return target_; }
    Type getType() const { return type_; }

private:
    std::shared_ptr<Port> source_;
    std::shared_ptr<Port> target_;
    Type type_;
};

class ComponentDiagram : public Diagram {
public:
    ComponentDiagram(const std::string& name)
        : Diagram(name, DiagramType::COMPONENT) {}

    void addComponent(std::shared_ptr<Component> component) {
        components_.push_back(component);
        addElement(component);
    }

    void addConnector(std::shared_ptr<Connector> connector) {
        connectors_.push_back(connector);
        addElement(connector);
    }

    const std::vector<std::shared_ptr<Component>>& getComponents() const {
        return components_;
    }

    const std::vector<std::shared_ptr<Connector>>& getConnectors() const {
        return connectors_;
    }

private:
    std::vector<std::shared_ptr<Component>> components_;
    std::vector<std::shared_ptr<Connector>> connectors_;
};

} // namespace uml
