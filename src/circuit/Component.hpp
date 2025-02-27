#pragma once

#include <string>
#include <vector>
#include <memory>
#include <map>
#include <complex>

namespace circuit {

using Complex = std::complex<double>;

// Forward declarations
class Node;
class Pin;

enum class ComponentType {
    RESISTOR,
    CAPACITOR,
    INDUCTOR,
    VOLTAGE_SOURCE,
    CURRENT_SOURCE,
    DIODE,
    TRANSISTOR,
    OPAMP,
    TRANSFORMER,
    GROUND
};

class Component {
public:
    Component(const std::string& name, ComponentType type)
        : name_(name), type_(type) {}
    
    virtual ~Component() = default;

    // Basic properties
    const std::string& getName() const { return name_; }
    ComponentType getType() const { return type_; }
    
    // Pin management
    void addPin(std::shared_ptr<Pin> pin) {
        pins_.push_back(pin);
    }

    const std::vector<std::shared_ptr<Pin>>& getPins() const {
        return pins_;
    }

    // Parameters
    void setParameter(const std::string& name, double value) {
        parameters_[name] = value;
    }

    double getParameter(const std::string& name) const {
        auto it = parameters_.find(name);
        return (it != parameters_.end()) ? it->second : 0.0;
    }

    // Virtual methods for analysis
    virtual Complex getImpedance(double frequency) const = 0;
    virtual Complex getCurrentThrough() const = 0;
    virtual Complex getVoltageAcross() const = 0;
    virtual void updateState(double timestep) = 0;

protected:
    std::string name_;
    ComponentType type_;
    std::vector<std::shared_ptr<Pin>> pins_;
    std::map<std::string, double> parameters_;
};

class Pin {
public:
    Pin(const std::string& name, std::shared_ptr<Component> component)
        : name_(name), component_(component), node_(nullptr) {}

    void connectTo(std::shared_ptr<Node> node) {
        node_ = node;
    }

    std::shared_ptr<Node> getNode() const { return node_; }
    std::shared_ptr<Component> getComponent() const { return component_.lock(); }
    const std::string& getName() const { return name_; }

private:
    std::string name_;
    std::weak_ptr<Component> component_;
    std::shared_ptr<Node> node_;
};

class Node {
public:
    Node(const std::string& name) : name_(name), voltage_(0.0) {}

    void addPin(std::shared_ptr<Pin> pin) {
        pins_.push_back(pin);
    }

    const std::vector<std::shared_ptr<Pin>>& getPins() const {
        return pins_;
    }

    void setVoltage(Complex voltage) { voltage_ = voltage; }
    Complex getVoltage() const { return voltage_; }

private:
    std::string name_;
    std::vector<std::shared_ptr<Pin>> pins_;
    Complex voltage_;
};

} // namespace circuit
