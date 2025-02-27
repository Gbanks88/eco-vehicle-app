#pragma once

#include "Component.hpp"
#include <cmath>

namespace circuit {

class Transistor : public Component {
public:
    enum class Type { NPN, PNP };
    
    Transistor(const std::string& name, Type type)
        : Component(name, ComponentType::TRANSISTOR) {
        setParameter("beta", 100.0);   // Current gain
        setParameter("is", 1e-14);     // Saturation current
        setParameter("vt", 0.026);     // Thermal voltage
        setParameter("va", 100.0);     // Early voltage
        transistor_type_ = type;
        
        addPin(std::make_shared<Pin>("collector", shared_from_this()));
        addPin(std::make_shared<Pin>("base", shared_from_this()));
        addPin(std::make_shared<Pin>("emitter", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        // Dynamic impedance based on operating point
        auto vbe = std::abs(getBaseEmitterVoltage());
        auto ic = getCollectorCurrent();
        return Complex(getParameter("vt") / ic, 0);
    }

    Complex getCurrentThrough() const override {
        return getCollectorCurrent();
    }

    Complex getVoltageAcross() const override {
        return getCollectorEmitterVoltage();
    }

    void updateState(double timestep) override {
        // Update internal capacitances and stored charge
        auto vbe = getBaseEmitterVoltage();
        auto vbc = getBaseCollectorVoltage();
        base_charge_ += (std::abs(getBaseCurrent()) * timestep);
    }

private:
    Complex getBaseEmitterVoltage() const {
        return pins_[1]->getNode()->getVoltage() - pins_[2]->getNode()->getVoltage();
    }

    Complex getBaseCollectorVoltage() const {
        return pins_[1]->getNode()->getVoltage() - pins_[0]->getNode()->getVoltage();
    }

    Complex getCollectorEmitterVoltage() const {
        return pins_[0]->getNode()->getVoltage() - pins_[2]->getNode()->getVoltage();
    }

    Complex getCollectorCurrent() const {
        auto vbe = std::abs(getBaseEmitterVoltage());
        auto vbc = std::abs(getBaseCollectorVoltage());
        auto is = getParameter("is");
        auto vt = getParameter("vt");
        auto beta = getParameter("beta");
        auto va = getParameter("va");
        
        auto ies = is / beta;
        auto ics = is;
        
        auto ie = ies * (std::exp(vbe/vt) - 1);
        auto ic = ics * (std::exp(vbe/vt) - 1) * (1 + vbc/va);
        
        return transistor_type_ == Type::NPN ? ic : -ic;
    }

    Complex getBaseCurrent() const {
        return getCollectorCurrent() / getParameter("beta");
    }

    Type transistor_type_;
    double base_charge_ = 0.0;
};

class MOSFET : public Component {
public:
    enum class Type { NMOS, PMOS };
    
    MOSFET(const std::string& name, Type type)
        : Component(name, ComponentType::MOSFET) {
        setParameter("vth", 0.7);      // Threshold voltage
        setParameter("kp", 20e-6);     // Transconductance parameter
        setParameter("lambda", 0.01);   // Channel length modulation
        mosfet_type_ = type;
        
        addPin(std::make_shared<Pin>("drain", shared_from_this()));
        addPin(std::make_shared<Pin>("gate", shared_from_this()));
        addPin(std::make_shared<Pin>("source", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        // Dynamic impedance based on operating point
        auto vgs = std::abs(getGateSourceVoltage());
        auto id = getDrainCurrent();
        if (std::abs(id) < 1e-12) return Complex(1e12, 0);
        return Complex(1.0 / (getParameter("kp") * (vgs - getParameter("vth"))), 0);
    }

    Complex getCurrentThrough() const override {
        return getDrainCurrent();
    }

    Complex getVoltageAcross() const override {
        return getDrainSourceVoltage();
    }

    void updateState(double timestep) override {
        // Update gate charge
        auto vgs = getGateSourceVoltage();
        gate_charge_ += (std::abs(getGateCurrent()) * timestep);
    }

private:
    Complex getGateSourceVoltage() const {
        return pins_[1]->getNode()->getVoltage() - pins_[2]->getNode()->getVoltage();
    }

    Complex getDrainSourceVoltage() const {
        return pins_[0]->getNode()->getVoltage() - pins_[2]->getNode()->getVoltage();
    }

    Complex getDrainCurrent() const {
        auto vgs = std::abs(getGateSourceVoltage());
        auto vds = std::abs(getDrainSourceVoltage());
        auto vth = getParameter("vth");
        auto kp = getParameter("kp");
        auto lambda = getParameter("lambda");
        
        Complex id(0, 0);
        if (vgs <= vth) {
            // Cut-off region
            id = Complex(0, 0);
        } else if (vds <= vgs - vth) {
            // Linear region
            id = Complex(kp * ((vgs - vth) * vds - vds * vds / 2) * (1 + lambda * vds), 0);
        } else {
            // Saturation region
            id = Complex(kp/2 * std::pow(vgs - vth, 2) * (1 + lambda * vds), 0);
        }
        
        return mosfet_type_ == Type::NMOS ? id : -id;
    }

    Complex getGateCurrent() const {
        // Gate leakage is typically negligible
        return Complex(1e-12, 0);
    }

    Type mosfet_type_;
    double gate_charge_ = 0.0;
};

class CrystalOscillator : public Component {
public:
    CrystalOscillator(const std::string& name, double frequency)
        : Component(name, ComponentType::CRYSTAL) {
        setParameter("frequency", frequency);  // Resonant frequency
        setParameter("q", 10000.0);           // Quality factor
        setParameter("c0", 5e-12);            // Shunt capacitance
        setParameter("cm", 1e-12);            // Motional capacitance
        
        addPin(std::make_shared<Pin>("p1", shared_from_this()));
        addPin(std::make_shared<Pin>("p2", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        auto f0 = getParameter("frequency");
        auto q = getParameter("q");
        auto c0 = getParameter("c0");
        auto cm = getParameter("cm");
        
        // Calculate motional inductance
        auto lm = 1.0 / (4 * M_PI * M_PI * f0 * f0 * cm);
        
        // Calculate motional resistance
        auto rm = 2 * M_PI * f0 * lm / q;
        
        // Calculate impedance components
        auto w = 2 * M_PI * frequency;
        auto zc0 = Complex(0, -1.0 / (w * c0));
        auto zcm = Complex(0, -1.0 / (w * cm));
        auto zlm = Complex(0, w * lm);
        
        // Combine impedances
        auto zm = rm + zcm + zlm;  // Series motional branch
        auto zt = (zc0 * zm) / (zc0 + zm);  // Parallel combination
        
        return zt;
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
        // Update stored energy
        auto i = getCurrentThrough();
        stored_energy_ += std::abs(i * getVoltageAcross()) * timestep;
    }

private:
    double current_frequency_ = 0.0;
    double stored_energy_ = 0.0;
};

} // namespace circuit
