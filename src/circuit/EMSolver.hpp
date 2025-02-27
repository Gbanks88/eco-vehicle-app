#pragma once

#include <vector>
#include <complex>
#include <memory>
#include <Eigen/Dense>

namespace circuit {

struct Point3D {
    double x, y, z;
};

struct Vector3D {
    double x, y, z;
    
    Vector3D operator+(const Vector3D& other) const {
        return {x + other.x, y + other.y, z + other.z};
    }
    
    Vector3D operator*(double scalar) const {
        return {x * scalar, y * scalar, z * scalar};
    }
};

class EMField {
public:
    EMField(const Point3D& point, const Vector3D& e_field, const Vector3D& h_field)
        : point_(point), e_field_(e_field), h_field_(h_field) {}
    
    Vector3D getPoyntingVector() const {
        return {
            e_field_.y * h_field_.z - e_field_.z * h_field_.y,
            e_field_.z * h_field_.x - e_field_.x * h_field_.z,
            e_field_.x * h_field_.y - e_field_.y * h_field_.x
        };
    }
    
    double getEFieldMagnitude() const {
        return std::sqrt(e_field_.x * e_field_.x + 
                        e_field_.y * e_field_.y + 
                        e_field_.z * e_field_.z);
    }
    
    double getHFieldMagnitude() const {
        return std::sqrt(h_field_.x * h_field_.x + 
                        h_field_.y * h_field_.y + 
                        h_field_.z * h_field_.z);
    }

private:
    Point3D point_;
    Vector3D e_field_;
    Vector3D h_field_;
};

class EMSolver {
public:
    struct Material {
        double epsilon_r;     // Relative permittivity
        double mu_r;         // Relative permeability
        double sigma;        // Conductivity
        double loss_tangent; // Loss tangent
    };
    
    struct Mesh {
        std::vector<Point3D> nodes;
        std::vector<std::vector<size_t>> elements;
        std::vector<Material> materials;
    };
    
    EMSolver(const Mesh& mesh, double frequency)
        : mesh_(mesh), frequency_(frequency) {
        setupMatrices();
    }
    
    void solve() {
        // Solve FEM equations
        Eigen::VectorXcd solution = A_.colPivHouseholderQr().solve(b_);
        
        // Extract E and H fields from solution
        extractFields(solution);
    }
    
    std::vector<EMField> getFields() const {
        return fields_;
    }
    
    double calculateQFactor(const std::vector<Point3D>& region) const {
        double stored_energy = 0.0;
        double power_loss = 0.0;
        
        for (const auto& field : fields_) {
            // Calculate stored energy
            double e_energy = epsilon_0_ * field.getEFieldMagnitude() * 
                            field.getEFieldMagnitude() / 2;
            double h_energy = mu_0_ * field.getHFieldMagnitude() * 
                            field.getHFieldMagnitude() / 2;
            stored_energy += e_energy + h_energy;
            
            // Calculate power loss
            auto s = field.getPoyntingVector();
            power_loss += std::sqrt(s.x * s.x + s.y * s.y + s.z * s.z);
        }
        
        return 2 * M_PI * frequency_ * stored_energy / power_loss;
    }
    
    std::vector<double> calculateSParameters() const {
        std::vector<double> s_params;
        
        // Calculate S-parameters from field solutions
        // This is a simplified version - actual implementation would be more complex
        for (const auto& field : fields_) {
            auto incident = field.getEFieldMagnitude();
            auto reflected = field.getHFieldMagnitude() * std::sqrt(mu_0_ / epsilon_0_);
            s_params.push_back(reflected / incident);
        }
        
        return s_params;
    }
    
    void addPort(const Point3D& position, const Vector3D& normal) {
        ports_.push_back({position, normal});
        setupMatrices();  // Rebuild matrices with new port
    }
    
    void setFrequency(double frequency) {
        frequency_ = frequency;
        setupMatrices();
    }
    
