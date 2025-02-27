#pragma once

#include "Diagram.hpp"
#include "ComponentDiagram.hpp"
#include "DeploymentDiagram.hpp"
#include "ActivityDiagram.hpp"
#include "StateMachine.hpp"
#include "SequenceDiagram.hpp"
#include <sstream>
#include <string>
#include <memory>
#include <map>

namespace uml {

class DocumentationGenerator {
public:
    enum class Format {
        MARKDOWN,
        HTML,
        LATEX
    };

    static std::string generateDocumentation(const std::shared_ptr<Diagram>& diagram,
                                           Format format) {
        switch (format) {
            case Format::MARKDOWN:
                return generateMarkdown(diagram);
            case Format::HTML:
                return generateHtml(diagram);
            case Format::LATEX:
                return generateLatex(diagram);
            default:
                return "";
        }
    }

private:
    static std::string generateMarkdown(const std::shared_ptr<Diagram>& diagram) {
        std::stringstream ss;
        
        // Title
        ss << "# " << diagram->getName() << "\n\n";
        
        // Description
        if (!diagram->getDescription().empty()) {
            ss << diagram->getDescription() << "\n\n";
        }

        // Generate diagram-specific documentation
        switch (diagram->getType()) {
            case DiagramType::CLASS:
                generateClassDiagramMd(diagram, ss);
                break;
            case DiagramType::COMPONENT:
                generateComponentDiagramMd(std::static_pointer_cast<ComponentDiagram>(diagram), ss);
                break;
            case DiagramType::DEPLOYMENT:
                generateDeploymentDiagramMd(std::static_pointer_cast<DeploymentDiagram>(diagram), ss);
                break;
            case DiagramType::ACTIVITY:
                generateActivityDiagramMd(std::static_pointer_cast<ActivityDiagram>(diagram), ss);
                break;
            case DiagramType::STATE_MACHINE:
                generateStateMachineMd(std::static_pointer_cast<StateMachine>(diagram), ss);
                break;
            case DiagramType::SEQUENCE:
                generateSequenceDiagramMd(std::static_pointer_cast<SequenceDiagram>(diagram), ss);
                break;
            default:
                break;
        }

        return ss.str();
    }

    static void generateClassDiagramMd(const std::shared_ptr<Diagram>& diagram,
                                     std::stringstream& ss) {
        ss << "## Classes\n\n";
        
        for (const auto& [name, element] : diagram->getElements()) {
            if (element->getType() == ElementType::CLASS) {
                auto classPtr = std::static_pointer_cast<Class>(element);
                
                ss << "### " << classPtr->getName() << "\n\n";
                
                // Attributes
                if (!classPtr->getAttributes().empty()) {
                    ss << "#### Attributes\n\n";
                    ss << "| Name | Type | Description |\n";
                    ss << "|------|------|-------------|\n";
                    for (const auto& attr : classPtr->getAttributes()) {
                        ss << "| " << attr->getName() << " | "
                           << attr->getDataType() << " | "
                           << attr->getDescription() << " |\n";
                    }
                    ss << "\n";
                }

                // Methods
                if (!classPtr->getMethods().empty()) {
                    ss << "#### Methods\n\n";
                    ss << "| Name | Return Type | Parameters | Description |\n";
                    ss << "|------|-------------|------------|-------------|\n";
                    for (const auto& method : classPtr->getMethods()) {
                        ss << "| " << method->getName() << " | "
                           << method->getReturnType() << " | ";
                        
                        // Parameters
                        bool first = true;
                        for (const auto& [paramName, paramType] : method->getParameters()) {
                            if (!first) ss << ", ";
                            ss << paramType << " " << paramName;
                            first = false;
                        }
                        
                        ss << " | " << method->getDescription() << " |\n";
                    }
                    ss << "\n";
                }
            }
        }
    }

    static void generateComponentDiagramMd(const std::shared_ptr<ComponentDiagram>& diagram,
                                         std::stringstream& ss) {
        ss << "## Components\n\n";
        
        for (const auto& component : diagram->getComponents()) {
            ss << "### " << component->getName() << "\n\n";
            
            // Provided Interfaces
            if (!component->getProvidedInterfaces().empty()) {
                ss << "#### Provided Interfaces\n\n";
                for (const auto& interface : component->getProvidedInterfaces()) {
                    ss << "- " << interface->getName() << "\n";
                    for (const auto& [opName, opDetails] : interface->getOperations()) {
                        ss << "  - " << opDetails.first << " " << opName << "(";
                        bool first = true;
                        for (const auto& param : opDetails.second) {
                            if (!first) ss << ", ";
                            ss << param.second << " " << param.first;
                            first = false;
                        }
                        ss << ")\n";
                    }
                }
                ss << "\n";
            }

            // Required Interfaces
            if (!component->getRequiredInterfaces().empty()) {
                ss << "#### Required Interfaces\n\n";
                for (const auto& interface : component->getRequiredInterfaces()) {
                    ss << "- " << interface->getName() << "\n";
                }
                ss << "\n";
            }
        }
    }

