#pragma once

#include "CircuitAnalyzer.hpp"
#include "BasicComponents.hpp"
#include <vector>
#include <complex>
#include <memory>

namespace circuit {

class FilterDesigner {
public:
    enum class FilterType {
        LOWPASS,
        HIGHPASS,
        BANDPASS,
        BANDSTOP,
        ALLPASS
    };

    enum class ApproximationType {
        BUTTERWORTH,
        CHEBYSHEV_I,
        CHEBYSHEV_II,
        ELLIPTIC,
        BESSEL
    };

    struct FilterSpecification {
        FilterType type;
        ApproximationType approximation;
        int order;
        double passband_freq;      // Hz
        double stopband_freq;      // Hz
        double passband_ripple;    // dB
        double stopband_atten;     // dB
        double impedance;          // Ohms
    };

    struct FilterResponse {
        std::vector<double> frequencies;
        std::vector<double> magnitude;    // dB
        std::vector<double> phase;        // degrees
        std::vector<double> group_delay;  // seconds
        double bandwidth;                 // Hz
        double q_factor;
    };

    FilterDesigner(CircuitAnalyzer& analyzer) : analyzer_(analyzer) {}

    std::vector<std::shared_ptr<Component>> designFilter(
        const FilterSpecification& spec) {
        std::vector<std::shared_ptr<Component>> components;
        
        // Calculate normalized filter coefficients
        auto coeffs = calculateCoefficients(spec);
        
        // Denormalize to actual frequency and impedance
        auto denorm_coeffs = denormalizeCoefficients(coeffs, spec);
        
        // Create components based on filter type
        switch (spec.type) {
            case FilterType::LOWPASS:
                components = createLowPassFilter(denorm_coeffs, spec);
                break;
            case FilterType::HIGHPASS:
                components = createHighPassFilter(denorm_coeffs, spec);
                break;
            case FilterType::BANDPASS:
                components = createBandPassFilter(denorm_coeffs, spec);
                break;
            case FilterType::BANDSTOP:
                components = createBandStopFilter(denorm_coeffs, spec);
                break;
            case FilterType::ALLPASS:
                components = createAllPassFilter(denorm_coeffs, spec);
                break;
        }
        
        return components;
    }

    FilterResponse analyzeFilter(const std::vector<double>& frequencies) {
        FilterResponse response;
        response.frequencies = frequencies;
        
        for (double f : frequencies) {
            analyzer_.analyze(f);
            auto transfer = calculateTransferFunction();
            
            response.magnitude.push_back(20 * std::log10(std::abs(transfer)));
            response.phase.push_back(std::arg(transfer) * 180.0 / M_PI);
            
            // Calculate group delay
            const double df = f * 0.01;  // Small frequency step
            analyzer_.analyze(f + df);
            auto transfer_plus = calculateTransferFunction();
            
            double phase_diff = std::arg(transfer_plus) - std::arg(transfer);
            response.group_delay.push_back(-phase_diff / (2 * M_PI * df));
        }
        
        // Calculate bandwidth and Q factor
        calculateBandwidthAndQ(response);
        
        return response;
    }

private:
    std::vector<double> calculateCoefficients(const FilterSpecification& spec) {
        std::vector<double> coeffs;
        
        switch (spec.approximation) {
            case ApproximationType::BUTTERWORTH:
                coeffs = calculateButterworthCoeffs(spec.order);
                break;
            case ApproximationType::CHEBYSHEV_I:
                coeffs = calculateChebyshevICoeffs(spec.order, spec.passband_ripple);
                break;
            case ApproximationType::CHEBYSHEV_II:
                coeffs = calculateChebyshevIICoeffs(spec.order, spec.stopband_atten);
                break;
            case ApproximationType::ELLIPTIC:
                coeffs = calculateEllipticCoeffs(spec.order, 
                                               spec.passband_ripple,
                                               spec.stopband_atten);
                break;
            case ApproximationType::BESSEL:
                coeffs = calculateBesselCoeffs(spec.order);
                break;
        }
        
        return coeffs;
    }

    std::vector<double> calculateButterworthCoeffs(int order) {
        std::vector<double> coeffs;
        for (int i = 0; i < order; i++) {
            double angle = M_PI * (2.0 * i + 1) / (2.0 * order);
            coeffs.push_back(2 * std::sin(angle));
        }
        return coeffs;
    }

