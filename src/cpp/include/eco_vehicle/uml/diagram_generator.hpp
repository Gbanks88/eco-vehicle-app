#pragma once

#include <memory>
#include <vector>
#include <string>
#include <optional>
#include <filesystem>
#include <boost/graph/adjacency_list.hpp>
#include "eco_vehicle/core/logging.hpp"
#include "eco_vehicle/core/config.hpp"

namespace eco_vehicle {
namespace uml {

/**
 * @brief Class definition metadata
 */
struct ClassDefinition {
    std::string name;
    std::vector<std::pair<std::string, std::string>> attributes;  // name, type
    std::vector<std::pair<std::string, std::string>> methods;     // name, signature
    std::vector<std::string> superclasses;
    std::vector<std::string> dependencies;
};

/**
 * @brief Message in sequence diagram
 */
struct SequenceMessage {
    std::string source;
    std::string target;
    std::string message;
    std::optional<std::string> response;
    bool is_async;
};

/**
 * @brief State in state diagram
 */
struct State {
    std::string name;
    std::vector<std::string> entry_actions;
    std::vector<std::string> exit_actions;
    std::vector<std::string> activities;
};

/**
 * @brief Transition in state diagram
 */
struct Transition {
    std::string from_state;
    std::string to_state;
    std::string trigger;
    std::string guard;
    std::string action;
};

/**
 * @brief High-performance UML diagram generator
 */
class DiagramGenerator {
public:
    /**
     * @brief Initialize diagram generator
     * @param config Generator configuration
     */
    explicit DiagramGenerator(const Config& config);
    
    /**
     * @brief Generate class diagram
     * @param classes List of class definitions
     * @param filename Output filename
     * @return Path to generated diagram
     */
    std::optional<std::filesystem::path> generate_class_diagram(
        const std::vector<ClassDefinition>& classes,
        const std::string& filename);
    
    /**
     * @brief Generate sequence diagram
     * @param messages List of sequence messages
     * @param filename Output filename
     * @return Path to generated diagram
     */
    std::optional<std::filesystem::path> generate_sequence_diagram(
        const std::vector<SequenceMessage>& messages,
        const std::string& filename);
    
    /**
     * @brief Generate state diagram
     * @param states List of states
     * @param transitions List of transitions
     * @param filename Output filename
     * @return Path to generated diagram
     */
    std::optional<std::filesystem::path> generate_state_diagram(
        const std::vector<State>& states,
        const std::vector<Transition>& transitions,
        const std::string& filename);
    
    /**
     * @brief Get current performance metrics
     * @return Generator performance metrics
     */
    PerformanceMetrics get_performance_metrics() const;

private:
    // Configuration
    Config config_;
    std::filesystem::path output_dir_;
    PerformanceTracker performance_tracker_;
    
    // Graph representation
    using Graph = boost::adjacency_list<
        boost::vecS,
        boost::vecS,
        boost::bidirectionalS,
        boost::property<boost::vertex_name_t, std::string>,
        boost::property<boost::edge_name_t, std::string>
    >;
    
    /**
     * @brief Create graph from class definitions
     */
    Graph create_class_graph(const std::vector<ClassDefinition>& classes);
    
    /**
     * @brief Create graph from sequence messages
     */
    Graph create_sequence_graph(const std::vector<SequenceMessage>& messages);
    
    /**
     * @brief Create graph from states and transitions
     */
    Graph create_state_graph(
        const std::vector<State>& states,
        const std::vector<Transition>& transitions);
    
    /**
     * @brief Layout graph using force-directed algorithm
     */
    void layout_graph(Graph& graph);
    
    /**
     * @brief Render graph to file
     */
    std::optional<std::filesystem::path> render_graph(
        const Graph& graph,
        const std::string& filename);
    
    /**
     * @brief Add class to diagram
     */
    void add_class_to_diagram(
        Graph& graph,
        const ClassDefinition& class_def);
    
    /**
     * @brief Add relationships between classes
     */
    void add_relationships(
        Graph& graph,
        const std::vector<ClassDefinition>& classes);
    
    /**
     * @brief Add lifeline to sequence diagram
     */
    void add_lifeline(
        Graph& graph,
        const std::string& participant,
        size_t position);
    
    /**
     * @brief Add message to sequence diagram
     */
    void add_sequence_message(
        Graph& graph,
        const SequenceMessage& msg,
        const std::unordered_map<std::string, size_t>& positions,
        size_t index);
    
    /**
     * @brief Add state to state diagram
     */
    void add_state(Graph& graph, const State& state);
    
    /**
     * @brief Add transition to state diagram
     */
    void add_transition(Graph& graph, const Transition& transition);
};

} // namespace uml
} // namespace eco_vehicle
