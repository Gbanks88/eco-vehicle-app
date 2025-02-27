"""Test utilities for UML diagram testing"""

import pytest
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
import random
import string
from datetime import datetime, timedelta

from src.modeling.uml.core import Model, Class, Operation, Parameter
from src.modeling.agile.process_monitor import AgileMetric, AgileMetricType

class TestDataGenerator:
    """Utility class for generating test data"""
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """Generate a random string of specified length"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_random_id() -> str:
        """Generate a random ID"""
        return str(uuid4())
    
    @staticmethod
    def generate_class_hierarchy(depth: int = 3, breadth: int = 2) -> List[Class]:
        """Generate a class hierarchy with specified depth and breadth"""
        classes = []
        
        def create_class(level: int, parent: Optional[Class] = None) -> None:
            if level > depth:
                return
                
            for i in range(breadth):
                class_name = f"Class_L{level}_B{i}"
                new_class = Class(
                    name=class_name,
                    operations=[
                        Operation(
                            name=f"operation_{j}",
                            parameters=[
                                Parameter(
                                    name=f"param_{k}",
                                    param_type=random.choice(["int", "string", "bool"])
                                )
                                for k in range(random.randint(0, 3))
                            ]
                        )
                        for j in range(random.randint(1, 3))
                    ]
                )
                
                if parent:
                    new_class.parent = parent.id
                    
                classes.append(new_class)
                create_class(level + 1, new_class)
        
        create_class(1)
        return classes
    
    @staticmethod
    def generate_sprint_data(num_days: int = 14) -> Dict[str, Any]:
        """Generate sprint data for testing"""
        start_date = datetime.now()
        
        return {
            "sprint_id": f"SPRINT-{TestDataGenerator.generate_random_string(5)}",
            "goals": [
                f"Goal {i}" for i in range(random.randint(3, 5))
            ],
            "burndown_data": [
                (
                    start_date + timedelta(days=i),
                    100 - (i * (100 / num_days))
                )
                for i in range(num_days + 1)
            ],
            "metrics": [
                AgileMetric(
                    metric_type=random.choice(list(AgileMetricType)),
                    value=random.uniform(0.5, 1.0),
                    details={"key": "value"}
                )
                for _ in range(5)
            ]
        }

class DiagramVerifier:
    """Utility class for verifying diagram properties"""
    
    @staticmethod
    def verify_connectivity(nodes: List[Any], edges: List[Tuple[Any, Any]]) -> bool:
        """Verify that the graph is fully connected"""
        if not nodes or not edges:
            return False
            
        # Create adjacency list
        adj_list = {node: [] for node in nodes}
        for source, target in edges:
            adj_list[source].append(target)
            adj_list[target].append(source)
        
        # Perform DFS
        visited = set()
        
        def dfs(node: Any) -> None:
            visited.add(node)
            for neighbor in adj_list[node]:
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(nodes[0])
        return len(visited) == len(nodes)
    
    @staticmethod
    def verify_no_cycles(nodes: List[Any], edges: List[Tuple[Any, Any]]) -> bool:
        """Verify that the graph has no cycles"""
        adj_list = {node: [] for node in nodes}
        for source, target in edges:
            adj_list[source].append(target)
        
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: Any) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in adj_list[node]:
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in nodes:
            if node not in visited:
                if has_cycle(node):
                    return False
        return True
    
    @staticmethod
    def verify_hierarchy(parent_child_pairs: List[Tuple[Any, Any]]) -> bool:
        """Verify that hierarchical relationships are valid"""
        # Create parent-child mapping
        hierarchy = {}
        for parent, child in parent_child_pairs:
            if parent not in hierarchy:
                hierarchy[parent] = set()
            hierarchy[parent].add(child)
        
        # Check for cycles in hierarchy
        def has_cycle(node: Any, visited: set) -> bool:
            if node in visited:
                return True
            
            visited.add(node)
            if node in hierarchy:
                for child in hierarchy[node]:
                    if has_cycle(child, visited.copy()):
                        return True
            return False
        
        for node in hierarchy:
            if has_cycle(node, set()):
                return False
        return True

class PerformanceProfiler:
    """Utility class for profiling diagram operations"""
    
    def __init__(self):
        self.measurements = {}
    
    def measure_operation(self, operation_name: str, func: callable, *args, **kwargs) -> Any:
        """Measure the execution time of an operation"""
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        if operation_name not in self.measurements:
            self.measurements[operation_name] = []
        self.measurements[operation_name].append(duration)
        
        return result
    
    def get_average_time(self, operation_name: str) -> float:
        """Get the average execution time for an operation"""
        if operation_name not in self.measurements:
            return 0.0
        return sum(self.measurements[operation_name]) / len(self.measurements[operation_name])
    
    def get_max_time(self, operation_name: str) -> float:
        """Get the maximum execution time for an operation"""
        if operation_name not in self.measurements:
            return 0.0
        return max(self.measurements[operation_name])
    
    def get_performance_report(self) -> Dict[str, Dict[str, float]]:
        """Generate a performance report for all measured operations"""
        return {
            op_name: {
                "avg_time": self.get_average_time(op_name),
                "max_time": self.get_max_time(op_name),
                "num_samples": len(measurements)
            }
            for op_name, measurements in self.measurements.items()
        }

class TestAssertion:
    """Utility class for custom test assertions"""
    
    @staticmethod
    def assert_valid_diagram(diagram: Any) -> None:
        """Assert that a diagram is valid"""
        assert diagram is not None, "Diagram should not be None"
        assert hasattr(diagram, "generate"), "Diagram should have generate method"
        assert callable(diagram.generate), "generate should be callable"
    
    @staticmethod
    def assert_valid_model(model: Model) -> None:
        """Assert that a model is valid"""
        assert model is not None, "Model should not be None"
        assert model.name, "Model should have a name"
        assert hasattr(model, "packages"), "Model should have packages"
    
    @staticmethod
    def assert_valid_metrics(metrics: List[AgileMetric]) -> None:
        """Assert that agile metrics are valid"""
        for metric in metrics:
            assert isinstance(metric, AgileMetric), "Metric should be AgileMetric instance"
            assert 0 <= metric.value <= 1, "Metric value should be between 0 and 1"
            assert metric.metric_type in AgileMetricType, "Invalid metric type"
