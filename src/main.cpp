#include "authorization/AutomatedBot.hpp"
#include "environmental/air_processing.hpp"
#include "automation/automation_bot.hpp"
#include <iostream>

int main() {
    try {
        // Initialize environmental control
        evehicle::environmental::AirProcessor airProcessor;
        airProcessor.initialize(evehicle::environmental::AirProcessorConfig::getDefaultConfig());
        airProcessor.startProcessing();

        // Initialize automation system
        AutomationBot automationBot;
        
        // Initialize authorization system
        ja::auth::AutomatedBot authBot;

        std::cout << "Eco Vehicle System Initialized\n";
        std::cout << "Air Quality Index: " << airProcessor.getAirQualityIndex() << "\n";
        std::cout << "System Efficiency: " << airProcessor.getEfficiency() << "%\n";

        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}
