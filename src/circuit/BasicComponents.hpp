#pragma once

#include "Component.hpp"
#include <cmath>

namespace circuit {

class Resistor : public Component {
public:
    Resistor(const std::string& name, double resistance)
        : Component(name, ComponentType::RESISTOR) {
        setParameter("resistance", resistance);
        addPin(std::make_shared<Pin>("p1", shared_from_this()));
        addPin(std::make_shared<Pin>("p2", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        return Complex(getParameter("resistance"), 0);
    }

    Complex getCurrentThrough() const override {
        auto v1 = pins_[0]->getNode()->getVoltage();
        auto v2 = pins_[1]->getNode()->getVoltage();
        return (v1 - v2) / getParameter("resistance");
    }

    Complex getVoltageAcross() const override {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    void updateState(double timestep) override {
        // Resistors are memoryless, no state to update
    }
};

class Capacitor : public Component {
public:
    Capacitor(const std::string& name, double capacitance)
        : Component(name, ComponentType::CAPACITOR) {
        setParameter("capacitance", capacitance);
        addPin(std::make_shared<Pin>("p1", shared_from_this()));
        addPin(std::make_shared<Pin>("p2", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        if (frequency == 0) return Complex(INFINITY, 0);
        double xc = 1.0 / (2 * M_PI * frequency * getParameter("capacitance"));
        return Complex(0, -xc);
    }

    Complex getCurrentThrough() const override {
        auto v = getVoltageAcross();
        auto z = getImpedance(current_frequency_);
        return v / z;
    }

    Complex getVoltageAcross() const override {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    void updateState(double timestep) override {
        // Update stored charge
        auto i = getCurrentThrough();
        charge_ += std::abs(i) * timestep;
    }

private:
    double charge_ = 0.0;
    double current_frequency_ = 0.0;
};

class Inductor : public Component {
public:
    Inductor(const std::string& name, double inductance)
        : Component(name, ComponentType::INDUCTOR) {
        setParameter("inductance", inductance);
        addPin(std::make_shared<Pin>("p1", shared_from_this()));
        addPin(std::make_shared<Pin>("p2", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        double xl = 2 * M_PI * frequency * getParameter("inductance");
        return Complex(0, xl);
    }

    Complex getCurrentThrough() const override {
        auto v = getVoltageAcross();
        auto z = getImpedance(current_frequency_);
        return v / z;
    }

    Complex getVoltageAcross() const override {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    void updateState(double timestep) override {
        // Update stored magnetic flux
        auto v = getVoltageAcross();
        flux_ += std::abs(v) * timestep;
    }

private:
    double flux_ = 0.0;
    double current_frequency_ = 0.0;
};

class VoltageSource : public Component {
public:
    VoltageSource(const std::string& name, double voltage, double frequency = 0.0)
        : Component(name, ComponentType::VOLTAGE_SOURCE) {
        setParameter("voltage", voltage);
        setParameter("frequency", frequency);
        addPin(std::make_shared<Pin>("p1", shared_from_this()));
        addPin(std::make_shared<Pin>("p2", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        return Complex(0, 0);  // Ideal voltage source has zero impedance
    }

    Complex getCurrentThrough() const override {
        // Current through voltage source is determined by circuit analysis
        return current_;
    }

    Complex getVoltageAcross() const override {
        double freq = getParameter("frequency");
        if (freq == 0.0) {
            return Complex(getParameter("voltage"), 0);
        } else {
            double time = current_time_;
            double omega = 2 * M_PI * freq;
            return Complex(getParameter("voltage") * std::cos(omega * time),
                         getParameter("voltage") * std::sin(omega * time));
        }
    }

    void updateState(double timestep) override {
        current_time_ += timestep;
    }

    void setCurrent(Complex current) {
        current_ = current;
    }

private:
    Complex current_;
    double current_time_ = 0.0;
};

class Diode : public Component {
public:
    Diode(const std::string& name)
        : Component(name, ComponentType::DIODE) {
        setParameter("is", 1e-12);    // Saturation current
        setParameter("vt", 0.026);    // Thermal voltage
        addPin(std::make_shared<Pin>("anode", shared_from_this()));
        addPin(std::make_shared<Pin>("cathode", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        // Dynamic resistance based on current operating point
        auto v = std::abs(getVoltageAcross());
        auto is = getParameter("is");
        auto vt = getParameter("vt");
        auto id = is * (std::exp(v/vt) - 1);
        return Complex(vt/id, 0);
    }

    Complex getCurrentThrough() const override {
        auto v = std::abs(getVoltageAcross());
        auto is = getParameter("is");
        auto vt = getParameter("vt");
        return Complex(is * (std::exp(v/vt) - 1), 0);
    }

    Complex getVoltageAcross() const override {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    void updateState(double timestep) override {
        // Diodes are memoryless, no state to update
    }
};

class OpAmp : public Component {
public:
    OpAmp(const std::string& name)
        : Component(name, ComponentType::OPAMP) {
        setParameter("gain", 1e5);     // Open loop gain
        setParameter("gbw", 1e6);      // Gain bandwidth product
        setParameter("vsat", 15.0);    // Output saturation voltage
        addPin(std::make_shared<Pin>("in+", shared_from_this()));
        addPin(std::make_shared<Pin>("in-", shared_from_this()));
        addPin(std::make_shared<Pin>("out", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        // Input impedance is very high, output impedance is very low
        return Complex(1e6, 0);
    }

    Complex getCurrentThrough() const override {
        // Depends on the load impedance
        return Complex(0, 0);
    }

    Complex getVoltageAcross() const override {
        auto vp = pins_[0]->getNode()->getVoltage();
        auto vn = pins_[1]->getNode()->getVoltage();
        auto gain = getParameter("gain");
        auto vout = gain * (vp - vn);
        auto vsat = getParameter("vsat");
        
        // Apply saturation
        if (std::abs(vout) > vsat) {
            vout = vsat * (vout > 0 ? 1 : -1);
        }
        
        return Complex(vout, 0);
    }

    void updateState(double timestep) override {
        // Update internal state for frequency compensation
        auto vout = getVoltageAcross();
        output_voltage_ = vout;
    }

private:
    Complex output_voltage_;
};

} // namespace circuit
