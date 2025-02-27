#pragma once

#include <vector>
#include <memory>
#include <map>
#include <string>
#include <cmath>
#include <algorithm>

namespace circuit {

// Forward declarations
class Component;
class Material;
class ProcessingUnit;

class RecyclingSystem {
public:
    enum class MaterialType {
        METAL_PRECIOUS,
        METAL_BASE,
        SEMICONDUCTOR,
        CERAMIC,
        POLYMER,
        COMPOSITE,
        RARE_EARTH
    };

    enum class ProcessType {
        MECHANICAL,
        THERMAL,
        CHEMICAL,
        ELECTROMAGNETIC,
        ELECTROCHEMICAL
    };

    struct MaterialProperties {
        double purity;                // 0.0 to 1.0
        double quantity;              // kg
        double marketValue;           // $/kg
        double recoveryEfficiency;    // 0.0 to 1.0
        std::vector<std::string> contaminants;
    };

    struct ProcessParameters {
        double temperature;           // Kelvin
        double pressure;             // Pascal
        double pH;                   // 0-14
        double energyConsumption;    // kWh
        double processTime;          // seconds
        std::map<std::string, double> chemicalConcentrations; // mol/L
    };

    class RecyclableComponent {
    public:
        RecyclableComponent(const Component* component) 
            : component_(component) {
            analyzeMaterialComposition();
        }

        void analyzeMaterialComposition() {
            // Analyze component materials and populate material_composition_
            for (const auto& material : detectMaterials()) {
                material_composition_[material.first] = material.second;
            }
        }

        double getRecoveryValue() const {
            double total_value = 0.0;
            for (const auto& [material, properties] : material_composition_) {
                total_value += properties.quantity * 
                             properties.marketValue * 
                             properties.recoveryEfficiency;
            }
            return total_value;
        }

        const std::map<MaterialType, MaterialProperties>& getMaterialComposition() const {
            return material_composition_;
        }

    private:
        std::map<MaterialType, MaterialProperties> detectMaterials() const;
        const Component* component_;
        std::map<MaterialType, MaterialProperties> material_composition_;
    };

    class ProcessingUnit {
    public:
        ProcessingUnit(ProcessType type, const ProcessParameters& params)
            : type_(type), params_(params) {}

        virtual double process(const MaterialProperties& input, 
                             MaterialProperties& output) = 0;

        virtual double getEfficiency() const {
            return calculateEfficiency(params_);
        }

        virtual double getOperatingCost() const {
            return calculateOperatingCost(params_);
        }

    protected:
        ProcessType type_;
        ProcessParameters params_;

        virtual double calculateEfficiency(const ProcessParameters& params) const {
            // Base efficiency calculation
            double base_efficiency = 0.85; // 85% base efficiency
            
            // Temperature effect
            double temp_factor = std::exp(-(params.temperature - 298.15) / 1000.0);
            
            // Pressure effect
            double pressure_factor = std::log10(params.pressure / 101325.0 + 1.0);
            
            // Time effect
            double time_factor = 1.0 - std::exp(-params.processTime / 3600.0);
            
            return base_efficiency * temp_factor * pressure_factor * time_factor;
        }

        virtual double calculateOperatingCost(const ProcessParameters& params) const {
            // Base cost per hour of operation
            double base_cost = 100.0; // $100/hour base cost
            
            // Energy cost
            double energy_cost = params.energyConsumption * 0.15; // $0.15 per kWh
            
            // Chemical cost
            double chemical_cost = 0.0;
            for (const auto& [chemical, concentration] : params.chemicalConcentrations) {
                chemical_cost += concentration * getChemicalCost(chemical);
            }
            
            // Time-based cost
            double time_cost = (params.processTime / 3600.0) * base_cost;
            
            return energy_cost + chemical_cost + time_cost;
        }

        double getChemicalCost(const std::string& chemical) const {
            // Chemical cost database ($/mol)
            static const std::map<std::string, double> chemical_costs = {
                {"HNO3", 0.5},
                {"H2SO4", 0.3},
                {"HCl", 0.4},
                {"NaOH", 0.2},
                {"HF", 1.0}
            };
            
            auto it = chemical_costs.find(chemical);
            return (it != chemical_costs.end()) ? it->second : 1.0;
        }
    };

