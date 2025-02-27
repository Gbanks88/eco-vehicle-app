"""Performance tests for large diagram generation"""

import pytest
import time
from uuid import uuid4
from typing import List, Tuple
import random

from src.modeling.uml.core import Model
from src.modeling.uml.diagrams.activity import ActivityDiagramGenerator, ActivityNode, ActivityEdge, ActivityNodeType
from src.modeling.uml.diagrams.component import ComponentDiagramGenerator, Component, Interface, ComponentRelation
from src.modeling.uml.diagrams.deployment import DeploymentDiagramGenerator, DeploymentNode, NodeType
from src.modeling.uml.diagrams.logical import LogicalDiagramGenerator, LogicalElement, ElementType
from src.modeling.uml.diagrams.sequence import SequenceDiagramGenerator
from src.modeling.uml.diagrams.state import StateDiagramGenerator, State, StateType, Transition

def measure_execution_time(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    return wrapper

@pytest.fixture
def large_model():
    """Create a test model"""
    return Model(name="LargeTestModel")

class TestLargeDiagrams:
    """Performance tests for large diagram generation"""
    
    @pytest.mark.slow
    def test_large_activity_diagram(self, large_model):
        """Test performance of large activity diagram generation"""
        generator = ActivityDiagramGenerator(large_model)
        
        # Create large number of nodes and edges
        @measure_execution_time
        def create_large_activity_diagram(num_nodes: int) -> Tuple[List[str], List[Tuple[str, str]]]:
            node_ids = []
            edges = []
            
            # Create nodes
            for i in range(num_nodes):
                node = ActivityNode(
                    id=str(uuid4()),
                    name=f"Activity{i}",
                    node_type=random.choice(list(ActivityNodeType))
                )
                generator.add_node(node)
                node_ids.append(node.id)
            
            # Create edges (ensuring connected graph)
            for i in range(len(node_ids)-1):
                edge = ActivityEdge(
                    source=node_ids[i],
                    target=node_ids[i+1]
                )
                generator.add_edge(edge)
                edges.append((node_ids[i], node_ids[i+1]))
            
            # Add some random edges for complexity
            num_random_edges = num_nodes // 2
            for _ in range(num_random_edges):
                source = random.choice(node_ids)
                target = random.choice(node_ids)
                if source != target:
                    edge = ActivityEdge(source=source, target=target)
                    generator.add_edge(edge)
                    edges.append((source, target))
            
            return node_ids, edges
        
        # Test with different sizes
        sizes = [100, 500, 1000]
        results = {}
        
        for size in sizes:
            (nodes, edges), creation_time = create_large_activity_diagram(size)
            
            @measure_execution_time
            def generate_diagram():
                return generator.generate()
            
            _, generation_time = generate_diagram()
            
            results[size] = {
                "creation_time": creation_time,
                "generation_time": generation_time,
                "total_time": creation_time + generation_time,
                "nodes": len(nodes),
                "edges": len(edges)
            }
        
        # Assert performance criteria
        for size, metrics in results.items():
            assert metrics["total_time"] < size * 0.01  # 10ms per element maximum

    @pytest.mark.slow
    def test_large_component_diagram(self, large_model):
        """Test performance of large component diagram generation"""
        generator = ComponentDiagramGenerator(large_model)
        
        @measure_execution_time
        def create_large_component_diagram(num_components: int):
            components = []
            
            # Create components with interfaces
            for i in range(num_components):
                component = Component(
                    id=str(uuid4()),
                    name=f"Component{i}",
                    stereotype="service"
                )
                
                # Add some interfaces
                for j in range(random.randint(1, 3)):
                    interface = Interface(
                        id=str(uuid4()),
                        name=f"Interface{i}_{j}",
                        provided=random.choice([True, False])
                    )
                    component.add_interface(interface)
                
                generator.add_component(component)
                components.append(component)
            
            # Add relations between components
            num_relations = num_components * 2  # Average 2 relations per component
            for _ in range(num_relations):
                source = random.choice(components)
                target = random.choice(components)
                if source != target:
                    relation = ComponentRelation(
                        source=source.id,
                        target=target.id,
                        type="uses"
                    )
                    generator.add_relation(relation)
            
            return components
        
        sizes = [50, 200, 500]
        results = {}
        
        for size in sizes:
            components, creation_time = create_large_component_diagram(size)
            _, generation_time = measure_execution_time(generator.generate)()
            
            results[size] = {
                "creation_time": creation_time,
                "generation_time": generation_time,
                "total_time": creation_time + generation_time,
                "components": len(components)
            }
        
        # Assert performance criteria
        for size, metrics in results.items():
            assert metrics["total_time"] < size * 0.02  # 20ms per component maximum

    @pytest.mark.slow
    def test_large_state_diagram(self, large_model):
        """Test performance of large state diagram generation"""
        generator = StateDiagramGenerator(large_model)
        
        @measure_execution_time
        def create_large_state_machine(num_states: int):
            states = []
            
            # Create states with different types and actions
            for i in range(num_states):
                state = State(
                    id=str(uuid4()),
                    name=f"State{i}",
                    state_type=StateType.NORMAL if i > 0 else StateType.INITIAL,
                    entry_actions=[f"entry{i}()"] if random.random() > 0.5 else [],
                    exit_actions=[f"exit{i}()"] if random.random() > 0.5 else []
                )
                generator.add_state(state)
                states.append(state)
            
            # Add transitions (ensuring connected graph)
            for i in range(len(states)-1):
                transition = Transition(
                    source=states[i].id,
                    target=states[i+1].id,
                    trigger=f"event{i}",
                    guard=f"[condition{i}]" if random.random() > 0.7 else None
                )
                generator.add_transition(transition)
            
            # Add some random transitions
            num_random_transitions = num_states
            for _ in range(num_random_transitions):
                source = random.choice(states)
                target = random.choice(states)
                if source != target:
                    transition = Transition(
                        source=source.id,
                        target=target.id,
                        trigger=f"randomEvent{_}"
                    )
                    generator.add_transition(transition)
            
            return states
        
        sizes = [100, 300, 500]
        results = {}
        
        for size in sizes:
            states, creation_time = create_large_state_machine(size)
            _, generation_time = measure_execution_time(generator.generate)()
            
            results[size] = {
                "creation_time": creation_time,
                "generation_time": generation_time,
                "total_time": creation_time + generation_time,
                "states": len(states)
            }
        
        # Assert performance criteria
        for size, metrics in results.items():
            assert metrics["total_time"] < size * 0.015  # 15ms per state maximum

    @pytest.mark.slow
    def test_large_sequence_diagram(self, large_model):
        """Test performance of large sequence diagram generation"""
        generator = SequenceDiagramGenerator(large_model)
        
        @measure_execution_time
        def create_large_sequence_diagram(num_lifelines: int, messages_per_lifeline: int):
            # Create lifelines
            lifelines = []
            for i in range(num_lifelines):
                name = f"Lifeline{i}"
                generator.add_lifeline(name, f"Type{i}")
                lifelines.append(name)
            
            # Create messages between lifelines
            total_messages = num_lifelines * messages_per_lifeline
            for i in range(total_messages):
                source = random.choice(lifelines)
                target = random.choice(lifelines)
                if source != target:
                    generator.add_message(
                        source=source,
                        target=target,
                        message=f"message{i}()",
                        return_value="result" if random.random() > 0.7 else None
                    )
            
            return lifelines
        
        configurations = [
            (10, 20),   # 10 lifelines, 20 messages each
            (20, 30),   # 20 lifelines, 30 messages each
            (30, 40)    # 30 lifelines, 40 messages each
        ]
        
        results = {}
        
        for num_lifelines, messages_per_lifeline in configurations:
            lifelines, creation_time = create_large_sequence_diagram(num_lifelines, messages_per_lifeline)
            _, generation_time = measure_execution_time(generator.generate)()
            
            total_messages = num_lifelines * messages_per_lifeline
            results[total_messages] = {
                "creation_time": creation_time,
                "generation_time": generation_time,
                "total_time": creation_time + generation_time,
                "lifelines": len(lifelines),
                "messages": total_messages
            }
        
        # Assert performance criteria
        for total_messages, metrics in results.items():
            assert metrics["total_time"] < total_messages * 0.005  # 5ms per message maximum
