#pragma once

#include "CircuitAnalyzer.hpp"
#include <vector>
#include <functional>
#include <random>
#include <algorithm>

namespace circuit {

class RFOptimizer {
public:
    struct Parameter {
        std::string name;
        double min_value;
        double max_value;
        double current_value;
    };

    struct Objective {
        enum class Type {
            MINIMIZE,
            MAXIMIZE,
            TARGET
        };
        
        std::string name;
        Type type;
        double target_value;  // Used for TARGET type
        double weight;
    };

    RFOptimizer(CircuitAnalyzer& analyzer) : analyzer_(analyzer) {
        rng_.seed(std::random_device{}());
    }

    void addParameter(const std::string& name, double min_value, 
                     double max_value, double initial_value) {
        parameters_.push_back({name, min_value, max_value, initial_value});
    }

    void addObjective(const std::string& name, Objective::Type type, 
                     double target_value, double weight) {
        objectives_.push_back({name, type, target_value, weight});
    }

    void setMeasurementFunction(
        std::function<std::vector<double>(const std::vector<Parameter>&)> func) {
        measurement_func_ = func;
    }

    std::vector<Parameter> optimizeGeneticAlgorithm(
        int population_size = 100,
        int generations = 50,
        double mutation_rate = 0.1,
        double crossover_rate = 0.8) {
        
        // Initialize population
        std::vector<std::vector<Parameter>> population;
        for (int i = 0; i < population_size; i++) {
            population.push_back(generateRandomIndividual());
        }

        // Evolution loop
        for (int gen = 0; gen < generations; gen++) {
            // Evaluate fitness
            std::vector<double> fitness;
            for (const auto& individual : population) {
                fitness.push_back(evaluateFitness(individual));
            }

            // Selection
            std::vector<std::vector<Parameter>> new_population;
            while (new_population.size() < population_size) {
                // Tournament selection
                auto parent1 = tournamentSelect(population, fitness);
                auto parent2 = tournamentSelect(population, fitness);

                // Crossover
                std::vector<Parameter> child1 = parent1;
                std::vector<Parameter> child2 = parent2;
                
                if (uniformDist(0.0, 1.0) < crossover_rate) {
                    crossover(child1, child2);
                }

                // Mutation
                mutate(child1, mutation_rate);
                mutate(child2, mutation_rate);

                new_population.push_back(child1);
                if (new_population.size() < population_size) {
                    new_population.push_back(child2);
                }
            }

            population = new_population;
        }

        // Find best solution
        double best_fitness = -std::numeric_limits<double>::infinity();
        std::vector<Parameter> best_solution;
        
        for (const auto& individual : population) {
            double fitness = evaluateFitness(individual);
            if (fitness > best_fitness) {
                best_fitness = fitness;
                best_solution = individual;
            }
        }

        return best_solution;
    }

    std::vector<Parameter> optimizeParticleSwarm(
        int swarm_size = 50,
        int iterations = 100,
        double w = 0.7,     // Inertia weight
        double c1 = 1.4,    // Cognitive parameter
        double c2 = 1.4) {  // Social parameter
        
        // Initialize particles
        std::vector<std::vector<Parameter>> positions;
        std::vector<std::vector<Parameter>> velocities;
        std::vector<std::vector<Parameter>> best_positions;
        std::vector<double> best_fitnesses;
        std::vector<Parameter> global_best;
        double global_best_fitness = -std::numeric_limits<double>::infinity();

        // Initialize swarm
        for (int i = 0; i < swarm_size; i++) {
            positions.push_back(generateRandomIndividual());
            velocities.push_back(generateRandomVelocity());
            best_positions.push_back(positions.back());
            
            double fitness = evaluateFitness(positions.back());
            best_fitnesses.push_back(fitness);
            
            if (fitness > global_best_fitness) {
                global_best_fitness = fitness;
                global_best = positions.back();
            }
        }

        // PSO iterations
        for (int iter = 0; iter < iterations; iter++) {
            for (int i = 0; i < swarm_size; i++) {
                // Update velocity and position
                for (size_t j = 0; j < parameters_.size(); j++) {
                    double r1 = uniformDist(0.0, 1.0);
                    double r2 = uniformDist(0.0, 1.0);

                    velocities[i][j].current_value = 
                        w * velocities[i][j].current_value +
                        c1 * r1 * (best_positions[i][j].current_value - 
                                  positions[i][j].current_value) +
                        c2 * r2 * (global_best[j].current_value - 
                                  positions[i][j].current_value);

                    positions[i][j].current_value += velocities[i][j].current_value;
                    
                    // Clamp to bounds
                    positions[i][j].current_value = std::clamp(
                        positions[i][j].current_value,
                        positions[i][j].min_value,
                        positions[i][j].max_value
                    );
                }

                // Update best positions
                double fitness = evaluateFitness(positions[i]);
                if (fitness > best_fitnesses[i]) {
                    best_fitnesses[i] = fitness;
                    best_positions[i] = positions[i];

                    if (fitness > global_best_fitness) {
                        global_best_fitness = fitness;
                        global_best = positions[i];
                    }
                }
            }
        }

        return global_best;
    }

private:
    std::vector<Parameter> generateRandomIndividual() {
        std::vector<Parameter> individual = parameters_;
        for (auto& param : individual) {
            param.current_value = uniformDist(param.min_value, param.max_value);
        }
        return individual;
    }

