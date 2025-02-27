#pragma once

#include "RFOptimizer.hpp"
#include <vector>
#include <random>
#include <algorithm>
#include <cmath>

namespace circuit {

class DifferentialEvolution : public RFOptimizer {
public:
    DifferentialEvolution(CircuitAnalyzer& analyzer) 
        : RFOptimizer(analyzer) {}

    std::vector<Parameter> optimize(
        int population_size = 50,
        int generations = 100,
        double F = 0.8,      // Differential weight
        double CR = 0.9) {   // Crossover probability
        
        // Initialize population
        std::vector<std::vector<Parameter>> population;
        std::vector<double> fitness;
        
        for (int i = 0; i < population_size; i++) {
            population.push_back(generateRandomIndividual());
            fitness.push_back(evaluateFitness(population.back()));
        }

        // Evolution loop
        for (int gen = 0; gen < generations; gen++) {
            for (int i = 0; i < population_size; i++) {
                // Select three random distinct vectors
                int r1, r2, r3;
                do {
                    r1 = uniformInt(0, population_size - 1);
                    r2 = uniformInt(0, population_size - 1);
                    r3 = uniformInt(0, population_size - 1);
                } while (r1 == r2 || r2 == r3 || r1 == r3 || r1 == i || r2 == i || r3 == i);

                // Create trial vector
                std::vector<Parameter> trial = population[i];
                int R = uniformInt(0, parameters_.size() - 1);

                for (size_t j = 0; j < parameters_.size(); j++) {
                    if (uniformReal(0, 1) < CR || j == R) {
                        trial[j].current_value = 
                            population[r1][j].current_value + 
                            F * (population[r2][j].current_value - 
                                 population[r3][j].current_value);
                        
                        // Bound constraints
                        trial[j].current_value = std::clamp(
                            trial[j].current_value,
                            trial[j].min_value,
                            trial[j].max_value
                        );
                    }
                }

                // Selection
                double trial_fitness = evaluateFitness(trial);
                if (trial_fitness > fitness[i]) {
                    population[i] = trial;
                    fitness[i] = trial_fitness;
                }
            }
        }

        // Return best solution
        auto best_it = std::max_element(fitness.begin(), fitness.end());
        return population[std::distance(fitness.begin(), best_it)];
    }
};

class SimulatedAnnealing : public RFOptimizer {
public:
    SimulatedAnnealing(CircuitAnalyzer& analyzer) 
        : RFOptimizer(analyzer) {}

    std::vector<Parameter> optimize(
        double initial_temp = 100.0,
        double final_temp = 1e-5,
        double cooling_rate = 0.95,
        int iterations_per_temp = 50) {
        
        // Initialize current solution
        auto current = generateRandomIndividual();
        double current_energy = -evaluateFitness(current);
        
        auto best = current;
        double best_energy = current_energy;
        
        // Annealing loop
        double temp = initial_temp;
        while (temp > final_temp) {
            for (int i = 0; i < iterations_per_temp; i++) {
                // Generate neighbor
                auto neighbor = generateNeighbor(current, temp);
                double neighbor_energy = -evaluateFitness(neighbor);
                
                // Calculate acceptance probability
                double delta_e = neighbor_energy - current_energy;
                double accept_prob = std::exp(-delta_e / temp);
                
                // Accept or reject
                if (delta_e < 0 || uniformReal(0, 1) < accept_prob) {
                    current = neighbor;
                    current_energy = neighbor_energy;
                    
                    // Update best
                    if (current_energy < best_energy) {
                        best = current;
                        best_energy = current_energy;
                    }
                }
            }
            
            // Cool down
            temp *= cooling_rate;
        }
        
        return best;
    }

private:
    std::vector<Parameter> generateNeighbor(
        const std::vector<Parameter>& current,
        double temp) {
        std::vector<Parameter> neighbor = current;
        
        // Perturb parameters based on temperature
        for (auto& param : neighbor) {
            double range = (param.max_value - param.min_value) * temp / 100.0;
            param.current_value += uniformReal(-range, range);
            param.current_value = std::clamp(
                param.current_value,
                param.min_value,
                param.max_value
            );
        }
        
        return neighbor;
    }
};

class NelderMead : public RFOptimizer {
public:
    NelderMead(CircuitAnalyzer& analyzer) 
        : RFOptimizer(analyzer) {}

