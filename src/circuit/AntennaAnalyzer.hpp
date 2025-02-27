#pragma once

#include "EMSolver.hpp"
#include <vector>
#include <complex>
#include <memory>

namespace circuit {

class AntennaAnalyzer {
public:
    struct RadiationPattern {
        std::vector<double> theta;      // Elevation angles
        std::vector<double> phi;        // Azimuth angles
        std::vector<std::vector<double>> gain;  // Gain pattern [theta][phi]
        std::vector<std::vector<double>> phase; // Phase pattern [theta][phi]
    };

    struct AntennaParameters {
        double frequency;           // Operating frequency
        double input_impedance;     // Input impedance
        double vswr;               // Voltage Standing Wave Ratio
        double directivity;        // Directivity in dBi
        double gain;               // Gain in dBi
        double efficiency;         // Radiation efficiency
        double bandwidth;          // Bandwidth
        Vector3D main_beam;        // Main beam direction
        double beamwidth;          // 3dB beamwidth
        double front_to_back;      // Front-to-back ratio
        double polarization;       // Polarization ratio
    };

    AntennaAnalyzer(EMSolver& solver) : solver_(solver) {}

    RadiationPattern calculateRadiationPattern(
        double theta_start = 0,
        double theta_end = 180,
        double theta_step = 1,
        double phi_start = 0,
        double phi_end = 360,
        double phi_step = 1) {
        
        RadiationPattern pattern;
        
        // Generate angle arrays
        for (double theta = theta_start; theta <= theta_end; theta += theta_step) {
            pattern.theta.push_back(theta);
        }
        
        for (double phi = phi_start; phi <= phi_end; phi += phi_step) {
            pattern.phi.push_back(phi);
        }
        
        // Initialize gain and phase matrices
        pattern.gain.resize(pattern.theta.size(), 
                          std::vector<double>(pattern.phi.size()));
        pattern.phase.resize(pattern.theta.size(), 
                           std::vector<double>(pattern.phi.size()));
        
        // Calculate pattern for each direction
        for (size_t i = 0; i < pattern.theta.size(); i++) {
            for (size_t j = 0; j < pattern.phi.size(); j++) {
                auto field = calculateFarField(pattern.theta[i], pattern.phi[j]);
                pattern.gain[i][j] = calculateGain(field);
                pattern.phase[i][j] = calculatePhase(field);
            }
        }
        
        return pattern;
    }

    AntennaParameters analyzeAntenna() {
        AntennaParameters params;
        
        // Calculate input impedance
        params.input_impedance = calculateInputImpedance();
        
        // Calculate VSWR
        params.vswr = calculateVSWR(params.input_impedance);
        
        // Calculate radiation pattern
        auto pattern = calculateRadiationPattern();
        
        // Find maximum gain and its direction
        findMaximumGain(pattern, params);
        
        // Calculate directivity
        params.directivity = calculateDirectivity(pattern);
        
        // Calculate efficiency
        params.efficiency = calculateEfficiency();
        
        // Calculate gain
        params.gain = params.directivity * params.efficiency;
        
        // Calculate bandwidth
        params.bandwidth = calculateBandwidth();
        
        // Calculate beamwidth
        params.beamwidth = calculateBeamwidth(pattern);
        
        // Calculate front-to-back ratio
        params.front_to_back = calculateFrontToBack(pattern);
        
        // Calculate polarization
        params.polarization = calculatePolarization();
        
        return params;
    }

    std::vector<double> calculateSParameters(
        const std::vector<double>& frequencies) {
        std::vector<double> s_params;
        
        for (double freq : frequencies) {
            solver_.setFrequency(freq);
            solver_.solve();
            
            auto s11 = calculateReflectionCoefficient();
            s_params.push_back(std::abs(s11));
        }
        
        return s_params;
    }

    double calculateGainAtFrequency(double frequency) {
        solver_.setFrequency(frequency);
        solver_.solve();
        
        auto pattern = calculateRadiationPattern();
        AntennaParameters params;
        findMaximumGain(pattern, params);
        
        return params.gain;
    }

private:
    EMField calculateFarField(double theta, double phi) {
        // Convert spherical to Cartesian coordinates
        double x = std::sin(theta) * std::cos(phi);
        double y = std::sin(theta) * std::sin(phi);
        double z = std::cos(theta);
        
        Point3D point = {x, y, z};
        
        // Get near-field solution from solver
        solver_.solve();
        auto near_fields = solver_.getFields();
        
        // Transform to far field using radiation integrals
        Vector3D e_field = {0, 0, 0};
        Vector3D h_field = {0, 0, 0};
        
        // This is a simplified version - actual implementation would use
        // proper far-field transformation
        for (const auto& near_field : near_fields) {
            // Add contribution from each near-field point
            // using radiation integrals
        }
        
        return EMField(point, e_field, h_field);
    }

