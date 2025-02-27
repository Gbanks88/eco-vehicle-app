#pragma once

#include "Diagram.hpp"
#include "Model.hpp"
#include <string>
#include <sstream>
#include <memory>
#include <map>

namespace uml {

class CodeGenerator {
public:
    enum class Language {
        CPP,
        JAVA,
        PYTHON,
        TYPESCRIPT
    };

    static std::string generateCode(const std::shared_ptr<Diagram>& diagram,
                                  Language lang) {
        switch (lang) {
            case Language::CPP:
                return generateCpp(diagram);
            case Language::JAVA:
                return generateJava(diagram);
            case Language::PYTHON:
                return generatePython(diagram);
            case Language::TYPESCRIPT:
                return generateTypeScript(diagram);
            default:
                return "";
        }
    }

private:
    static std::string generateCpp(const std::shared_ptr<Diagram>& diagram) {
        std::stringstream ss;
        
        // Generate header guard
        ss << "#pragma once\n\n";
        
        // Add standard includes
        ss << "#include <string>\n";
        ss << "#include <vector>\n";
        ss << "#include <memory>\n\n";
        
        // Start namespace
        ss << "namespace " << toLower(diagram->getName()) << " {\n\n";
        
        // Generate classes
        for (const auto& [name, element] : diagram->getElements()) {
            if (element->getType() == ElementType::CLASS) {
                auto classPtr = std::static_pointer_cast<Class>(element);
                generateCppClass(classPtr, ss);
                ss << "\n";
            }
        }
        
        // End namespace
        ss << "} // namespace " << toLower(diagram->getName()) << "\n";
        
        return ss.str();
    }

    static void generateCppClass(const std::shared_ptr<Class>& classPtr,
                               std::stringstream& ss) {
        // Class declaration
        ss << "class " << classPtr->getName() << " {\n";
        ss << "public:\n";
        
        // Constructor
        ss << "    " << classPtr->getName() << "() = default;\n\n";
        
        // Generate getters and setters for attributes
        for (const auto& attr : classPtr->getAttributes()) {
            // Private member variable
            ss << "private:\n";
            ss << "    " << attr->getDataType() << " " << attr->getName() << "_;\n\n";
            
            // Public getter and setter
            ss << "public:\n";
            ss << "    const " << attr->getDataType() << "& get"
               << capitalize(attr->getName()) << "() const {\n";
            ss << "        return " << attr->getName() << "_;\n";
            ss << "    }\n\n";
            
            ss << "    void set" << capitalize(attr->getName())
               << "(const " << attr->getDataType() << "& value) {\n";
            ss << "        " << attr->getName() << "_ = value;\n";
            ss << "    }\n\n";
        }
        
        // Generate methods
        for (const auto& method : classPtr->getMethods()) {
            ss << "    " << method->getReturnType() << " "
               << method->getName() << "(";
            
            // Add parameters
            bool first = true;
            for (const auto& [paramName, paramType] : method->getParameters()) {
                if (!first) ss << ", ";
                ss << "const " << paramType << "& " << paramName;
                first = false;
            }
            
            ss << ") {\n";
            ss << "        // TODO: Implement " << method->getName() << "\n";
            ss << "    }\n\n";
        }
        
        ss << "};\n";
    }

    static std::string generateJava(const std::shared_ptr<Diagram>& diagram) {
        // TODO: Implement Java code generation
        return "";
    }

    static std::string generatePython(const std::shared_ptr<Diagram>& diagram) {
        // TODO: Implement Python code generation
        return "";
    }

    static std::string generateTypeScript(const std::shared_ptr<Diagram>& diagram) {
        // TODO: Implement TypeScript code generation
        return "";
    }

    static std::string toLower(const std::string& str) {
        std::string result = str;
        std::transform(result.begin(), result.end(), result.begin(), ::tolower);
        return result;
    }

    static std::string capitalize(const std::string& str) {
        if (str.empty()) return str;
        std::string result = str;
        result[0] = std::toupper(result[0]);
        return result;
    }
};

} // namespace uml