    static void generateDeploymentDiagramMd(const std::shared_ptr<DeploymentDiagram>& diagram,
                                          std::stringstream& ss) {
        ss << "## Deployment Structure\n\n";
        
        // Nodes
        ss << "### Nodes\n\n";
        for (const auto& node : diagram->getNodes()) {
            ss << "#### " << node->getName() << "\n\n";
            
            // Properties
            if (!node->getProperties().empty()) {
                ss << "Properties:\n\n";
                for (const auto& [key, value] : node->getProperties()) {
                    ss << "- " << key << ": " << value << "\n";
                }
                ss << "\n";
            }

            // Deployed Components
            if (!node->getDeployedComponents().empty()) {
                ss << "Deployed Components:\n\n";
                for (const auto& component : node->getDeployedComponents()) {
                    ss << "- " << component->getName() << "\n";
                }
                ss << "\n";
            }
        }

        // Communication Paths
        ss << "### Communication Paths\n\n";
        for (const auto& path : diagram->getPaths()) {
            ss << "- " << path->getSource()->getName() << " → "
               << path->getTarget()->getName() << "\n";
            if (!path->getProtocols().empty()) {
                ss << "  - Protocols: " << join(path->getProtocols(), ", ") << "\n";
            }
            if (!path->getBandwidth().empty()) {
                ss << "  - Bandwidth: " << path->getBandwidth() << "\n";
            }
        }
        ss << "\n";
    }

    static void generateActivityDiagramMd(const std::shared_ptr<ActivityDiagram>& diagram,
                                        std::stringstream& ss) {
        ss << "## Activity Flow\n\n";
        
        // Partitions
        for (const auto& partition : diagram->getPartitions()) {
            ss << "### " << partition->getName() << "\n\n";
            ss << "Activities:\n";
            for (const auto& node : partition->getNodes()) {
                ss << "- " << node->getName() << "\n";
            }
            ss << "\n";
        }

        // Edges
        ss << "### Flow Transitions\n\n";
        for (const auto& edge : diagram->getEdges()) {
            ss << "- " << edge->getSource()->getName() << " → "
               << edge->getTarget()->getName();
            if (!edge->getGuard().empty()) {
                ss << " [" << edge->getGuard() << "]";
            }
            ss << "\n";
        }
        ss << "\n";
    }

    static void generateStateMachineMd(const std::shared_ptr<StateMachine>& diagram,
                                     std::stringstream& ss) {
        ss << "## States and Transitions\n\n";
        
        // States
        for (const auto& state : diagram->getStates()) {
            ss << "### " << state->getName();
            if (state->isInitial()) ss << " (Initial)";
            if (state->isFinal()) ss << " (Final)";
            ss << "\n\n";

            if (!state->getEntryActions().empty()) {
                ss << "Entry Actions:\n";
                for (const auto& action : state->getEntryActions()) {
                    ss << "- " << action << "\n";
                }
                ss << "\n";
            }

            if (!state->getDoActivities().empty()) {
                ss << "Do Activities:\n";
                for (const auto& activity : state->getDoActivities()) {
                    ss << "- " << activity << "\n";
                }
                ss << "\n";
            }

            if (!state->getExitActions().empty()) {
                ss << "Exit Actions:\n";
                for (const auto& action : state->getExitActions()) {
                    ss << "- " << action << "\n";
                }
                ss << "\n";
            }
        }

        // Transitions
        ss << "### Transitions\n\n";
        for (const auto& transition : diagram->getTransitions()) {
            ss << "- " << transition->getSource()->getName() << " → "
               << transition->getTarget()->getName() << "\n";
            ss << "  - Trigger: " << transition->getTrigger() << "\n";
            if (!transition->getGuard().empty()) {
                ss << "  - Guard: " << transition->getGuard() << "\n";
            }
            ss << "  - Effect: " << transition->getEffect() << "\n\n";
        }
    }

    static void generateSequenceDiagramMd(const std::shared_ptr<SequenceDiagram>& diagram,
                                        std::stringstream& ss) {
        ss << "## Sequence Flow\n\n";
        
        // Lifelines
        ss << "### Participants\n\n";
        for (const auto& lifeline : diagram->getLifelines()) {
            ss << "- " << lifeline->getName();
            if (lifeline->isActor()) ss << " (Actor)";
            ss << "\n";
        }
        ss << "\n";

        // Messages
        ss << "### Messages\n\n";
        for (const auto& message : diagram->getMessages()) {
            ss << message->getSequenceNumber() << ". "
               << message->getSource()->getName() << " → "
               << message->getTarget()->getName() << ": "
               << message->getName();
            if (!message->getGuard().empty()) {
                ss << " [" << message->getGuard() << "]";
            }
            ss << "\n";
        }
        ss << "\n";

        // Combined Fragments
        if (!diagram->getFragments().empty()) {
            ss << "### Combined Fragments\n\n";
            for (const auto& fragment : diagram->getFragments()) {
                ss << "- " << fragment->getName() << " (";
                switch (fragment->getOperatorType()) {
                    case CombinedFragment::OperatorType::ALT:
                        ss << "Alternative";
                        break;
                    case CombinedFragment::OperatorType::OPT:
                        ss << "Optional";
                        break;
                    case CombinedFragment::OperatorType::LOOP:
                        ss << "Loop";
                        break;
                    default:
                        ss << "Other";
                }
                ss << ")\n";
                
                ss << "  Operands:\n";
                for (const auto& operand : fragment->getOperands()) {
                    ss << "  - " << operand << "\n";
                }
                ss << "\n";
            }
        }
    }

    static std::string generateHtml(const std::shared_ptr<Diagram>& diagram) {
        // TODO: Implement HTML documentation generation
        return "";
    }

    static std::string generateLatex(const std::shared_ptr<Diagram>& diagram) {
        // TODO: Implement LaTeX documentation generation
        return "";
    }

    static std::string join(const std::vector<std::string>& items,
                           const std::string& delimiter) {
        std::stringstream ss;
        bool first = true;
        for (const auto& item : items) {
            if (!first) ss << delimiter;
            ss << item;
            first = false;
        }
        return ss.str();
    }
};

} // namespace uml
