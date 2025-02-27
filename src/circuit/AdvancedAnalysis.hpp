#pragma once

#include "CircuitAnalyzer.hpp"
#include <complex>
#include <vector>
#include <map>

namespace circuit {

class NoiseAnalyzer {
public:
    NoiseAnalyzer(CircuitAnalyzer& analyzer) : analyzer_(analyzer) {}

    struct NoiseSource {
        enum class Type {
            THERMAL,    // Johnson-Nyquist noise
            SHOT,       // Shot noise
            FLICKER    // 1/f noise
        };
        
        Type type;
        double magnitude;
        std::shared_ptr<Component> component;
    };

    void addNoiseSource(const NoiseSource& source) {
        noise_sources_.push_back(source);
    }

    double calculateTotalNoise(double frequency_start, double frequency_stop) {
        double total_noise = 0.0;
        
        // Integrate noise over frequency range
        double f = frequency_start;
        while (f <= frequency_stop) {
            for (const auto& source : noise_sources_) {
                switch (source.type) {
                    case NoiseSource::Type::THERMAL: {
                        // V_n^2 = 4kTRΔf
                        const double k = 1.380649e-23;  // Boltzmann constant
                        const double T = 300;           // Temperature in Kelvin
                        auto R = std::abs(source.component->getImpedance(f));
                        total_noise += 4 * k * T * R;
                        break;
                    }
                    case NoiseSource::Type::SHOT: {
                        // I_n^2 = 2qIΔf
                        const double q = 1.602176634e-19;  // Elementary charge
                        auto I = std::abs(source.component->getCurrentThrough());
                        total_noise += 2 * q * I;
                        break;
                    }
                    case NoiseSource::Type::FLICKER: {
                        // S(f) = K/f
                        total_noise += source.magnitude / f;
                        break;
                    }
                }
            }
            f *= 1.1;  // Logarithmic frequency steps
        }
        
        return total_noise;
    }

    std::vector<double> calculateNoiseSpectrum(double frequency_start, 
                                             double frequency_stop,
                                             int points) {
        std::vector<double> spectrum;
        double log_start = std::log10(frequency_start);
        double log_stop = std::log10(frequency_stop);
        double step = (log_stop - log_start) / (points - 1);
        
        for (int i = 0; i < points; i++) {
            double f = std::pow(10, log_start + i * step);
            double noise = 0.0;
            
            for (const auto& source : noise_sources_) {
                switch (source.type) {
                    case NoiseSource::Type::THERMAL: {
                        const double k = 1.380649e-23;
                        const double T = 300;
                        auto R = std::abs(source.component->getImpedance(f));
                        noise += 4 * k * T * R;
                        break;
                    }
                    case NoiseSource::Type::SHOT: {
                        const double q = 1.602176634e-19;
                        auto I = std::abs(source.component->getCurrentThrough());
                        noise += 2 * q * I;
                        break;
                    }
                    case NoiseSource::Type::FLICKER: {
                        noise += source.magnitude / f;
                        break;
                    }
                }
            }
            spectrum.push_back(noise);
        }
        
        return spectrum;
    }

private:
    CircuitAnalyzer& analyzer_;
    std::vector<NoiseSource> noise_sources_;
};

class StabilityAnalyzer {
public:
    StabilityAnalyzer(CircuitAnalyzer& analyzer) : analyzer_(analyzer) {}

    struct StabilityMetrics {
        double k_factor;      // Rollett stability factor
        double delta;         // Determinant of S-matrix
        double mu_source;     // Source stability measure
        double mu_load;       // Load stability measure
        bool unconditionally_stable;
    };

    StabilityMetrics analyzeStability(double frequency) {
        StabilityMetrics metrics;
        
        // Calculate S-parameters at given frequency
        auto s_params = calculateSParameters(frequency);
        
        // Calculate K factor
        double s11s11 = std::norm(s_params[0][0]);
        double s22s22 = std::norm(s_params[1][1]);
        double s21s12 = std::norm(s_params[1][0]) * std::norm(s_params[0][1]);
        metrics.delta = s_params[0][0] * s_params[1][1] - 
                       s_params[1][0] * s_params[0][1];
        double delta_sq = std::norm(metrics.delta);
        
        metrics.k_factor = (1 - s11s11 - s22s22 + delta_sq) / (2 * std::sqrt(s21s12));
        
        // Calculate mu factors
        metrics.mu_source = (1 - s11s11) / 
                          (std::abs(s_params[1][1] - std::conj(metrics.delta) * 
                           s_params[0][0]) + std::abs(s_params[1][0] * s_params[0][1]));
        
        metrics.mu_load = (1 - s22s22) /
                        (std::abs(s_params[0][0] - std::conj(metrics.delta) * 
                         s_params[1][1]) + std::abs(s_params[1][0] * s_params[0][1]));
        
        // Check stability conditions
        metrics.unconditionally_stable = (metrics.k_factor > 1) && (delta_sq < 1);
        
        return metrics;
    }

