#include "SequenceDiagram.hpp"
#include "Serializer.hpp"
#include "Validator.hpp"
#include <iostream>

using namespace uml;

void printValidationErrors(const std::vector<ValidationError>& errors) {
    if (errors.empty()) {
        std::cout << "No validation errors found.\n";
        return;
    }

    std::cout << "Validation errors:\n";
    for (const auto& error : errors) {
        std::cout << "- " << error.message;
        if (!error.elementName.empty()) {
            std::cout << " (Element: " << error.elementName << ")";
        }
        if (!error.details.empty()) {
            std::cout << "\n  Details: " << error.details;
        }
        std::cout << "\n";
    }
}

int main() {
    // Create a sequence diagram for a login process
    auto diagram = std::make_shared<SequenceDiagram>("LoginProcess");
    
    // Create lifelines
    auto user = std::make_shared<Lifeline>("User");
    user->setActor(true);
    
    auto ui = std::make_shared<Lifeline>("LoginUI");
    auto auth = std::make_shared<Lifeline>("AuthService");
    auto db = std::make_shared<Lifeline>("Database");

    // Add lifelines to diagram
    diagram->addLifeline(user);
    diagram->addLifeline(ui);
    diagram->addLifeline(auth);
    diagram->addLifeline(db);

    // Create messages
    auto msg1 = std::make_shared<Message>(
        "enterCredentials",
        user,
        ui,
        MessageType::SYNCHRONOUS
    );
    msg1->setSequenceNumber(1);

    auto msg2 = std::make_shared<Message>(
        "validateCredentials",
        ui,
        auth,
        MessageType::SYNCHRONOUS
    );
    msg2->setSequenceNumber(2);

    auto msg3 = std::make_shared<Message>(
        "queryUser",
        auth,
        db,
        MessageType::SYNCHRONOUS
    );
    msg3->setSequenceNumber(3);

    auto msg4 = std::make_shared<Message>(
        "userData",
        db,
        auth,
        MessageType::REPLY
    );
    msg4->setSequenceNumber(4);

    // Create an alternative fragment for login success/failure
    auto altFragment = std::make_shared<CombinedFragment>(
        "LoginResult",
        CombinedFragment::OperatorType::ALT
    );
    altFragment->addOperand("credentials valid");
    altFragment->addOperand("credentials invalid");

    // Add messages and fragments to diagram
    diagram->addMessage(msg1);
    diagram->addMessage(msg2);
    diagram->addMessage(msg3);
    diagram->addMessage(msg4);
    diagram->addCombinedFragment(altFragment);

    // Validate the diagram
    auto errors = Validator::validateDiagram(diagram);
    printValidationErrors(errors);

    // Save the diagram to a file
    Serializer::saveDiagramToJson(diagram, "login_sequence.json");

    // Print diagram information
    std::cout << "\nSequence Diagram: " << diagram->getName() << "\n\n";

    std::cout << "Lifelines:\n";
    for (const auto& lifeline : diagram->getLifelines()) {
        std::cout << "- " << lifeline->getName()
                 << (lifeline->isActor() ? " (Actor)" : "") << "\n";
    }

    std::cout << "\nMessages:\n";
    for (const auto& msg : diagram->getMessages()) {
        std::cout << msg->getSequenceNumber() << ". "
                 << msg->getSource()->getName() << " -> "
                 << msg->getTarget()->getName() << ": "
                 << msg->getName() << "\n";
    }

    std::cout << "\nCombined Fragments:\n";
    for (const auto& fragment : diagram->getFragments()) {
        std::cout << "- " << fragment->getName() << " (";
        switch (fragment->getOperatorType()) {
            case CombinedFragment::OperatorType::ALT:
                std::cout << "Alternative";
                break;
            case CombinedFragment::OperatorType::OPT:
                std::cout << "Optional";
                break;
            case CombinedFragment::OperatorType::LOOP:
                std::cout << "Loop";
                break;
            default:
                std::cout << "Other";
        }
        std::cout << ")\n";
        
        std::cout << "  Operands:\n";
        for (const auto& operand : fragment->getOperands()) {
            std::cout << "  - " << operand << "\n";
        }
    }

    return 0;
}
