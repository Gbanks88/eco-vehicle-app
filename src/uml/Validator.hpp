#pragma once

#include "Diagram.hpp"
#include <vector>
#include <string>

namespace uml {

struct ValidationError {
    std::string message;
    std::string elementName;
    std::string details;
};

class Validator {
public:
    static std::vector<ValidationError> validateDiagram(const std::shared_ptr<Diagram>& diagram) {
        std::vector<ValidationError> errors;
        
        // Check diagram name
        if (diagram->getName().empty()) {
            errors.push_back({"Diagram name cannot be empty", "", ""});
        }

        // Validate all elements
        for (const auto& [name, element] : diagram->getElements()) {
            validateElement(element, errors);
        }

        // Validate relationships
        for (const auto& rel : diagram->getRelationships()) {
            validateRelationship(rel, errors);
        }

        // Validate diagram-specific rules based on type
        switch (diagram->getType()) {
            case DiagramType::CLASS:
                validateClassDiagram(diagram, errors);
                break;
            case DiagramType::SEQUENCE:
                validateSequenceDiagram(diagram, errors);
                break;
            // Add more diagram type validations as needed
            default:
                break;
        }

        return errors;
    }

private:
    static void validateElement(const std::shared_ptr<Element>& element,
                              std::vector<ValidationError>& errors) {
        // Check element name
        if (element->getName().empty()) {
            errors.push_back({"Element name cannot be empty", "", ""});
            return;
        }

        // Validate based on element type
        switch (element->getType()) {
            case ElementType::CLASS:
                validateClass(std::static_pointer_cast<Class>(element), errors);
                break;
            // Add more element type validations as needed
            default:
                break;
        }
    }

    static void validateClass(const std::shared_ptr<Class>& classElement,
                            std::vector<ValidationError>& errors) {
        // Validate class name (should start with uppercase)
        if (!classElement->getName().empty() && 
            !std::isupper(classElement->getName()[0])) {
            errors.push_back({
                "Class name should start with uppercase letter",
                classElement->getName(),
                "Current name: " + classElement->getName()
            });
        }

        // Validate attributes
        for (const auto& attr : classElement->getAttributes()) {
            if (attr->getName().empty()) {
                errors.push_back({
                    "Attribute name cannot be empty",
                    classElement->getName(),
                    "Class: " + classElement->getName()
                });
            }
            if (attr->getDataType().empty()) {
                errors.push_back({
                    "Attribute type cannot be empty",
                    classElement->getName(),
                    "Attribute: " + attr->getName()
                });
            }
        }

        // Validate methods
        for (const auto& method : classElement->getMethods()) {
            if (method->getName().empty()) {
                errors.push_back({
                    "Method name cannot be empty",
                    classElement->getName(),
                    "Class: " + classElement->getName()
                });
            }
            // Check return type
            if (method->getReturnType().empty()) {
                errors.push_back({
                    "Method return type cannot be empty",
                    classElement->getName(),
                    "Method: " + method->getName()
                });
            }
            // Check parameters
            for (const auto& [paramName, paramType] : method->getParameters()) {
                if (paramName.empty() || paramType.empty()) {
                    errors.push_back({
                        "Method parameter name and type cannot be empty",
                        classElement->getName(),
                        "Method: " + method->getName()
                    });
                }
            }
        }
    }

    static void validateRelationship(const std::shared_ptr<Relationship>& rel,
                                   std::vector<ValidationError>& errors) {
        // Check if source and target exist
        if (!rel->getSource() || !rel->getTarget()) {
            errors.push_back({
                "Relationship source and target must exist",
                rel->getName(),
                "Relationship type: " + std::to_string(static_cast<int>(rel->getRelationType()))
            });
        }

        // Validate multiplicity format (if specified)
        validateMultiplicity(rel->getMultiplicitySource(), rel->getName(), errors);
        validateMultiplicity(rel->getMultiplicityTarget(), rel->getName(), errors);
    }

    static void validateMultiplicity(const std::string& mult,
                                   const std::string& relName,
                                   std::vector<ValidationError>& errors) {
        if (!mult.empty()) {
            // Check for valid multiplicity format (e.g., "1", "*", "0..1", "1..*")
            bool valid = false;
            if (mult == "1" || mult == "*" || mult == "0..1" || mult == "1..*") {
                valid = true;
            }
            // Add more multiplicity format checks as needed

            if (!valid) {
                errors.push_back({
                    "Invalid multiplicity format",
                    relName,
                    "Multiplicity: " + mult
                });
            }
        }
    }

    static void validateClassDiagram(const std::shared_ptr<Diagram>& diagram,
                                   std::vector<ValidationError>& errors) {
        // Check for at least one class
        bool hasClass = false;
        for (const auto& [name, element] : diagram->getElements()) {
            if (element->getType() == ElementType::CLASS) {
                hasClass = true;
                break;
            }
        }
        
        if (!hasClass) {
            errors.push_back({
                "Class diagram must contain at least one class",
                diagram->getName(),
                ""
            });
        }
    }

    static void validateSequenceDiagram(const std::shared_ptr<Diagram>& diagram,
                                      std::vector<ValidationError>& errors) {
        // Add sequence diagram specific validation
        // TODO: Implement sequence diagram validation
    }
};

} // namespace uml