    std::vector<Parameter> optimize(
        double alpha = 1.0,    // Reflection coefficient
        double gamma = 2.0,    // Expansion coefficient
        double rho = 0.5,      // Contraction coefficient
        double sigma = 0.5,    // Shrink coefficient
        double tolerance = 1e-6,
        int max_iterations = 1000) {
        
        // Initialize simplex
        std::vector<std::vector<Parameter>> simplex;
        std::vector<double> values;
        
        // Initial point
        simplex.push_back(generateRandomIndividual());
        values.push_back(-evaluateFitness(simplex[0]));
        
        // Generate other points
        for (size_t i = 0; i < parameters_.size(); i++) {
            auto point = simplex[0];
            point[i].current_value += 0.05 * (point[i].max_value - 
                                            point[i].min_value);
            point[i].current_value = std::clamp(
                point[i].current_value,
                point[i].min_value,
                point[i].max_value
            );
            
            simplex.push_back(point);
            values.push_back(-evaluateFitness(point));
        }
        
        // Main loop
        int iterations = 0;
        while (iterations < max_iterations) {
            // Order
            std::vector<size_t> order(simplex.size());
            std::iota(order.begin(), order.end(), 0);
            std::sort(order.begin(), order.end(),
                     [&values](size_t i1, size_t i2) {
                         return values[i1] < values[i2];
                     });
            
            // Check convergence
            double range = values[order.back()] - values[order.front()];
            if (range < tolerance) break;
            
            // Calculate centroid
            std::vector<Parameter> centroid = simplex[order[0]];
            for (size_t i = 1; i < order.size() - 1; i++) {
                for (size_t j = 0; j < parameters_.size(); j++) {
                    centroid[j].current_value += simplex[order[i]][j].current_value;
                }
            }
            for (auto& param : centroid) {
                param.current_value /= (order.size() - 1);
            }
            
            // Reflection
            auto reflected = reflect(centroid, simplex[order.back()], alpha);
            double reflected_value = -evaluateFitness(reflected);
            
            if (reflected_value < values[order[order.size()-2]] &&
                reflected_value >= values[order[0]]) {
                simplex[order.back()] = reflected;
                values[order.back()] = reflected_value;
            }
            // Expansion
            else if (reflected_value < values[order[0]]) {
                auto expanded = reflect(centroid, simplex[order.back()], gamma);
                double expanded_value = -evaluateFitness(expanded);
                
                if (expanded_value < reflected_value) {
                    simplex[order.back()] = expanded;
                    values[order.back()] = expanded_value;
                } else {
                    simplex[order.back()] = reflected;
                    values[order.back()] = reflected_value;
                }
            }
            // Contraction
            else {
                auto contracted = reflect(centroid, simplex[order.back()], -rho);
                double contracted_value = -evaluateFitness(contracted);
                
                if (contracted_value < values[order.back()]) {
                    simplex[order.back()] = contracted;
                    values[order.back()] = contracted_value;
                }
                // Shrink
                else {
                    for (size_t i = 1; i < simplex.size(); i++) {
                        for (size_t j = 0; j < parameters_.size(); j++) {
                            simplex[i][j].current_value = 
                                simplex[0][j].current_value + 
                                sigma * (simplex[i][j].current_value - 
                                       simplex[0][j].current_value);
                        }
                        values[i] = -evaluateFitness(simplex[i]);
                    }
                }
            }
            
            iterations++;
        }
        
        // Return best point
        auto best_it = std::min_element(values.begin(), values.end());
        return simplex[std::distance(values.begin(), best_it)];
    }

private:
    std::vector<Parameter> reflect(
        const std::vector<Parameter>& centroid,
        const std::vector<Parameter>& point,
        double coefficient) {
        std::vector<Parameter> result = centroid;
        
        for (size_t i = 0; i < parameters_.size(); i++) {
            result[i].current_value = centroid[i].current_value + 
                coefficient * (centroid[i].current_value - point[i].current_value);
            result[i].current_value = std::clamp(
                result[i].current_value,
                result[i].min_value,
                result[i].max_value
            );
        }
        
        return result;
    }
};

} // namespace circuit
