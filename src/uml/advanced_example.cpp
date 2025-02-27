#include "ActivityDiagram.hpp"
#include "StateMachine.hpp"
#include "CodeGenerator.hpp"
#include "Serializer.hpp"
#include <iostream>

using namespace uml;

void createAndShowActivityDiagram() {
    // Create an activity diagram for order processing
    auto diagram = std::make_shared<ActivityDiagram>("OrderProcessing");

    // Create nodes
    auto start = std::make_shared<ActivityNode>("Start", ActivityNodeType::INITIAL);
    auto receiveOrder = std::make_shared<ActivityNode>("Receive Order", ActivityNodeType::ACTION);
    auto validateOrder = std::make_shared<ActivityNode>("Validate Order", ActivityNodeType::ACTION);
    auto checkStock = std::make_shared<ActivityNode>("Check Stock", ActivityNodeType::DECISION);
    auto processPayment = std::make_shared<ActivityNode>("Process Payment", ActivityNodeType::ACTION);
    auto shipOrder = std::make_shared<ActivityNode>("Ship Order", ActivityNodeType::ACTION);
    auto notifyCustomer = std::make_shared<ActivityNode>("Notify Customer", ActivityNodeType::ACTION);
    auto end = std::make_shared<ActivityNode>("End", ActivityNodeType::FINAL);

    // Add nodes to diagram
    diagram->addNode(start);
    diagram->addNode(receiveOrder);
    diagram->addNode(validateOrder);
    diagram->addNode(checkStock);
    diagram->addNode(processPayment);
    diagram->addNode(shipOrder);
    diagram->addNode(notifyCustomer);
    diagram->addNode(end);

    // Create edges
    auto edge1 = std::make_shared<ActivityEdge>("", start, receiveOrder);
    auto edge2 = std::make_shared<ActivityEdge>("", receiveOrder, validateOrder);
    auto edge3 = std::make_shared<ActivityEdge>("", validateOrder, checkStock);
    auto edge4 = std::make_shared<ActivityEdge>("", checkStock, processPayment);
    edge4->setGuard("In Stock");
    auto edge5 = std::make_shared<ActivityEdge>("", processPayment, shipOrder);
    auto edge6 = std::make_shared<ActivityEdge>("", shipOrder, notifyCustomer);
    auto edge7 = std::make_shared<ActivityEdge>("", notifyCustomer, end);

    // Add edges to diagram
    diagram->addEdge(edge1);
    diagram->addEdge(edge2);
    diagram->addEdge(edge3);
    diagram->addEdge(edge4);
    diagram->addEdge(edge5);
    diagram->addEdge(edge6);
    diagram->addEdge(edge7);

    // Create partitions
    auto customerPartition = std::make_shared<ActivityPartition>("Customer");
    auto systemPartition = std::make_shared<ActivityPartition>("System");
    auto warehousePartition = std::make_shared<ActivityPartition>("Warehouse");

    // Add nodes to partitions
    customerPartition->addNode(receiveOrder);
    systemPartition->addNode(validateOrder);
    systemPartition->addNode(processPayment);
    warehousePartition->addNode(checkStock);
    warehousePartition->addNode(shipOrder);
    systemPartition->addNode(notifyCustomer);

    // Add partitions to diagram
    diagram->addPartition(customerPartition);
    diagram->addPartition(systemPartition);
    diagram->addPartition(warehousePartition);

    // Print diagram information
    std::cout << "Activity Diagram: " << diagram->getName() << "\n\n";
    
    std::cout << "Partitions:\n";
    for (const auto& partition : diagram->getPartitions()) {
        std::cout << "- " << partition->getName() << "\n";
        std::cout << "  Nodes:\n";
        for (const auto& node : partition->getNodes()) {
            std::cout << "  - " << node->getName() << "\n";
        }
    }

    std::cout << "\nEdges:\n";
    for (const auto& edge : diagram->getEdges()) {
        std::cout << "- " << edge->getSource()->getName() << " -> "
                 << edge->getTarget()->getName();
        if (!edge->getGuard().empty()) {
            std::cout << " [" << edge->getGuard() << "]";
        }
        std::cout << "\n";
    }
}