    std::vector<Parameter> generateRandomVelocity() {
        std::vector<Parameter> velocity = parameters_;
        for (auto& param : velocity) {
            double range = param.max_value - param.min_value;
            param.current_value = uniformDist(-range/10, range/10);
        }
        return velocity;
    }

    double evaluateFitness(const std::vector<Parameter>& individual) {
        // Apply parameters to circuit
        for (const auto& param : individual) {
            // Find component and set parameter
            // This is simplified - actual implementation would need to
            // properly identify components and their parameters
        }

        // Get measurements
        auto measurements = measurement_func_(individual);

        // Calculate fitness
        double fitness = 0.0;
        for (size_t i = 0; i < objectives_.size(); i++) {
            const auto& obj = objectives_[i];
            double value = measurements[i];
            
            switch (obj.type) {
                case Objective::Type::MINIMIZE:
                    fitness -= obj.weight * value;
                    break;
                case Objective::Type::MAXIMIZE:
                    fitness += obj.weight * value;
                    break;
                case Objective::Type::TARGET:
                    fitness -= obj.weight * std::abs(value - obj.target_value);
                    break;
            }
        }

        return fitness;
    }

    std::vector<Parameter> tournamentSelect(
        const std::vector<std::vector<Parameter>>& population,
        const std::vector<double>& fitness,
        int tournament_size = 3) {
        
        std::vector<size_t> tournament;
        for (int i = 0; i < tournament_size; i++) {
            tournament.push_back(
                static_cast<size_t>(uniformDist(0, population.size() - 1))
            );
        }

        size_t winner = tournament[0];
        double best_fitness = fitness[tournament[0]];

        for (size_t i = 1; i < tournament.size(); i++) {
            if (fitness[tournament[i]] > best_fitness) {
                winner = tournament[i];
                best_fitness = fitness[tournament[i]];
            }
        }

        return population[winner];
    }

    void crossover(std::vector<Parameter>& child1, 
                  std::vector<Parameter>& child2) {
        for (size_t i = 0; i < parameters_.size(); i++) {
            if (uniformDist(0.0, 1.0) < 0.5) {
                std::swap(child1[i].current_value, child2[i].current_value);
            }
        }
    }

    void mutate(std::vector<Parameter>& individual, double mutation_rate) {
        for (auto& param : individual) {
            if (uniformDist(0.0, 1.0) < mutation_rate) {
                param.current_value = uniformDist(param.min_value, param.max_value);
            }
        }
    }

    double uniformDist(double min, double max) {
        return std::uniform_real_distribution<double>(min, max)(rng_);
    }

    CircuitAnalyzer& analyzer_;
    std::vector<Parameter> parameters_;
    std::vector<Objective> objectives_;
    std::function<std::vector<double>(const std::vector<Parameter>&)> measurement_func_;
    std::mt19937 rng_;
};

} // namespace circuit
