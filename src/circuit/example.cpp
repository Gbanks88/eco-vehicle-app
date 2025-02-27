#include "CircuitAnalyzer.hpp"
#include <iostream>
#include <iomanip>

using namespace circuit;

void printVoltages(const std::vector<Complex>& voltages) {
    std::cout << std::fixed << std::setprecision(3);
    for (size_t i = 0; i < voltages.size(); i++) {
        std::cout << "Node " << i << ": " 
                 << std::abs(voltages[i]) << " V, " 
                 << std::arg(voltages[i]) * 180.0 / M_PI << " deg\n";
    }
}

int main() {
    // Create circuit analyzer
    CircuitAnalyzer analyzer;

    // Create components
    auto vs = std::make_shared<VoltageSource>("V1", 10.0);
    auto r1 = std::make_shared<Resistor>("R1", 1000.0);
    auto c1 = std::make_shared<Capacitor>("C1", 1e-6);
    auto r2 = std::make_shared<Resistor>("R2", 2000.0);

    // Add components to analyzer
    analyzer.addComponent(vs);
    analyzer.addComponent(r1);
    analyzer.addComponent(c1);
    analyzer.addComponent(r2);

    // Set ground node
    analyzer.setGroundNode(vs->getPins()[1]->getNode());

    // Perform DC analysis
    std::cout << "DC Analysis:\n";
    analyzer.analyze();
    printVoltages(analyzer.getNodeVoltages());

    // Perform AC analysis
    std::cout << "\nAC Analysis:\n";
    analyzer.performAC(1.0, 1e6, 10);
    auto freq_response = analyzer.getFrequencyResponse();
    
    for (const auto& [freq, voltages] : freq_response) {
        std::cout << "\nFrequency: " << freq << " Hz\n";
        printVoltages(voltages);
    }

    // Perform transient analysis
    std::cout << "\nTransient Analysis:\n";
    analyzer.performTransient(0.001, 1e-5);  // 1ms simulation with 10us steps
    printVoltages(analyzer.getNodeVoltages());

    return 0;
}