    class MechanicalProcessor : public ProcessingUnit {
    public:
        MechanicalProcessor(const ProcessParameters& params)
            : ProcessingUnit(ProcessType::MECHANICAL, params) {}

        double process(const MaterialProperties& input,
                      MaterialProperties& output) override {
            // Implement mechanical processing (shredding, sorting, etc.)
            output.purity = input.purity * getEfficiency();
            output.quantity = input.quantity * 0.95; // 5% material loss
            output.recoveryEfficiency = calculateRecoveryEfficiency();
            return getOperatingCost();
        }

    private:
        double calculateRecoveryEfficiency() const {
            return 0.90 + 0.05 * std::log10(params_.energyConsumption);
        }
    };

    class ThermalProcessor : public ProcessingUnit {
    public:
        ThermalProcessor(const ProcessParameters& params)
            : ProcessingUnit(ProcessType::THERMAL, params) {}

        double process(const MaterialProperties& input,
                      MaterialProperties& output) override {
            // Implement thermal processing (smelting, pyrolysis, etc.)
            output.purity = input.purity * getEfficiency();
            output.quantity = input.quantity * 0.98; // 2% material loss
            output.recoveryEfficiency = calculateRecoveryEfficiency();
            return getOperatingCost();
        }

    private:
        double calculateRecoveryEfficiency() const {
            return 0.95 * (1.0 - std::exp(-params_.temperature / 1000.0));
        }
    };

    class ChemicalProcessor : public ProcessingUnit {
    public:
        ChemicalProcessor(const ProcessParameters& params)
            : ProcessingUnit(ProcessType::CHEMICAL, params) {}

        double process(const MaterialProperties& input,
                      MaterialProperties& output) override {
            // Implement chemical processing (leaching, precipitation, etc.)
            output.purity = input.purity * getEfficiency();
            output.quantity = input.quantity * 0.97; // 3% material loss
            output.recoveryEfficiency = calculateRecoveryEfficiency();
            return getOperatingCost();
        }

    private:
        double calculateRecoveryEfficiency() const {
            double ph_factor = std::exp(-std::pow(params_.pH - 7.0, 2) / 10.0);
            return 0.92 * ph_factor;
        }
    };

    class ElectromagneticProcessor : public ProcessingUnit {
    public:
        ElectromagneticProcessor(const ProcessParameters& params)
            : ProcessingUnit(ProcessType::ELECTROMAGNETIC, params) {}

        double process(const MaterialProperties& input,
                      MaterialProperties& output) override {
            // Implement electromagnetic processing (eddy current separation, etc.)
            output.purity = input.purity * getEfficiency();
            output.quantity = input.quantity * 0.99; // 1% material loss
            output.recoveryEfficiency = calculateRecoveryEfficiency();
            return getOperatingCost();
        }

    private:
        double calculateRecoveryEfficiency() const {
            return 0.88 + 0.10 * std::log10(params_.energyConsumption);
        }
    };

    class ElectrochemicalProcessor : public ProcessingUnit {
    public:
        ElectrochemicalProcessor(const ProcessParameters& params)
            : ProcessingUnit(ProcessType::ELECTROCHEMICAL, params) {}

        double process(const MaterialProperties& input,
                      MaterialProperties& output) override {
            // Implement electrochemical processing (electrolysis, electrowinning, etc.)
            output.purity = input.purity * getEfficiency();
            output.quantity = input.quantity * 0.96; // 4% material loss
            output.recoveryEfficiency = calculateRecoveryEfficiency();
            return getOperatingCost();
        }

    private:
        double calculateRecoveryEfficiency() const {
            return 0.94 * (1.0 - std::exp(-params_.energyConsumption / 100.0));
        }
    };

    // Main recycling system methods
    RecyclingSystem() {
        initializeProcessors();
    }

    void addComponent(const Component* component) {
        recyclable_components_.emplace_back(component);
    }

