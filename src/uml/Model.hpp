#pragma once

#include <string>
#include <vector>
#include <memory>
#include <map>

namespace uml {

enum class ElementType {
    CLASS,
    INTERFACE,
    PACKAGE,
    RELATIONSHIP,
    ATTRIBUTE,
    METHOD,
    ENUM,
    COMPONENT
};

class Element {
public:
    Element(const std::string& name, ElementType type)
        : name_(name), type_(type) {}
    
    virtual ~Element() = default;

    const std::string& getName() const { return name_; }
    ElementType getType() const { return type_; }
    
    void setDescription(const std::string& desc) { description_ = desc; }
    const std::string& getDescription() const { return description_; }

protected:
    std::string name_;
    ElementType type_;
    std::string description_;
};

class Attribute : public Element {
public:
    Attribute(const std::string& name, const std::string& type, bool isStatic = false)
        : Element(name, ElementType::ATTRIBUTE), type_(type), isStatic_(isStatic) {}

    const std::string& getDataType() const { return type_; }
    bool isStatic() const { return isStatic_; }

private:
    std::string type_;
    bool isStatic_;
};

class Method : public Element {
public:
    Method(const std::string& name, const std::string& returnType)
        : Element(name, ElementType::METHOD), returnType_(returnType) {}

    void addParameter(const std::string& name, const std::string& type) {
        parameters_[name] = type;
    }

    const std::string& getReturnType() const { return returnType_; }
    const std::map<std::string, std::string>& getParameters() const { return parameters_; }

private:
    std::string returnType_;
    std::map<std::string, std::string> parameters_;
};

class Class : public Element {
public:
    Class(const std::string& name) : Element(name, ElementType::CLASS) {}

    void addAttribute(std::shared_ptr<Attribute> attr) {
        attributes_.push_back(attr);
    }

    void addMethod(std::shared_ptr<Method> method) {
        methods_.push_back(method);
    }

    const std::vector<std::shared_ptr<Attribute>>& getAttributes() const {
        return attributes_;
    }

    const std::vector<std::shared_ptr<Method>>& getMethods() const {
        return methods_;
    }

private:
    std::vector<std::shared_ptr<Attribute>> attributes_;
    std::vector<std::shared_ptr<Method>> methods_;
};

} // namespace uml
