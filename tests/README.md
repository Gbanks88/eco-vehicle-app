# UML Diagram Generator Test Suite

This test suite provides comprehensive testing for the UML diagram generation system, including unit tests, integration tests, performance tests, and agile process monitoring.

## Test Structure

```
tests/
├── conftest.py              # Global pytest configuration and fixtures
├── modeling/
│   ├── uml/
│   │   └── test_diagrams/  # Unit tests for diagram generators
│   │       ├── test_activity.py
│   │       ├── test_component.py
│   │       ├── test_deployment.py
│   │       ├── test_logical.py
│   │       ├── test_sequence.py
│   │       └── test_state.py
│   └── agile/
│       └── test_process_monitor.py  # Agile process monitoring tests
├── performance/
│   └── test_large_diagrams.py      # Performance tests
├── integration/
│   └── test_diagram_integration.py  # Integration tests
└── utils/
    └── test_utils.py               # Test utilities and helpers
```

## Test Categories

### 1. Unit Tests

Unit tests for each diagram generator cover:
- Basic diagram creation
- Complex scenarios
- Edge cases
- Validation rules
- Error handling

### 2. Integration Tests

Integration tests verify:
- Cross-diagram relationships
- Diagram synchronization
- End-to-end workflows
- Component interactions

### 3. Performance Tests

Performance tests evaluate:
- Large diagram generation
- Memory usage
- Response times
- Scalability limits

### 4. Agile Process Monitor Tests

Tests for agile process monitoring include:
- Sprint management
- Metric tracking
- Health calculations
- Warning generation
- Report generation

## Test Utilities

### 1. Fixtures (`conftest.py`)

Common fixtures provide:
- Sample models
- Diagram elements
- Mock file systems
- Helper classes

### 2. Test Utilities (`test_utils.py`)

Utility classes include:
- `TestDataGenerator`: Generate test data
- `DiagramVerifier`: Verify diagram properties
- `PerformanceProfiler`: Profile operations
- `TestAssertion`: Custom assertions

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/modeling/uml/test_diagrams/
pytest tests/performance/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

### Test Configuration

Configure test behavior in `pytest.ini`:
```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    performance: marks tests as performance tests
```

## Performance Benchmarks

Performance tests verify:

1. Activity Diagrams:
   - 100 nodes: < 1s
   - 500 nodes: < 5s
   - 1000 nodes: < 10s

2. Component Diagrams:
   - 50 components: < 0.5s
   - 200 components: < 2s
   - 500 components: < 5s

3. State Diagrams:
   - 100 states: < 1s
   - 300 states: < 3s
   - 500 states: < 5s

4. Sequence Diagrams:
   - 200 messages: < 1s
   - 600 messages: < 3s
   - 1200 messages: < 6s

## Adding New Tests

### 1. Unit Tests

1. Create test file in appropriate directory
2. Import required modules and fixtures
3. Write test functions using pytest
4. Add appropriate markers

Example:
```python
@pytest.mark.slow
def test_large_diagram():
    """Test large diagram generation"""
    # Test implementation
```

### 2. Integration Tests

1. Identify cross-component scenarios
2. Create test file in integration directory
3. Use fixtures from conftest.py
4. Verify component interactions

### 3. Performance Tests

1. Define performance criteria
2. Create test scenarios
3. Use PerformanceProfiler
4. Assert performance requirements

## Best Practices

1. Test Organization:
   - Group related tests
   - Use descriptive names
   - Add clear docstrings

2. Test Data:
   - Use fixtures for common data
   - Generate random data when appropriate
   - Clean up test data

3. Assertions:
   - Use custom assertions for clarity
   - Include meaningful error messages
   - Test both positive and negative cases

4. Performance:
   - Mark slow tests appropriately
   - Use performance profiling
   - Set realistic benchmarks

## Contributing

When adding new tests:

1. Follow existing test structure
2. Add appropriate documentation
3. Include performance considerations
4. Update this README if needed

## Troubleshooting

Common issues and solutions:

1. Slow Tests:
   - Use appropriate markers
   - Optimize test data generation
   - Consider parallel execution

2. Flaky Tests:
   - Add proper cleanup
   - Use stable test data
   - Add proper assertions

3. Memory Issues:
   - Clean up large objects
   - Use appropriate fixtures
   - Monitor memory usage
