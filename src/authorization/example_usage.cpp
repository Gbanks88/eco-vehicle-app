#include "AuthorizationSystem.hpp"
#include "LearningRule.hpp"
#include <iostream>
#include <thread>
#include <chrono>

using namespace ja::auth;
using namespace std::chrono_literals;

void printDecision(const std::string& requestType, bool approved) {
    std::cout << requestType << ": " << (approved ? "APPROVED" : "DENIED") << "\n";
}

int main() {
    // Get the authorization system instance
    auto& auth = AuthorizationSystem::getInstance();

    // Create user context with high privileges
    UserContext context("bot_user", 4);
    context.addPermission("file_access");
    context.addPermission("system_mod");
    context.addPermission("config_change");
    context.addPermission("security_override");
    
    // Set the context
    auth.setUserContext(context);

    // Add automated rules
    auth.addAutomatedRule(std::make_shared<FileAccessRule>());
    auth.addAutomatedRule(std::make_shared<SystemModRule>());
    auth.addAutomatedRule(std::make_shared<LearningRule>());

    // First round of requests
    std::cout << "First round - Initial decisions:\n";
    
    // File access request
    Request fileRequest("req_001", RequestType::FILE_ACCESS);
    fileRequest.addData("path", std::string("/path/to/file.txt"));
    printDecision("File Access", auth.authorize(fileRequest));

    // System modification request
    Request sysRequest("req_002", RequestType::SYSTEM_MODIFICATION);
    sysRequest.addData("component", std::string("network"));
    sysRequest.addData("action", std::string("restart"));
    printDecision("System Modification", auth.authorize(sysRequest));

    // Configuration change request
    Request configRequest("req_003", RequestType::CONFIGURATION_CHANGE);
    configRequest.addData("setting", std::string("timeout"));
    configRequest.addData("value", std::string("300"));
    printDecision("Configuration Change", auth.authorize(configRequest));

    // Wait a moment to simulate time passing
    std::this_thread::sleep_for(1s);

    // Second round - Same requests should be auto-approved
    std::cout << "\nSecond round - Auto-approvals based on history:\n";
    
    // Same file access request
    Request fileRequest2("req_004", RequestType::FILE_ACCESS);
    fileRequest2.addData("path", std::string("/path/to/file.txt"));
    printDecision("File Access", auth.authorize(fileRequest2));

    // Similar system modification
    Request sysRequest2("req_005", RequestType::SYSTEM_MODIFICATION);
    sysRequest2.addData("component", std::string("network"));
    sysRequest2.addData("action", std::string("restart"));
    printDecision("System Modification", auth.authorize(sysRequest2));

    // Similar configuration change
    Request configRequest2("req_006", RequestType::CONFIGURATION_CHANGE);
    configRequest2.addData("setting", std::string("timeout"));
    configRequest2.addData("value", std::string("600")); // Different value, but similar pattern
    printDecision("Configuration Change", auth.authorize(configRequest2));

    std::cout << "\nNote: Second round requests were processed using historical decisions\n";
    
    return 0;
}