    double processComponents() {
        double total_cost = 0.0;
        double total_value = 0.0;

        for (const auto& recyclable : recyclable_components_) {
            for (const auto& [material_type, properties] : recyclable.getMaterialComposition()) {
                MaterialProperties output_properties;
                double process_cost = processeMaterial(material_type, properties, output_properties);
                total_cost += process_cost;
                total_value += output_properties.quantity * 
                              output_properties.marketValue * 
                              output_properties.recoveryEfficiency;
            }
        }

        return total_value - total_cost;
    }

    std::vector<std::pair<MaterialType, MaterialProperties>> getRecoveredMaterials() const {
        return recovered_materials_;
    }

private:
    std::vector<RecyclableComponent> recyclable_components_;
    std::vector<std::unique_ptr<ProcessingUnit>> processors_;
    std::vector<std::pair<MaterialType, MaterialProperties>> recovered_materials_;

    void initializeProcessors() {
        // Initialize different types of processors with default parameters
        ProcessParameters mechanical_params{298.15, 101325, 7.0, 50.0, 1800.0};
        ProcessParameters thermal_params{1273.15, 101325, 7.0, 200.0, 3600.0};
        ProcessParameters chemical_params{298.15, 101325, 2.0, 100.0, 7200.0};
        ProcessParameters electromagnetic_params{298.15, 101325, 7.0, 75.0, 1200.0};
        ProcessParameters electrochemical_params{298.15, 101325, 1.0, 150.0, 5400.0};

        processors_.push_back(std::make_unique<MechanicalProcessor>(mechanical_params));
        processors_.push_back(std::make_unique<ThermalProcessor>(thermal_params));
        processors_.push_back(std::make_unique<ChemicalProcessor>(chemical_params));
        processors_.push_back(std::make_unique<ElectromagneticProcessor>(electromagnetic_params));
        processors_.push_back(std::make_unique<ElectrochemicalProcessor>(electrochemical_params));
    }

    double processeMaterial(MaterialType type, 
                          const MaterialProperties& input,
                          MaterialProperties& output) {
        double total_cost = 0.0;

        // Select appropriate processors based on material type
        std::vector<ProcessingUnit*> process_chain = selectProcessChain(type);

        // Process through the chain
        MaterialProperties intermediate = input;
        for (auto* processor : process_chain) {
            total_cost += processor->process(intermediate, output);
            intermediate = output;
        }

        // Store recovered material
        recovered_materials_.push_back({type, output});

        return total_cost;
    }

    std::vector<ProcessingUnit*> selectProcessChain(MaterialType type) {
        std::vector<ProcessingUnit*> chain;

        switch (type) {
            case MaterialType::METAL_PRECIOUS:
                chain = {
                    processors_[0].get(), // Mechanical
                    processors_[2].get(), // Chemical
                    processors_[4].get()  // Electrochemical
                };
                break;

            case MaterialType::METAL_BASE:
                chain = {
                    processors_[0].get(), // Mechanical
                    processors_[1].get(), // Thermal
                    processors_[4].get()  // Electrochemical
                };
                break;

            case MaterialType::SEMICONDUCTOR:
                chain = {
                    processors_[0].get(), // Mechanical
                    processors_[2].get(), // Chemical
                    processors_[3].get()  // Electromagnetic
                };
                break;

            case MaterialType::CERAMIC:
                chain = {
                    processors_[0].get(), // Mechanical
                    processors_[1].get()  // Thermal
                };
                break;

            case MaterialType::POLYMER:
                chain = {
                    processors_[0].get(), // Mechanical
                    processors_[1].get()  // Thermal
                };
                break;

            case MaterialType::COMPOSITE:
                chain = {
                    processors_[0].get(), // Mechanical
                    processors_[2].get(), // Chemical
                    processors_[1].get()  // Thermal
                };
                break;

            case MaterialType::RARE_EARTH:
                chain = {
                    processors_[0].get(), // Mechanical
                    processors_[2].get(), // Chemical
                    processors_[4].get()  // Electrochemical
                };
                break;
        }

        return chain;
    }
};

} // namespace circuit