void createAndShowStateMachine() {
    // Create a state machine for order status
    auto stateMachine = std::make_shared<StateMachine>("OrderStatus");

    // Create states
    auto pending = std::make_shared<State>("Pending");
    pending->setInitial(true);
    pending->addEntryAction("Log order received");
    pending->addDoActivity("Validate order details");

    auto processing = std::make_shared<State>("Processing");
    processing->addEntryAction("Start processing timer");
    processing->addDoActivity("Process payment");
    processing->addExitAction("Stop processing timer");

    auto shipped = std::make_shared<State>("Shipped");
    shipped->addEntryAction("Update inventory");
    shipped->addDoActivity("Track shipment");

    auto delivered = std::make_shared<State>("Delivered");
    delivered->setFinal(true);
    delivered->addEntryAction("Send confirmation email");

    // Add states to state machine
    stateMachine->addState(pending);
    stateMachine->addState(processing);
    stateMachine->addState(shipped);
    stateMachine->addState(delivered);

    // Create transitions
    auto t1 = std::make_shared<Transition>("ValidateOrder", pending, processing);
    t1->setTrigger("orderValidated");
    t1->setGuard("isValid");
    t1->setEffect("startProcessing");

    auto t2 = std::make_shared<Transition>("ShipOrder", processing, shipped);
    t2->setTrigger("paymentConfirmed");
    t2->setEffect("initiateShipment");

    auto t3 = std::make_shared<Transition>("DeliverOrder", shipped, delivered);
    t3->setTrigger("deliveryConfirmed");
    t3->setEffect("closeOrder");

    // Add transitions to state machine
    stateMachine->addTransition(t1);
    stateMachine->addTransition(t2);
    stateMachine->addTransition(t3);

    // Print state machine information
    std::cout << "\nState Machine: " << stateMachine->getName() << "\n\n";

    std::cout << "States:\n";
    for (const auto& state : stateMachine->getStates()) {
        std::cout << "- " << state->getName();
        if (state->isInitial()) std::cout << " (Initial)";
        if (state->isFinal()) std::cout << " (Final)";
        std::cout << "\n";

        if (!state->getEntryActions().empty()) {
            std::cout << "  Entry Actions:\n";
            for (const auto& action : state->getEntryActions()) {
                std::cout << "  - " << action << "\n";
            }
        }

        if (!state->getDoActivities().empty()) {
            std::cout << "  Do Activities:\n";
            for (const auto& activity : state->getDoActivities()) {
                std::cout << "  - " << activity << "\n";
            }
        }

        if (!state->getExitActions().empty()) {
            std::cout << "  Exit Actions:\n";
            for (const auto& action : state->getExitActions()) {
                std::cout << "  - " << action << "\n";
            }
        }
    }

    std::cout << "\nTransitions:\n";
    for (const auto& transition : stateMachine->getTransitions()) {
        std::cout << "- " << transition->getSource()->getName() << " -> "
                 << transition->getTarget()->getName() << "\n";
        std::cout << "  Trigger: " << transition->getTrigger() << "\n";
        if (!transition->getGuard().empty()) {
            std::cout << "  Guard: " << transition->getGuard() << "\n";
        }
        std::cout << "  Effect: " << transition->getEffect() << "\n";
    }
}

void demonstrateCodeGeneration() {
    // Create a simple class diagram for code generation
    auto diagram = std::make_shared<Diagram>("OrderSystem", DiagramType::CLASS);

    // Create Order class
    auto orderClass = std::make_shared<Class>("Order");
    
    // Add attributes
    orderClass->addAttribute(std::make_shared<Attribute>("orderId", "string"));
    orderClass->addAttribute(std::make_shared<Attribute>("customerName", "string"));
    orderClass->addAttribute(std::make_shared<Attribute>("totalAmount", "double"));
    
    // Add methods
    auto processMethod = std::make_shared<Method>("processOrder", "bool");
    processMethod->addParameter("paymentMethod", "string");
    orderClass->addMethod(processMethod);

    auto calculateMethod = std::make_shared<Method>("calculateTotal", "double");
    orderClass->addMethod(calculateMethod);

    // Add class to diagram
    diagram->addElement(orderClass);

    // Generate C++ code
    std::cout << "\nGenerated C++ Code:\n";
    std::cout << "==================\n\n";
    std::cout << CodeGenerator::generateCode(diagram, CodeGenerator::Language::CPP);
}

int main() {
    createAndShowActivityDiagram();
    createAndShowStateMachine();
    demonstrateCodeGeneration();
    return 0;
}
