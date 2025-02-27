#include "ModelBase.hpp"
#include <iostream>

using namespace uml;

int main() {
    // Get the model base instance
    auto& modelBase = ModelBase::getInstance();

    // Create a new class diagram
    modelBase.createDiagram("BankingSystem", DiagramType::CLASS);
    auto diagram = modelBase.getDiagram("BankingSystem");

    // Create Account class
    auto account = std::make_shared<Class>("Account");
    
    // Add attributes to Account
    account->addAttribute(std::make_shared<Attribute>("accountNumber", "string"));
    account->addAttribute(std::make_shared<Attribute>("balance", "double"));
    account->addAttribute(std::make_shared<Attribute>("accountType", "string"));

    // Add methods to Account
    auto deposit = std::make_shared<Method>("deposit", "void");
    deposit->addParameter("amount", "double");
    account->addMethod(deposit);

    auto withdraw = std::make_shared<Method>("withdraw", "bool");
    withdraw->addParameter("amount", "double");
    account->addMethod(withdraw);

    // Create Customer class
    auto customer = std::make_shared<Class>("Customer");
    
    // Add attributes to Customer
    customer->addAttribute(std::make_shared<Attribute>("name", "string"));
    customer->addAttribute(std::make_shared<Attribute>("address", "string"));
    customer->addAttribute(std::make_shared<Attribute>("phoneNumber", "string"));

    // Add classes to diagram
    diagram->addElement(account);
    diagram->addElement(customer);

    // Create relationship between Customer and Account
    auto relationship = std::make_shared<Relationship>(
        "CustomerAccounts",
        customer,
        account,
        RelationType::AGGREGATION
    );
    relationship->setMultiplicitySource("1");
    relationship->setMultiplicityTarget("1..*");

    // Add relationship to diagram
    diagram->addRelationship(relationship);

    // Print diagram information
    std::cout << "Diagram: " << diagram->getName() << "\n\n";

    // Print classes
    for (const auto& [name, element] : diagram->getElements()) {
        if (element->getType() == ElementType::CLASS) {
            auto classPtr = std::static_pointer_cast<Class>(element);
            std::cout << "Class: " << classPtr->getName() << "\n";
            
            std::cout << "Attributes:\n";
            for (const auto& attr : classPtr->getAttributes()) {
                std::cout << "  - " << attr->getName() << ": " << attr->getDataType() << "\n";
            }

            std::cout << "Methods:\n";
            for (const auto& method : classPtr->getMethods()) {
                std::cout << "  - " << method->getName() << "(" ;
                bool first = true;
                for (const auto& [paramName, paramType] : method->getParameters()) {
                    if (!first) std::cout << ", ";
                    std::cout << paramType << " " << paramName;
                    first = false;
                }
                std::cout << ") : " << method->getReturnType() << "\n";
            }
            std::cout << "\n";
        }
    }

    // Print relationships
    std::cout << "Relationships:\n";
    for (const auto& rel : diagram->getRelationships()) {
        std::cout << rel->getSource()->getName() << " --("
                 << rel->getMultiplicitySource() << ")---> ("
                 << rel->getMultiplicityTarget() << ") "
                 << rel->getTarget()->getName() << "\n";
    }

    return 0;
}
