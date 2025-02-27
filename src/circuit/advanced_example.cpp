#include "CircuitAnalyzer.hpp"
#include "AdvancedComponents.hpp"
#include "CircuitVisualizer.hpp"
#include <iostream>
#include <iomanip>

using namespace circuit;

int main() {
    // Create circuit analyzer
    CircuitAnalyzer analyzer;
    CircuitVisualizer visualizer(analyzer);

    // Example 1: Common-Emitter Amplifier
    std::cout << "Common-Emitter Amplifier Example:\n";
    {
        // Create components
        auto vcc = std::make_shared<VoltageSource>("VCC", 12.0);
        auto vin = std::make_shared<VoltageSource>("Vin", 0.1, 1000.0);  // 0.1V, 1kHz
        auto rc = std::make_shared<Resistor>("RC", 4700.0);
        auto re = std::make_shared<Resistor>("RE", 1000.0);
        auto r1 = std::make_shared<Resistor>("R1", 47000.0);
        auto r2 = std::make_shared<Resistor>("R2", 10000.0);
        auto ce = std::make_shared<Capacitor>("CE", 10e-6);
        auto cin = std::make_shared<Capacitor>("Cin", 1e-6);
        auto cout = std::make_shared<Capacitor>("Cout", 1e-6);
        auto q1 = std::make_shared<Transistor>("Q1", Transistor::Type::NPN);

        // Add components to analyzer
        analyzer.addComponent(vcc);
        analyzer.addComponent(vin);
        analyzer.addComponent(rc);
        analyzer.addComponent(re);
        analyzer.addComponent(r1);
        analyzer.addComponent(r2);
        analyzer.addComponent(ce);
        analyzer.addComponent(cin);
        analyzer.addComponent(cout);
        analyzer.addComponent(q1);

        // Set ground node
        analyzer.setGroundNode(vin->getPins()[1]->getNode());

        // Perform AC analysis
        analyzer.performAC(1.0, 1e6, 100);
        
        // Generate Bode plot
        visualizer.generateBodePlot("ce_amplifier", analyzer.getFrequencyResponse(), 1);
        
        // Generate netlist and schematic
        visualizer.generateNetlist("ce_amplifier.net");
        visualizer.generateSchematic("ce_amplifier.tex");
    }

    // Example 2: Crystal Oscillator
    std::cout << "\nCrystal Oscillator Example:\n";
    {
        // Create new analyzer for crystal oscillator
        CircuitAnalyzer osc_analyzer;
        
        // Create components
        auto vdd = std::make_shared<VoltageSource>("VDD", 5.0);
        auto xtal = std::make_shared<CrystalOscillator>("XTAL", 10e6);  // 10MHz
        auto rf = std::make_shared<Resistor>("RF", 1e6);
        auto r1 = std::make_shared<Resistor>("R1", 100e3);
        auto c1 = std::make_shared<Capacitor>("C1", 22e-12);
        auto c2 = std::make_shared<Capacitor>("C2", 22e-12);
        auto m1 = std::make_shared<MOSFET>("M1", MOSFET::Type::NMOS);

        // Add components
        osc_analyzer.addComponent(vdd);
        osc_analyzer.addComponent(xtal);
        osc_analyzer.addComponent(rf);
        osc_analyzer.addComponent(r1);
        osc_analyzer.addComponent(c1);
        osc_analyzer.addComponent(c2);
        osc_analyzer.addComponent(m1);

        // Set ground node
        osc_analyzer.setGroundNode(vdd->getPins()[1]->getNode());

        // Create visualizer for oscillator
        CircuitVisualizer osc_visualizer(osc_analyzer);

        // Perform transient analysis
        std::vector<double> time_points;
        std::vector<std::vector<Complex>> node_voltages;
        
        double t = 0.0;
        double tstop = 1e-6;  // 1µs simulation
        double tstep = 1e-9;  // 1ns steps
        
        while (t < tstop) {
            osc_analyzer.analyze();
            time_points.push_back(t);
            node_voltages.push_back(osc_analyzer.getNodeVoltages());
            t += tstep;
        }

        // Generate transient plot
        osc_visualizer.generateTransientPlot("crystal_osc", time_points, node_voltages);
        
        // Generate netlist and schematic
        osc_visualizer.generateNetlist("crystal_osc.net");
        osc_visualizer.generateSchematic("crystal_osc.tex");
    }

    return 0;
}
