# Testing Guide for SMWCentral Downloader & Patcher

This document provides comprehensive information about the testing framework for SMWCentral Downloader & Patcher v4.0.

## 🎯 Testing Goals

Our testing framework is designed to:
- Achieve **80%+ code coverage** across all major components
- Provide **automated regression testing** for every code change
- Enable **continuous integration** and confident deployments
- Test **real-world workflows** and edge cases
- Ensure **cross-component integration** works correctly

## 📁 Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── test_config.py             # Test configuration and utilities
├── run_tests.py               # Main test runner with coverage
├── test_utils.py              # Tests for utils.py
├── test_config_manager.py     # Tests for config_manager.py
├── test_hack_data_manager.py  # Tests for hack_data_manager.py
├── test_api_pipeline.py       # Tests for api_pipeline.py
├── test_patch_handler.py      # Tests for patch_handler.py
├── test_ui_components.py      # Tests for UI components
└── test_integration.py        # End-to-end integration tests
```

## 🚀 Quick Start

### Running All Tests

```bash
# Method 1: Using the custom test runner (Windows)
run_tests.bat

# Method 2: Using Python directly
python -m tests.run_tests

# Method 3: Using pytest (if installed)
pytest
```

### Running Specific Tests

```bash
# Quick test of core modules
quick_test.bat

# Specific test module
python -m tests.run_tests --module test_utils

# Specific test class
python -m tests.run_tests --module test_utils --class TestUtils

# Specific test method
python -m tests.run_tests --module test_utils --class TestUtils --method test_safe_filename
```

## 📊 Coverage Reporting

### Coverage Targets

- **Overall Target**: 80%+ code coverage
- **Core Modules**: 90%+ coverage
  - `utils.py`
  - `config_manager.py`
  - `hack_data_manager.py`
  - `api_pipeline.py`
- **UI Components**: 70%+ coverage (GUI testing limitations)
- **Integration**: 85%+ workflow coverage

### Viewing Coverage Reports

After running tests with coverage:

```bash
# View HTML coverage report
open coverage_html/index.html  # macOS/Linux
start coverage_html/index.html # Windows

# View terminal coverage summary
python -m tests.run_tests --verbose
```

## 🧪 Test Categories

### 1. Unit Tests

**Purpose**: Test individual functions and methods in isolation

**Modules Covered**:
- `test_utils.py` - Utility functions, file operations, formatting
- `test_config_manager.py` - Configuration management and persistence
- `test_hack_data_manager.py` - Data filtering, analytics, CRUD operations
- `test_api_pipeline.py` - API interactions, download pipeline
- `test_patch_handler.py` - Patch application (BPS/IPS)

**Example**:
```python
def test_safe_filename(self):
    """Test safe_filename function"""
    test_cases = [
        ("Normal Filename", "Normal Filename"),
        ("File<>Name", "FileName"),
        ("File|Name", "FileName")
    ]
    
    for input_name, expected in test_cases:
        with self.subTest(input_name=input_name):
            result = utils.safe_filename(input_name)
            self.assertEqual(result, expected)
```

### 2. UI Component Tests

**Purpose**: Test GUI components and user interactions

**Coverage**:
- Navigation system
- Theme toggling
- Form validation
- Button state management
- Dialog handling

**Approach**: Uses mocking to avoid actual GUI creation during tests

### 3. Integration Tests

**Purpose**: Test end-to-end workflows and component interactions

**Test Scenarios**:
- Complete download workflow (API → Download → Patch → Save)
- Data persistence across application sessions
- Multi-type system workflows
- Filter and analytics workflows
- Error handling and recovery
- Performance with large datasets

### 4. Regression Tests

**Purpose**: Ensure new changes don't break existing functionality

**Strategy**:
- Run full test suite before every commit
- Automated testing in CI/CD pipeline
- Performance benchmarks for critical operations

## 🔧 Test Configuration

### Environment Setup

Tests automatically create isolated test environments:
- Temporary directories for file operations
- Mock configuration files
- Isolated data files
- Mocked external dependencies

### Mock Components

The test framework includes comprehensive mocking:

```python
# HTTP requests for API testing
@patch('api_pipeline.requests.get')
def test_fetch_metadata(self, mock_get):
    mock_get.return_value = create_mock_response(200, {"data": {}})
    # Test implementation

# GUI components
@run_with_mock_gui
def test_ui_component(self):
    # Test without creating actual windows
```

### Test Data

Standardized test data is provided:
- Sample hack data with all required fields
- Multi-type hack examples
- Edge cases (obsolete hacks, missing data)
- Large datasets for performance testing

## 📈 Performance Testing

### Benchmarks

Key performance targets tested:
- **Data Loading**: Large datasets (1000+ hacks) < 5 seconds
- **Filtering**: Complex filters < 2 seconds
- **Analytics**: Statistical calculations < 3 seconds
- **File Operations**: Save/load operations < 1 second

### Memory Testing

Optional memory profiling available:
```bash
# Install memory profiler
pip install memory_profiler