    double calculateGain(const EMField& field) {
        auto s = field.getPoyntingVector();
        double power = std::sqrt(s.x * s.x + s.y * s.y + s.z * s.z);
        
        // Calculate gain relative to isotropic radiator
        return 10 * std::log10(4 * M_PI * power / total_input_power_);
    }

    double calculatePhase(const EMField& field) {
        return std::atan2(field.getEFieldMagnitude(), 
                         field.getHFieldMagnitude());
    }

    double calculateInputImpedance() {
        // Get fields at input port
        solver_.solve();
        auto fields = solver_.getFields();
        
        // Find port location
        // This is simplified - actual implementation would properly
        // identify port location
        auto port_field = fields[0];
        
        // Calculate impedance
        return port_field.getEFieldMagnitude() / 
               port_field.getHFieldMagnitude();
    }

    double calculateVSWR(double z_in) {
        double z0 = 50.0;  // Reference impedance
        double gamma = std::abs((z_in - z0) / (z_in + z0));
        return (1 + gamma) / (1 - gamma);
    }

    void findMaximumGain(const RadiationPattern& pattern,
                        AntennaParameters& params) {
        double max_gain = -std::numeric_limits<double>::infinity();
        size_t max_i = 0, max_j = 0;
        
        for (size_t i = 0; i < pattern.theta.size(); i++) {
            for (size_t j = 0; j < pattern.phi.size(); j++) {
                if (pattern.gain[i][j] > max_gain) {
                    max_gain = pattern.gain[i][j];
                    max_i = i;
                    max_j = j;
                }
            }
        }
        
        params.gain = max_gain;
        params.main_beam = {
            std::sin(pattern.theta[max_i]) * std::cos(pattern.phi[max_j]),
            std::sin(pattern.theta[max_i]) * std::sin(pattern.phi[max_j]),
            std::cos(pattern.theta[max_i])
        };
    }

    double calculateDirectivity(const RadiationPattern& pattern) {
        double total_power = 0.0;
        double max_power = 0.0;
        
        for (size_t i = 0; i < pattern.theta.size(); i++) {
            for (size_t j = 0; j < pattern.phi.size(); j++) {
                double power = std::pow(10, pattern.gain[i][j] / 10);
                total_power += power;
                max_power = std::max(max_power, power);
            }
        }
        
        return 10 * std::log10(4 * M_PI * max_power / total_power);
    }

    double calculateEfficiency() {
        solver_.solve();
        auto fields = solver_.getFields();
        
        double radiated_power = 0.0;
        double input_power = total_input_power_;
        
        for (const auto& field : fields) {
            auto s = field.getPoyntingVector();
            radiated_power += std::sqrt(s.x * s.x + s.y * s.y + s.z * s.z);
        }
        
        return radiated_power / input_power;
    }

    double calculateBandwidth() {
        // Find frequencies where VSWR crosses threshold
        double vswr_threshold = 2.0;
        double f_low = 0.0, f_high = 0.0;
        
        // This is simplified - actual implementation would
        // search for bandwidth limits
        
        return (f_high - f_low) / solver_.getFrequency();
    }

    double calculateBeamwidth(const RadiationPattern& pattern) {
        // Find -3dB points in main beam
        double max_gain = -std::numeric_limits<double>::infinity();
        
        for (const auto& row : pattern.gain) {
            for (double gain : row) {
                max_gain = std::max(max_gain, gain);
            }
        }
        
        // Find angular width at -3dB points
        double threshold = max_gain - 3.0;
        
        // This is simplified - actual implementation would
        // properly calculate 3dB beamwidth
        
        return 0.0;  // Return in degrees
    }

    double calculateFrontToBack(const RadiationPattern& pattern) {
        // Find gain in main beam direction and opposite direction
        double front_gain = pattern.gain[0][0];  // Simplified
        double back_gain = pattern.gain[pattern.theta.size()-1][0];  // Simplified
        
        return front_gain - back_gain;  // Return in dB
    }

    double calculatePolarization() {
        // Calculate ratio of desired to cross-polarization
        solver_.solve();
        auto fields = solver_.getFields();
        
        // This is simplified - actual implementation would
        // properly calculate polarization ratio
        
        return 0.0;  // Return in dB
    }

    Complex calculateReflectionCoefficient() {
        double z_in = calculateInputImpedance();
        double z0 = 50.0;  // Reference impedance
        return Complex((z_in - z0) / (z_in + z0));
    }

    EMSolver& solver_;
    double total_input_power_ = 1.0;  // Normalized input power
};

} // namespace circuit
