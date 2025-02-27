#pragma once

#include "Component.hpp"
#include "BasicComponents.hpp"
#include <Eigen/Dense>
#include <vector>
#include <map>
#include <set>

namespace circuit {

class CircuitAnalyzer {
public:
    CircuitAnalyzer() = default;

    void addComponent(std::shared_ptr<Component> component) {
        components_.push_back(component);
        
        // Add nodes if they don't exist
        for (const auto& pin : component->getPins()) {
            if (pin->getNode() == nullptr) {
                auto node = std::make_shared<Node>("n" + std::to_string(next_node_id_++));
                pin->connectTo(node);
                nodes_.push_back(node);
            }
        }
    }

    void setGroundNode(std::shared_ptr<Node> node) {
        ground_node_ = node;
    }

    void analyze(double frequency = 0.0) {
        current_frequency_ = frequency;
        buildMNA();
        solve();
        updateComponents();
    }

    void performTransient(double stop_time, double timestep) {
        double t = 0.0;
        while (t < stop_time) {
            analyze();
            for (auto& component : components_) {
                component->updateState(timestep);
            }
            t += timestep;
            time_ = t;
        }
    }

    void performAC(double start_freq, double stop_freq, int points) {
        std::vector<double> frequencies;
        double log_start = std::log10(start_freq);
        double log_stop = std::log10(stop_freq);
        double step = (log_stop - log_start) / (points - 1);

        for (int i = 0; i < points; i++) {
            frequencies.push_back(std::pow(10, log_start + i * step));
        }

        for (double freq : frequencies) {
            analyze(freq);
            // Store results for frequency response analysis
            frequency_response_[freq] = getNodeVoltages();
        }
    }

    std::map<double, std::vector<Complex>> getFrequencyResponse() const {
        return frequency_response_;
    }

    std::vector<Complex> getNodeVoltages() const {
        std::vector<Complex> voltages;
        for (const auto& node : nodes_) {
            voltages.push_back(node->getVoltage());
        }
        return voltages;
    }

private:
    void buildMNA() {
        int n = nodes_.size() - 1;  // Exclude ground node
        int m = voltage_sources_.size();
        int size = n + m;

        // Initialize matrices
        A_ = Eigen::MatrixXcd::Zero(size, size);
        b_ = Eigen::VectorXcd::Zero(size);

        // Build conductance matrix (G)
        for (const auto& component : components_) {
            if (component->getType() != ComponentType::VOLTAGE_SOURCE) {
                auto z = component->getImpedance(current_frequency_);
                auto y = Complex(1.0) / z;
                
                auto pins = component->getPins();
                int n1 = getNodeIndex(pins[0]->getNode());
                int n2 = getNodeIndex(pins[1]->getNode());

                if (n1 >= 0) {
                    A_(n1, n1) += y;
                    if (n2 >= 0) A_(n1, n2) -= y;
                }
                if (n2 >= 0) {
                    A_(n2, n2) += y;
                    if (n1 >= 0) A_(n2, n1) -= y;
                }
            }
        }

        // Add voltage sources
        int vsi = n;
        for (const auto& vs : voltage_sources_) {
            auto pins = vs->getPins();
            int n1 = getNodeIndex(pins[0]->getNode());
            int n2 = getNodeIndex(pins[1]->getNode());

            // Add current variables
            if (n1 >= 0) {
                A_(n1, vsi) = 1.0;
                A_(vsi, n1) = 1.0;
            }
            if (n2 >= 0) {
                A_(n2, vsi) = -1.0;
                A_(vsi, n2) = -1.0;
            }

            // Add voltage constraint
            b_(vsi) = vs->getVoltageAcross();
            vsi++;
        }
    }

    void solve() {
        // Solve Ax = b using Eigen
        Eigen::VectorXcd x = A_.colPivHouseholderQr().solve(b_);

        // Update node voltages
        for (size_t i = 0; i < nodes_.size() - 1; i++) {
            nodes_[i]->setVoltage(x(i));
        }

        // Update voltage source currents
        int vsi = nodes_.size() - 1;
        for (auto& vs : voltage_sources_) {
            vs->setCurrent(x(vsi++));
        }
    }

    void updateComponents() {
        for (auto& component : components_) {
            component->updateState(timestep_);
        }
    }

    int getNodeIndex(std::shared_ptr<Node> node) {
        if (node == ground_node_) return -1;
        for (size_t i = 0; i < nodes_.size(); i++) {
            if (nodes_[i] == node) return i;
        }
        return -1;
    }

    std::vector<std::shared_ptr<Component>> components_;
    std::vector<std::shared_ptr<Node>> nodes_;
    std::vector<std::shared_ptr<VoltageSource>> voltage_sources_;
    std::shared_ptr<Node> ground_node_;
    
    Eigen::MatrixXcd A_;
    Eigen::VectorXcd b_;
    
    double current_frequency_ = 0.0;
    double time_ = 0.0;
    double timestep_ = 1e-6;
    int next_node_id_ = 0;
    
    std::map<double, std::vector<Complex>> frequency_response_;
};

} // namespace circuit
