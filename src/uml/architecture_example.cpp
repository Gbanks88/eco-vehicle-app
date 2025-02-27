#include "ComponentDiagram.hpp"
#include "DeploymentDiagram.hpp"
#include "DocumentationGenerator.hpp"
#include <iostream>
#include <fstream>

using namespace uml;

void createAndDocumentMicroservices() {
    // Create a component diagram for a microservices architecture
    auto diagram = std::make_shared<ComponentDiagram>("E-Commerce System");

    // Create interfaces
    auto orderInterface = std::make_shared<Interface>("IOrderService");
    orderInterface->addOperation("createOrder", "OrderId",
        {{"order", "OrderDetails"}});
    orderInterface->addOperation("getOrder", "Order",
        {{"orderId", "OrderId"}});

    auto paymentInterface = std::make_shared<Interface>("IPaymentService");
    paymentInterface->addOperation("processPayment", "PaymentResult",
        {{"orderId", "OrderId"}, {"amount", "Money"}});

    auto inventoryInterface = std::make_shared<Interface>("IInventoryService");
    inventoryInterface->addOperation("checkStock", "bool",
        {{"productId", "ProductId"}, {"quantity", "int"}});

    // Create components
    auto orderService = std::make_shared<Component>("OrderService");
    orderService->addInterface(orderInterface, true);  // Provided
    orderService->addInterface(paymentInterface, false);  // Required
    orderService->addInterface(inventoryInterface, false);  // Required

    auto paymentService = std::make_shared<Component>("PaymentService");
    paymentService->addInterface(paymentInterface, true);

    auto inventoryService = std::make_shared<Component>("InventoryService");
    inventoryService->addInterface(inventoryInterface, true);

    // Add components to diagram
    diagram->addComponent(orderService);
    diagram->addComponent(paymentService);
    diagram->addComponent(inventoryService);

    // Generate documentation
    std::cout << "Component Diagram Documentation:\n";
    std::cout << "===============================\n\n";
    std::cout << DocumentationGenerator::generateDocumentation(
        diagram, DocumentationGenerator::Format::MARKDOWN);

    // Create deployment diagram
    auto deployDiagram = std::make_shared<DeploymentDiagram>("E-Commerce Deployment");

    // Create nodes
    auto webServer = std::make_shared<Node>("Web Server", Node::Type::DEVICE);
    webServer->addProperty("OS", "Ubuntu 22.04");
    webServer->addProperty("RAM", "16GB");
    webServer->addProperty("CPU", "8 cores");

    auto appServer1 = std::make_shared<Node>("App Server 1", Node::Type::DEVICE);
    appServer1->addProperty("OS", "Ubuntu 22.04");
    appServer1->addProperty("RAM", "32GB");
    appServer1->addProperty("CPU", "16 cores");

    auto appServer2 = std::make_shared<Node>("App Server 2", Node::Type::DEVICE);
    appServer2->addProperty("OS", "Ubuntu 22.04");
    appServer2->addProperty("RAM", "32GB");
    appServer2->addProperty("CPU", "16 cores");

    auto database = std::make_shared<Node>("Database Server", Node::Type::DEVICE);
    database->addProperty("OS", "Ubuntu 22.04");
    database->addProperty("RAM", "64GB");
    database->addProperty("CPU", "32 cores");
    database->addProperty("Storage", "2TB SSD");

    // Deploy components
    appServer1->addComponent(orderService);
    appServer1->addComponent(paymentService);
    appServer2->addComponent(inventoryService);

    // Add nodes to diagram
    deployDiagram->addNode(webServer);
    deployDiagram->addNode(appServer1);
    deployDiagram->addNode(appServer2);
    deployDiagram->addNode(database);

    // Create communication paths
    auto path1 = std::make_shared<CommunicationPath>(
        "Web-App1", webServer, appServer1);
    path1->addProtocol("HTTPS");
    path1->setBandwidth("1Gbps");

    auto path2 = std::make_shared<CommunicationPath>(
        "Web-App2", webServer, appServer2);
    path2->addProtocol("HTTPS");
    path2->setBandwidth("1Gbps");

    auto path3 = std::make_shared<CommunicationPath>(
        "App1-DB", appServer1, database);
    path3->addProtocol("PostgreSQL");
    path3->setBandwidth("10Gbps");

    auto path4 = std::make_shared<CommunicationPath>(
        "App2-DB", appServer2, database);
    path4->addProtocol("PostgreSQL");
    path4->setBandwidth("10Gbps");

    // Add paths to diagram
    deployDiagram->addCommunicationPath(path1);
    deployDiagram->addCommunicationPath(path2);
    deployDiagram->addCommunicationPath(path3);
    deployDiagram->addCommunicationPath(path4);

    // Create artifacts
    auto orderArtifact = std::make_shared<Artifact>("OrderService.jar");
    orderArtifact->setVersion("1.0.0");
    auto paymentArtifact = std::make_shared<Artifact>("PaymentService.jar");
    paymentArtifact->setVersion("1.0.0");
    auto inventoryArtifact = std::make_shared<Artifact>("InventoryService.jar");
    inventoryArtifact->setVersion("1.0.0");

    // Add artifacts to diagram
    deployDiagram->addArtifact(orderArtifact);
    deployDiagram->addArtifact(paymentArtifact);
    deployDiagram->addArtifact(inventoryArtifact);

    // Generate documentation
    std::cout << "\nDeployment Diagram Documentation:\n";
    std::cout << "================================\n\n";
    std::cout << DocumentationGenerator::generateDocumentation(
        deployDiagram, DocumentationGenerator::Format::MARKDOWN);

    // Save documentation to files
    std::ofstream componentDoc("component_diagram.md");
    componentDoc << DocumentationGenerator::generateDocumentation(
        diagram, DocumentationGenerator::Format::MARKDOWN);
    componentDoc.close();

    std::ofstream deploymentDoc("deployment_diagram.md");
    deploymentDoc << DocumentationGenerator::generateDocumentation(
        deployDiagram, DocumentationGenerator::Format::MARKDOWN);
    deploymentDoc.close();
}

int main() {
    createAndDocumentMicroservices();
    return 0;
}
