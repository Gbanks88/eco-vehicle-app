#pragma once

#include "Component.hpp"
#include <complex>
#include <vector>
#include <array>

namespace circuit {

class Circulator : public Component {
public:
    Circulator(const std::string& name, double isolation = 20.0)
        : Component(name, ComponentType::CIRCULATOR) {
        setParameter("isolation", isolation);      // dB
        setParameter("insertion_loss", 0.5);       // dB
        setParameter("vswr", 1.2);                // Voltage Standing Wave Ratio
        setParameter("impedance", 50.0);          // Characteristic impedance
        
        addPin(std::make_shared<Pin>("port1", shared_from_this()));
        addPin(std::make_shared<Pin>("port2", shared_from_this()));
        addPin(std::make_shared<Pin>("port3", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        return Complex(getParameter("impedance"), 0);
    }

    Complex getCurrentThrough() const override {
        // Calculate currents based on S-parameters
        std::array<Complex, 3> voltages;
        for (size_t i = 0; i < 3; i++) {
            voltages[i] = pins_[i]->getNode()->getVoltage();
        }
        
        // S-parameters for ideal circulator
        double il = std::pow(10, -getParameter("insertion_loss") / 20);
        double iso = std::pow(10, -getParameter("isolation") / 20);
        
        std::array<std::array<Complex, 3>, 3> s_matrix = {{
            {Complex(0, 0), Complex(il, 0), Complex(iso, 0)},
            {Complex(iso, 0), Complex(0, 0), Complex(il, 0)},
            {Complex(il, 0), Complex(iso, 0), Complex(0, 0)}
        }};
        
        // Calculate port currents
        Complex current(0, 0);
        for (size_t i = 0; i < 3; i++) {
            for (size_t j = 0; j < 3; j++) {
                current += s_matrix[0][j] * voltages[j];
            }
        }
        
        return current / getParameter("impedance");
    }

    Complex getVoltageAcross() const override {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    void updateState(double timestep) override {
        // Circulators are typically passive devices with no state
    }
};

class Isolator : public Component {
public:
    Isolator(const std::string& name, double isolation = 20.0)
        : Component(name, ComponentType::ISOLATOR) {
        setParameter("isolation", isolation);      // dB
        setParameter("insertion_loss", 0.5);       // dB
        setParameter("vswr", 1.2);                // Voltage Standing Wave Ratio
        setParameter("impedance", 50.0);          // Characteristic impedance
        
        addPin(std::make_shared<Pin>("input", shared_from_this()));
        addPin(std::make_shared<Pin>("output", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        return Complex(getParameter("impedance"), 0);
    }

    Complex getCurrentThrough() const override {
        auto v_in = pins_[0]->getNode()->getVoltage();
        auto v_out = pins_[1]->getNode()->getVoltage();
        
        // Forward direction
        double il = std::pow(10, -getParameter("insertion_loss") / 20);
        double iso = std::pow(10, -getParameter("isolation") / 20);
        
        if (std::abs(v_in) > std::abs(v_out)) {
            return (v_in - v_out) * il / getParameter("impedance");
        } else {
            return (v_in - v_out) * iso / getParameter("impedance");
        }
    }

    Complex getVoltageAcross() const override {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    void updateState(double timestep) override {
        // Isolators are typically passive devices with no state
    }
};

class Coupler : public Component {
public:
    Coupler(const std::string& name, double coupling = 20.0)
        : Component(name, ComponentType::COUPLER) {
        setParameter("coupling", coupling);        // dB
        setParameter("directivity", 25.0);        // dB
        setParameter("insertion_loss", 0.5);       // dB
        setParameter("impedance", 50.0);          // Characteristic impedance
        
        addPin(std::make_shared<Pin>("input", shared_from_this()));
        addPin(std::make_shared<Pin>("through", shared_from_this()));
        addPin(std::make_shared<Pin>("coupled", shared_from_this()));
        addPin(std::make_shared<Pin>("isolated", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        return Complex(getParameter("impedance"), 0);
    }

    Complex getCurrentThrough() const override {
        std::array<Complex, 4> voltages;
        for (size_t i = 0; i < 4; i++) {
            voltages[i] = pins_[i]->getNode()->getVoltage();
        }
        
        // Calculate S-parameters
        double c = std::pow(10, -getParameter("coupling") / 20);
        double il = std::pow(10, -getParameter("insertion_loss") / 20);
        double d = std::pow(10, -getParameter("directivity") / 20);
        
        // S-matrix for directional coupler
        std::array<std::array<Complex, 4>, 4> s_matrix = {{
            {Complex(0, 0), Complex(il, 0), Complex(c, 0), Complex(d, 0)},
            {Complex(il, 0), Complex(0, 0), Complex(d, 0), Complex(c, 0)},
            {Complex(c, 0), Complex(d, 0), Complex(0, 0), Complex(il, 0)},
            {Complex(d, 0), Complex(c, 0), Complex(il, 0), Complex(0, 0)}
        }};
        
        // Calculate port currents
        Complex current(0, 0);
        for (size_t i = 0; i < 4; i++) {
            for (size_t j = 0; j < 4; j++) {
                current += s_matrix[0][j] * voltages[j];
            }
        }
        
        return current / getParameter("impedance");
    }

    Complex getVoltageAcross() const override {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    void updateState(double timestep) override {
        // Couplers are typically passive devices with no state
    }
};

class Attenuator : public Component {
public:
    Attenuator(const std::string& name, double attenuation = 10.0)
        : Component(name, ComponentType::ATTENUATOR) {
        setParameter("attenuation", attenuation); // dB
        setParameter("vswr", 1.2);               // Voltage Standing Wave Ratio
        setParameter("impedance", 50.0);         // Characteristic impedance
        setParameter("max_power", 1.0);          // Maximum power in watts
        
        addPin(std::make_shared<Pin>("input", shared_from_this()));
        addPin(std::make_shared<Pin>("output", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        return Complex(getParameter("impedance"), 0);
    }

    Complex getCurrentThrough() const override {
        auto v_in = pins_[0]->getNode()->getVoltage();
        auto v_out = pins_[1]->getNode()->getVoltage();
        
        double att = std::pow(10, -getParameter("attenuation") / 20);
        return (v_in - v_out) * att / getParameter("impedance");
    }

    Complex getVoltageAcross() const override {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    void updateState(double timestep) override {
        // Calculate power dissipation
        auto v = getVoltageAcross();
        auto i = getCurrentThrough();
        power_dissipated_ = std::abs(v * std::conj(i));
        
        // Check power limit
        if (power_dissipated_ > getParameter("max_power")) {
            // In real implementation, this would trigger a warning or simulation stop
        }
    }

private:
    double power_dissipated_ = 0.0;
};

class PhaseShifter : public Component {
public:
    PhaseShifter(const std::string& name, double phase_shift = 90.0)
        : Component(name, ComponentType::PHASE_SHIFTER) {
        setParameter("phase_shift", phase_shift); // degrees
        setParameter("insertion_loss", 1.0);      // dB
        setParameter("vswr", 1.3);               // Voltage Standing Wave Ratio
        setParameter("impedance", 50.0);         // Characteristic impedance
        
        addPin(std::make_shared<Pin>("input", shared_from_this()));
        addPin(std::make_shared<Pin>("output", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        return Complex(getParameter("impedance"), 0);
    }

    Complex getCurrentThrough() const override {
        auto v_in = pins_[0]->getNode()->getVoltage();
        auto v_out = pins_[1]->getNode()->getVoltage();
        
        double il = std::pow(10, -getParameter("insertion_loss") / 20);
        double phase_rad = getParameter("phase_shift") * M_PI / 180.0;
        
        Complex phase_factor = std::polar(1.0, phase_rad);
        return (v_in * phase_factor - v_out) * il / getParameter("impedance");
    }

    Complex getVoltageAcross() const override {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    void updateState(double timestep) override {
        // Phase shifters are typically passive devices with no state
    }
};

} // namespace circuit