    std::vector<double> calculateChebyshevICoeffs(int order, double ripple) {
        std::vector<double> coeffs;
        double eps = std::sqrt(std::pow(10, ripple/10) - 1);
        
        for (int i = 0; i < order; i++) {
            double angle = M_PI * (2.0 * i + 1) / (2.0 * order);
            double sinh = std::sinh(std::asinh(1/eps) / order);
            double cosh = std::cosh(std::asinh(1/eps) / order);
            coeffs.push_back(2 * std::sin(angle) * sinh);
        }
        return coeffs;
    }

    std::vector<double> denormalizeCoefficients(
        const std::vector<double>& coeffs,
        const FilterSpecification& spec) {
        std::vector<double> denorm_coeffs;
        
        double omega_c = 2 * M_PI * spec.passband_freq;
        
        for (double coeff : coeffs) {
            switch (spec.type) {
                case FilterType::LOWPASS:
                    denorm_coeffs.push_back(coeff / omega_c);
                    break;
                case FilterType::HIGHPASS:
                    denorm_coeffs.push_back(1 / (coeff * omega_c));
                    break;
                case FilterType::BANDPASS:
                case FilterType::BANDSTOP: {
                    double omega_0 = 2 * M_PI * std::sqrt(spec.passband_freq * 
                                                        spec.stopband_freq);
                    double bw = 2 * M_PI * (spec.stopband_freq - spec.passband_freq);
                    denorm_coeffs.push_back(coeff * bw / omega_0);
                    break;
                }
                case FilterType::ALLPASS:
                    denorm_coeffs.push_back(coeff / omega_c);
                    break;
            }
        }
        
        return denorm_coeffs;
    }

    std::vector<std::shared_ptr<Component>> createLowPassFilter(
        const std::vector<double>& coeffs,
        const FilterSpecification& spec) {
        std::vector<std::shared_ptr<Component>> components;
        
        // Create ladder network
        bool use_inductor = true;
        for (size_t i = 0; i < coeffs.size(); i++) {
            if (use_inductor) {
                auto L = std::make_shared<Inductor>(
                    "L" + std::to_string(i+1),
                    coeffs[i] * spec.impedance
                );
                components.push_back(L);
            } else {
                auto C = std::make_shared<Capacitor>(
                    "C" + std::to_string(i+1),
                    coeffs[i] / spec.impedance
                );
                components.push_back(C);
            }
            use_inductor = !use_inductor;
        }
        
        return components;
    }

    std::vector<std::shared_ptr<Component>> createHighPassFilter(
        const std::vector<double>& coeffs,
        const FilterSpecification& spec) {
        std::vector<std::shared_ptr<Component>> components;
        
        // Create ladder network (dual of lowpass)
        bool use_capacitor = true;
        for (size_t i = 0; i < coeffs.size(); i++) {
            if (use_capacitor) {
                auto C = std::make_shared<Capacitor>(
                    "C" + std::to_string(i+1),
                    coeffs[i] / spec.impedance
                );
                components.push_back(C);
            } else {
                auto L = std::make_shared<Inductor>(
                    "L" + std::to_string(i+1),
                    coeffs[i] * spec.impedance
                );
                components.push_back(L);
            }
            use_capacitor = !use_capacitor;
        }
        
        return components;
    }

    Complex calculateTransferFunction() {
        // Get input and output voltages
        auto v_in = analyzer_.getNodeVoltages()[0];
        auto v_out = analyzer_.getNodeVoltages().back();
        
        return v_out / v_in;
    }

    void calculateBandwidthAndQ(FilterResponse& response) {
        // Find -3dB points
        double max_mag = *std::max_element(response.magnitude.begin(),
                                         response.magnitude.end());
        
        std::vector<double> cutoff_freqs;
        for (size_t i = 0; i < response.frequencies.size() - 1; i++) {
            if (std::abs(response.magnitude[i] - (max_mag - 3)) < 0.1) {
                cutoff_freqs.push_back(response.frequencies[i]);
            }
        }
        
        if (cutoff_freqs.size() >= 2) {
            response.bandwidth = cutoff_freqs[1] - cutoff_freqs[0];
            double center_freq = std::sqrt(cutoff_freqs[0] * cutoff_freqs[1]);
            response.q_factor = center_freq / response.bandwidth;
        }
    }

    CircuitAnalyzer& analyzer_;
};

} // namespace circuit
