#pragma once

#include "Diagram.hpp"
#include "ComponentDiagram.hpp"
#include <memory>
#include <vector>
#include <string>
#include <map>

namespace uml {

class Node : public Element {
public:
    enum class Type {
        DEVICE,
        EXECUTION_ENVIRONMENT,
        NODE
    };

    Node(const std::string& name, Type type)
        : Element(name, ElementType::COMPONENT),
          type_(type) {}

    void addProperty(const std::string& key, const std::string& value) {
        properties_[key] = value;
    }

    void addComponent(std::shared_ptr<Component> component) {
        deployedComponents_.push_back(component);
    }

    Type getNodeType() const { return type_; }
    const std::map<std::string, std::string>& getProperties() const { return properties_; }
    const std::vector<std::shared_ptr<Component>>& getDeployedComponents() const {
        return deployedComponents_;
    }

private:
    Type type_;
    std::map<std::string, std::string> properties_;
    std::vector<std::shared_ptr<Component>> deployedComponents_;
};

class CommunicationPath : public Element {
public:
    CommunicationPath(const std::string& name,
                     std::shared_ptr<Node> source,
                     std::shared_ptr<Node> target)
        : Element(name, ElementType::RELATIONSHIP),
          source_(source),
          target_(target) {}

    void addProtocol(const std::string& protocol) {
        protocols_.push_back(protocol);
    }

    void setBandwidth(const std::string& bandwidth) {
        bandwidth_ = bandwidth;
    }

    std::shared_ptr<Node> getSource() const { return source_; }
    std::shared_ptr<Node> getTarget() const { return target_; }
    const std::vector<std::string>& getProtocols() const { return protocols_; }
    const std::string& getBandwidth() const { return bandwidth_; }

private:
    std::shared_ptr<Node> source_;
    std::shared_ptr<Node> target_;
    std::vector<std::string> protocols_;
    std::string bandwidth_;
};

class Artifact : public Element {
public:
    Artifact(const std::string& name)
        : Element(name, ElementType::COMPONENT) {}

    void setFileName(const std::string& fileName) {
        fileName_ = fileName;
    }

    void setVersion(const std::string& version) {
        version_ = version;
    }

    const std::string& getFileName() const { return fileName_; }
    const std::string& getVersion() const { return version_; }

private:
    std::string fileName_;
    std::string version_;
};

class DeploymentDiagram : public Diagram {
public:
    DeploymentDiagram(const std::string& name)
        : Diagram(name, DiagramType::DEPLOYMENT) {}

    void addNode(std::shared_ptr<Node> node) {
        nodes_.push_back(node);
        addElement(node);
    }

    void addCommunicationPath(std::shared_ptr<CommunicationPath> path) {
        paths_.push_back(path);
        addElement(path);
    }

    void addArtifact(std::shared_ptr<Artifact> artifact) {
        artifacts_.push_back(artifact);
        addElement(artifact);
    }

    const std::vector<std::shared_ptr<Node>>& getNodes() const {
        return nodes_;
    }

    const std::vector<std::shared_ptr<CommunicationPath>>& getPaths() const {
        return paths_;
    }

    const std::vector<std::shared_ptr<Artifact>>& getArtifacts() const {
        return artifacts_;
    }

private:
    std::vector<std::shared_ptr<Node>> nodes_;
    std::vector<std::shared_ptr<CommunicationPath>> paths_;
    std::vector<std::shared_ptr<Artifact>> artifacts_;
};

} // namespace uml
