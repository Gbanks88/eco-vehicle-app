#pragma once

#include "Component.hpp"
#include <complex>
#include <vector>
#include <deque>

namespace circuit {

class TransmissionLine : public Component {
public:
    TransmissionLine(const std::string& name, double length, double z0, double velocity_factor = 0.66)
        : Component(name, ComponentType::TRANSMISSION_LINE) {
        setParameter("length", length);                 // meters
        setParameter("z0", z0);                        // characteristic impedance (ohms)
        setParameter("vf", velocity_factor);           // velocity factor (0 to 1)
        setParameter("loss", 0.1);                     // dB/meter
        
        addPin(std::make_shared<Pin>("in+", shared_from_this()));
        addPin(std::make_shared<Pin>("in-", shared_from_this()));
        addPin(std::make_shared<Pin>("out+", shared_from_this()));
        addPin(std::make_shared<Pin>("out-", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        auto z0 = getParameter("z0");
        auto length = getParameter("length");
        auto loss = getParameter("loss");
        auto vf = getParameter("vf");
        
        // Calculate propagation constant
        double c = 3e8;  // speed of light
        double beta = 2 * M_PI * frequency / (c * vf);
        double alpha = loss * frequency / 1e9;  // Convert loss to Nepers/m
        Complex gamma(alpha, beta);
        
        // Calculate input impedance
        auto zl = getLoadImpedance();
        return z0 * (zl * std::cosh(gamma * length) + z0 * std::sinh(gamma * length)) /
               (z0 * std::cosh(gamma * length) + zl * std::sinh(gamma * length));
    }

    Complex getCurrentThrough() const override {
        auto vin = getInputVoltage();
        auto z = getImpedance(current_frequency_);
        return vin / z;
    }

    Complex getVoltageAcross() const override {
        return getInputVoltage();
    }

    void updateState(double timestep) override {
        // Update voltage and current history for time-domain simulation
        auto v_in = getInputVoltage();
        auto i_in = getCurrentThrough();
        
        voltage_history_.push_front(v_in);
        current_history_.push_front(i_in);
        
        // Maintain history length based on line delay
        size_t max_history = static_cast<size_t>(getDelay() / timestep);
        while (voltage_history_.size() > max_history) {
            voltage_history_.pop_back();
            current_history_.pop_back();
        }
    }

    Complex getDelayedVoltage() const {
        return voltage_history_.empty() ? Complex(0,0) : voltage_history_.back();
    }

    Complex getDelayedCurrent() const {
        return current_history_.empty() ? Complex(0,0) : current_history_.back();
    }

private:
    Complex getInputVoltage() const {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    Complex getLoadImpedance() const {
        auto vl = pins_[2]->getNode()->getVoltage() - pins_[3]->getNode()->getVoltage();
        auto il = getDelayedCurrent();
        return std::abs(il) < 1e-12 ? getParameter("z0") : vl / il;
    }

    double getDelay() const {
        auto length = getParameter("length");
        auto vf = getParameter("vf");
        return length / (3e8 * vf);  // seconds
    }

    std::deque<Complex> voltage_history_;
    std::deque<Complex> current_history_;
    double current_frequency_ = 0.0;
};

class Transformer : public Component {
public:
    Transformer(const std::string& name, double turns_ratio, double primary_inductance)
        : Component(name, ComponentType::TRANSFORMER) {
        setParameter("turns_ratio", turns_ratio);
        setParameter("Lp", primary_inductance);        // Primary inductance
        setParameter("coupling", 0.99);                // Coupling coefficient
        setParameter("Rp", 0.1);                       // Primary winding resistance
        setParameter("Rs", 0.1);                       // Secondary winding resistance
        
        addPin(std::make_shared<Pin>("p1", shared_from_this()));
        addPin(std::make_shared<Pin>("p2", shared_from_this()));
        addPin(std::make_shared<Pin>("s1", shared_from_this()));
        addPin(std::make_shared<Pin>("s2", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        auto Lp = getParameter("Lp");
        auto Rp = getParameter("Rp");
        auto w = 2 * M_PI * frequency;
        return Complex(Rp, w * Lp);
    }

    Complex getCurrentThrough() const override {
        auto vp = getPrimaryVoltage();
        auto z = getImpedance(current_frequency_);
        return vp / z;
    }

    Complex getVoltageAcross() const override {
        return getPrimaryVoltage();
    }

    void updateState(double timestep) override {
        // Update magnetic flux
        auto vp = getPrimaryVoltage();
        primary_flux_ += std::abs(vp) * timestep;
        
        auto vs = getSecondaryVoltage();
        secondary_flux_ += std::abs(vs) * timestep;
    }

    Complex getSecondaryVoltage() const {
        auto n = getParameter("turns_ratio");
        auto k = getParameter("coupling");
        return getPrimaryVoltage() * n * k;
    }

    Complex getSecondaryImpedance(double frequency) const {
        auto n = getParameter("turns_ratio");
        auto Rs = getParameter("Rs");
        auto z = getImpedance(frequency);
        return Complex(Rs, 0) + z * n * n;
    }

private:
    Complex getPrimaryVoltage() const {
        return pins_[0]->getNode()->getVoltage() - pins_[1]->getNode()->getVoltage();
    }

    double primary_flux_ = 0.0;
    double secondary_flux_ = 0.0;
    double current_frequency_ = 0.0;
};

class WaveguidePort : public Component {
public:
    WaveguidePort(const std::string& name, double width, double height, 
                  double cutoff_frequency)
        : Component(name, ComponentType::WAVEGUIDE) {
        setParameter("width", width);
        setParameter("height", height);
        setParameter("fc", cutoff_frequency);
        setParameter("loss", 0.1);  // dB/meter
        
        addPin(std::make_shared<Pin>("p1", shared_from_this()));
        addPin(std::make_shared<Pin>("p2", shared_from_this()));
    }

    Complex getImpedance(double frequency) const override {
        auto fc = getParameter("fc");
        if (frequency < fc) {
            return Complex(0, 1e6);  // Below cutoff, very high impedance
        }
        
        // Calculate wave impedance above cutoff
        double eta = 377.0;  // Free space impedance
        double beta = 2 * M_PI * frequency * 
                     std::sqrt(1 - std::pow(fc/frequency, 2)) / 3e8;
        return Complex(eta / beta, 0);
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
        auto v = getVoltageAcross();
        auto i = getCurrentThrough();
        stored_energy_ += std::abs(v * std::conj(i)) * timestep;
    }

private:
    double stored_energy_ = 0.0;
    double current_frequency_ = 0.0;
};

} // namespace circuit