    std::vector<StabilityMetrics> analyzeStabilityVsFrequency(
        double freq_start, double freq_stop, int points) {
        std::vector<StabilityMetrics> results;
        double log_start = std::log10(freq_start);
        double log_stop = std::log10(freq_stop);
        double step = (log_stop - log_start) / (points - 1);
        
        for (int i = 0; i < points; i++) {
            double f = std::pow(10, log_start + i * step);
            results.push_back(analyzeStability(f));
        }
        
        return results;
    }

private:
    std::vector<std::vector<Complex>> calculateSParameters(double frequency) {
        // Initialize S-parameter matrix
        std::vector<std::vector<Complex>> s_params(2, std::vector<Complex>(2));
        
        // Get reference impedance (usually 50 ohms)
        Complex z0(50, 0);
        
        // Calculate Z-parameters
        auto z_params = calculateZParameters(frequency);
        
        // Convert Z to S parameters
        Complex denominator = (z_params[0][0] + z0) * (z_params[1][1] + z0) - 
                            z_params[0][1] * z_params[1][0];
        
        s_params[0][0] = ((z_params[0][0] - z0) * (z_params[1][1] + z0) - 
                         z_params[0][1] * z_params[1][0]) / denominator;
        s_params[0][1] = 2 * z0 * z_params[0][1] / denominator;
        s_params[1][0] = 2 * z0 * z_params[1][0] / denominator;
        s_params[1][1] = ((z_params[0][0] + z0) * (z_params[1][1] - z0) - 
                         z_params[0][1] * z_params[1][0]) / denominator;
        
        return s_params;
    }

    std::vector<std::vector<Complex>> calculateZParameters(double frequency) {
        // Perform circuit analysis at the given frequency
        analyzer_.analyze(frequency);
        
        // Get port voltages and currents
        // This is a simplified version - actual implementation would need to
        // properly identify and measure the ports
        std::vector<std::vector<Complex>> z_params(2, std::vector<Complex>(2));
        
        // Calculate Z-parameters
        // Z11 = V1/I1 with I2=0
        // Z12 = V1/I2 with I1=0
        // Z21 = V2/I1 with I2=0
        // Z22 = V2/I2 with I1=0
        
        return z_params;
    }

    CircuitAnalyzer& analyzer_;
};

class SensitivityAnalyzer {
public:
    SensitivityAnalyzer(CircuitAnalyzer& analyzer) : analyzer_(analyzer) {}

    struct SensitivityResult {
        std::string parameter;
        double nominal_value;
        double sensitivity;
        double tolerance;
        double worst_case_deviation;
    };

    std::vector<SensitivityResult> analyzeSensitivity(
        const std::vector<std::string>& parameters,
        const std::vector<double>& tolerances,
        double frequency) {
        std::vector<SensitivityResult> results;
        
        // Analyze nominal circuit
        analyzer_.analyze(frequency);
        auto nominal_response = analyzer_.getNodeVoltages();
        
        // Calculate sensitivity for each parameter
        for (size_t i = 0; i < parameters.size(); i++) {
            SensitivityResult result;
            result.parameter = parameters[i];
            result.tolerance = tolerances[i];
            
            // Get component and nominal value
            // This is simplified - actual implementation would need to properly
            // identify components and their parameters
            auto component = findComponentByParameter(parameters[i]);
            result.nominal_value = component->getParameter(parameters[i]);
            
            // Calculate sensitivity using finite difference
            double delta = result.nominal_value * 0.01;  // 1% perturbation
            component->setParameter(parameters[i], result.nominal_value + delta);
            analyzer_.analyze(frequency);
            auto perturbed_response = analyzer_.getNodeVoltages();
            
            // Restore nominal value
            component->setParameter(parameters[i], result.nominal_value);
            
            // Calculate sensitivity
            result.sensitivity = std::abs(
                (perturbed_response[0] - nominal_response[0]) / 
                (delta / result.nominal_value)
            );
            
            // Calculate worst-case deviation
            result.worst_case_deviation = result.sensitivity * 
                                        result.tolerance * 
                                        result.nominal_value;
            
            results.push_back(result);
        }
        
        return results;
    }

private:
    std::shared_ptr<Component> findComponentByParameter(const std::string& param) {
        // This is a placeholder - actual implementation would need to
        // properly search through components
        return nullptr;
    }

    CircuitAnalyzer& analyzer_;
};

} // namespace circuit