    void setBoundaryCondition(const Point3D& point, const Vector3D& condition) {
        boundary_conditions_.push_back({point, condition});
        setupMatrices();
    }

private:
    void setupMatrices() {
        size_t n = mesh_.nodes.size();
        A_ = Eigen::MatrixXcd::Zero(n, n);
        b_ = Eigen::VectorXcd::Zero(n);
        
        // Set up FEM matrices
        double omega = 2 * M_PI * frequency_;
        
        for (size_t i = 0; i < mesh_.elements.size(); i++) {
            const auto& element = mesh_.elements[i];
            const auto& material = mesh_.materials[i];
            
            // Calculate element matrices
            auto Ke = calculateElementStiffnessMatrix(element, material);
            auto Me = calculateElementMassMatrix(element, material);
            
            // Assemble global matrices
            for (size_t j = 0; j < element.size(); j++) {
                for (size_t k = 0; k < element.size(); k++) {
                    Complex value = Ke(j,k) - omega * omega * Me(j,k);
                    A_(element[j], element[k]) += value;
                }
            }
        }
        
        // Apply boundary conditions
        for (const auto& bc : boundary_conditions_) {
            // Find nearest node and apply condition
            size_t node = findNearestNode(bc.first);
            b_(node) = Complex(bc.second.x, bc.second.y);
        }
        
        // Apply port conditions
        for (const auto& port : ports_) {
            size_t node = findNearestNode(port.first);
            // Set port excitation
            b_(node) = Complex(1.0, 0.0);  // Unit excitation
        }
    }
    
    Eigen::MatrixXcd calculateElementStiffnessMatrix(
        const std::vector<size_t>& element,
        const Material& material) {
        // Calculate element stiffness matrix using FEM shape functions
        size_t n = element.size();
        Eigen::MatrixXcd Ke(n, n);
        
        // This is a simplified version - actual implementation would use
        // proper FEM shape functions and numerical integration
        for (size_t i = 0; i < n; i++) {
            for (size_t j = 0; j < n; j++) {
                Ke(i,j) = Complex(material.epsilon_r * epsilon_0_, 
                                -material.sigma / (2 * M_PI * frequency_));
            }
        }
        
        return Ke;
    }
    
    Eigen::MatrixXcd calculateElementMassMatrix(
        const std::vector<size_t>& element,
        const Material& material) {
        // Calculate element mass matrix using FEM shape functions
        size_t n = element.size();
        Eigen::MatrixXcd Me(n, n);
        
        // This is a simplified version - actual implementation would use
        // proper FEM shape functions and numerical integration
        for (size_t i = 0; i < n; i++) {
            for (size_t j = 0; j < n; j++) {
                Me(i,j) = Complex(material.mu_r * mu_0_, 0);
            }
        }
        
        return Me;
    }
    
    size_t findNearestNode(const Point3D& point) {
        size_t nearest = 0;
        double min_dist = std::numeric_limits<double>::max();
        
        for (size_t i = 0; i < mesh_.nodes.size(); i++) {
            const auto& node = mesh_.nodes[i];
            double dist = std::pow(node.x - point.x, 2) +
                         std::pow(node.y - point.y, 2) +
                         std::pow(node.z - point.z, 2);
            if (dist < min_dist) {
                min_dist = dist;
                nearest = i;
            }
        }
        
        return nearest;
    }
    
    void extractFields(const Eigen::VectorXcd& solution) {
        fields_.clear();
        
        // Convert solution to E and H fields
        for (size_t i = 0; i < mesh_.nodes.size(); i++) {
            const auto& point = mesh_.nodes[i];
            
            // Extract E-field components
            Vector3D e_field = {
                std::real(solution(i)),
                std::imag(solution(i)),
                0.0  // Assuming 2D solution for simplicity
            };
            
            // Calculate H-field using curl of E
            Vector3D h_field = {
                0.0,  // Simplified H-field calculation
                0.0,
                std::abs(solution(i)) / std::sqrt(mu_0_ / epsilon_0_)
            };
            
            fields_.emplace_back(point, e_field, h_field);
        }
    }
    
    Mesh mesh_;
    double frequency_;
    std::vector<std::pair<Point3D, Vector3D>> ports_;
    std::vector<std::pair<Point3D, Vector3D>> boundary_conditions_;
    std::vector<EMField> fields_;
    
    Eigen::MatrixXcd A_;
    Eigen::VectorXcd b_;
    
    const double epsilon_0_ = 8.854e-12;  // Vacuum permittivity
    const double mu_0_ = 1.257e-6;        // Vacuum permeability
};

} // namespace circuit
