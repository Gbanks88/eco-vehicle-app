#pragma once

#include "ModelBase.hpp"
#include <nlohmann/json.hpp>
#include <fstream>
#include <sstream>

namespace uml {

using json = nlohmann::json;

class Serializer {
public:
    static void saveDiagramToJson(const std::shared_ptr<Diagram>& diagram, const std::filesystem::path& path) {
        json j;
        j["name"] = diagram->getName();
        j["type"] = static_cast<int>(diagram->getType());
        j["description"] = diagram->getDescription();

        // Serialize elements
        json elements = json::array();
        for (const auto& [name, element] : diagram->getElements()) {
            elements.push_back(serializeElement(element));
        }
        j["elements"] = elements;

        // Serialize relationships
        json relationships = json::array();
        for (const auto& rel : diagram->getRelationships()) {
            relationships.push_back(serializeRelationship(rel));
        }
        j["relationships"] = relationships;

        // Write to file
        std::ofstream file(path);
        file << j.dump(4);
    }

    static std::shared_ptr<Diagram> loadDiagramFromJson(const std::filesystem::path& path) {
        std::ifstream file(path);
        json j;
        file >> j;

        auto diagram = std::make_shared<Diagram>(
            j["name"].get<std::string>(),
            static_cast<DiagramType>(j["type"].get<int>())
        );
        diagram->setDescription(j["description"].get<std::string>());

        // Load elements
        std::map<std::string, std::shared_ptr<Element>> elementMap;
        for (const auto& elementJson : j["elements"]) {
            auto element = deserializeElement(elementJson);
            elementMap[element->getName()] = element;
            diagram->addElement(element);
        }

        // Load relationships
        for (const auto& relJson : j["relationships"]) {
            auto relationship = deserializeRelationship(relJson, elementMap);
            diagram->addRelationship(relationship);
        }

        return diagram;
    }

private:
    static json serializeElement(const std::shared_ptr<Element>& element) {
        json j;
        j["name"] = element->getName();
        j["type"] = static_cast<int>(element->getType());
        j["description"] = element->getDescription();

        if (element->getType() == ElementType::CLASS) {
            auto classPtr = std::static_pointer_cast<Class>(element);
            
            json attributes = json::array();
            for (const auto& attr : classPtr->getAttributes()) {
                json attrJson;
                attrJson["name"] = attr->getName();
                attrJson["type"] = attr->getDataType();
                attrJson["isStatic"] = attr->isStatic();
                attributes.push_back(attrJson);
            }
            j["attributes"] = attributes;

            json methods = json::array();
            for (const auto& method : classPtr->getMethods()) {
                json methodJson;
                methodJson["name"] = method->getName();
                methodJson["returnType"] = method->getReturnType();
                
                json params = json::object();
                for (const auto& [paramName, paramType] : method->getParameters()) {
                    params[paramName] = paramType;
                }
                methodJson["parameters"] = params;
                methods.push_back(methodJson);
            }
            j["methods"] = methods;
        }

        return j;
    }

    static std::shared_ptr<Element> deserializeElement(const json& j) {
        auto type = static_cast<ElementType>(j["type"].get<int>());
        
        if (type == ElementType::CLASS) {
            auto classPtr = std::make_shared<Class>(j["name"].get<std::string>());
            classPtr->setDescription(j["description"].get<std::string>());

            // Load attributes
            for (const auto& attrJson : j["attributes"]) {
                auto attr = std::make_shared<Attribute>(
                    attrJson["name"].get<std::string>(),
                    attrJson["type"].get<std::string>(),
                    attrJson["isStatic"].get<bool>()
                );
                classPtr->addAttribute(attr);
            }

            // Load methods
            for (const auto& methodJson : j["methods"]) {
                auto method = std::make_shared<Method>(
                    methodJson["name"].get<std::string>(),
                    methodJson["returnType"].get<std::string>()
                );
                
                for (const auto& [paramName, paramType] : methodJson["parameters"].items()) {
                    method->addParameter(paramName, paramType);
                }
                classPtr->addMethod(method);
            }

            return classPtr;
        }

        return nullptr;
    }

    static json serializeRelationship(const std::shared_ptr<Relationship>& rel) {
        json j;
        j["name"] = rel->getName();
        j["type"] = static_cast<int>(rel->getRelationType());
        j["source"] = rel->getSource()->getName();
        j["target"] = rel->getTarget()->getName();
        j["multiplicitySource"] = rel->getMultiplicitySource();
        j["multiplicityTarget"] = rel->getMultiplicityTarget();
        return j;
    }

    static std::shared_ptr<Relationship> deserializeRelationship(
        const json& j,
        const std::map<std::string, std::shared_ptr<Element>>& elementMap) {
        
        auto source = elementMap.at(j["source"].get<std::string>());
        auto target = elementMap.at(j["target"].get<std::string>());
        
        auto rel = std::make_shared<Relationship>(
            j["name"].get<std::string>(),
            source,
            target,
            static_cast<RelationType>(j["type"].get<int>())
        );
        
        rel->setMultiplicitySource(j["multiplicitySource"].get<std::string>());
        rel->setMultiplicityTarget(j["multiplicityTarget"].get<std::string>());
        
        return rel;
    }
};

} // namespace uml