# Run with memory monitoring
python -m tests.run_tests --profile-memory
```

## 🐛 Debugging Tests

### Verbose Output

```bash
# Maximum verbosity
python -m tests.run_tests --verbose --verbose

# See all test output
python -m tests.run_tests --no-capture
```

### Running Individual Tests

```bash
# Debug specific failing test
python -m unittest tests.test_utils.TestUtils.test_safe_filename -v
```

### Common Issues

1. **GUI Tests Failing**: Ensure mocking is properly configured
2. **File Permission Errors**: Tests clean up automatically, but may need manual cleanup
3. **Import Errors**: Ensure PYTHONPATH includes project root
4. **Slow Tests**: Check if creating too many temporary files

## 🔄 Continuous Integration

### Pre-Commit Testing

Before every commit:
```bash
# Run quick test suite
quick_test.bat

# Run full test suite for major changes
run_tests.bat
```

### Automated Testing

The test framework supports CI/CD integration:
- Exit codes indicate pass/fail status
- XML coverage reports for CI systems
- Parallel test execution support

### Quality Gates

Recommended quality gates:
- **80%+ coverage** required for merge
- **All tests passing** required for release
- **Performance tests** passing for major features

## 📝 Writing New Tests

### Test Structure

```python
class TestNewFeature(unittest.TestCase):
    """Test cases for new feature"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestConfig.get_temp_dir()
        # Additional setup
    
    def tearDown(self):
        """Clean up test environment"""
        TestConfig.cleanup_temp_dir(self.test_dir)
    
    def test_feature_functionality(self):
        """Test the main functionality"""
        # Arrange
        # Act
        # Assert
```

### Best Practices

1. **Use descriptive test names**: `test_safe_filename_removes_invalid_characters`
2. **Test edge cases**: Empty inputs, invalid data, boundary conditions
3. **Use subTests for multiple scenarios**: Test similar cases in one method
4. **Mock external dependencies**: Don't rely on network, file system, etc.
5. **Clean up resources**: Use setUp/tearDown properly
6. **Assert meaningfully**: Use specific assertions with clear messages

### Adding Tests for New Features

1. **Create test methods** in appropriate test module
2. **Add integration tests** for workflows
3. **Update coverage targets** if needed
4. **Document test scenarios** in this guide

## 🎯 Coverage Analysis

### Reviewing Coverage Reports

1. **Overall Coverage**: Check summary in terminal output
2. **Module Coverage**: Review per-file coverage in HTML report
3. **Missing Lines**: Identify untested code paths
4. **Coverage Trends**: Track coverage over time

### Improving Coverage

1. **Identify gaps**: Use HTML report to find untested lines
2. **Add unit tests**: For individual functions
3. **Add integration tests**: For complex workflows
4. **Test error paths**: Exception handling, edge cases

### Coverage Exclusions

Some code is excluded from coverage requirements:
- Debug-only code
- Abstract methods
- Platform-specific code
- Error handling that can't be easily triggered

## 🚀 Advanced Testing

### Parameterized Tests

```python
def test_multiple_scenarios(self):
    test_cases = [
        (input1, expected1),
        (input2, expected2),
        (input3, expected3)
    ]
    
    for input_val, expected in test_cases:
        with self.subTest(input_val=input_val):
            result = function_under_test(input_val)
            self.assertEqual(result, expected)
```

### Property-Based Testing

For complex data transformations, consider property-based testing:
```python
# Example: Test that encoding/decoding is reversible
def test_encoding_reversible(self):
    original_data = generate_test_data()
    encoded = encode_data(original_data)
    decoded = decode_data(encoded)
    self.assertEqual(original_data, decoded)
```

### Load Testing

For performance-critical operations:
```python
def test_performance_large_dataset(self):
    large_dataset = create_large_dataset(10000)
    start_time = time.time()
    result = process_dataset(large_dataset)
    end_time = time.time()
    
    self.assertLess(end_time - start_time, 5.0)  # Should complete in 5 seconds
    self.assertEqual(len(result), 10000)
```

## 📚 Resources

### Python Testing Documentation
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [pytest Documentation](https://docs.pytest.org/)
- [coverage.py Documentation](https://coverage.readthedocs.io/)

### Best Practices
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Test-Driven Development](https://testdriven.io/test-driven-development/)

### Tools
- **Coverage.py**: Code coverage measurement
- **pytest**: Alternative test runner with plugins
- **mock**: Python mocking library
- **responses**: HTTP request mocking

---

## 🎉 Success Metrics

Our testing framework ensures:
- ✅ **80%+ code coverage** across all modules
- ✅ **Automated regression testing** for every change
- ✅ **Fast feedback loop** (< 2 minutes for full test suite)
- ✅ **Reliable CI/CD pipeline** with quality gates
- ✅ **Confident deployments** with comprehensive test coverage

**Happy Testing!** 🧪✨
