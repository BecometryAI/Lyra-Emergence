# Integration Testing Guide

## Running Integration Tests

### Run All Integration Tests

```bash
pytest emergence_core/tests/integration/ -v -m integration
```

### Run Specific Test File

```bash
pytest emergence_core/tests/integration/test_workspace_integration.py -v
pytest emergence_core/tests/integration/test_action_integration.py -v
pytest emergence_core/tests/integration/test_language_interfaces_integration.py -v
pytest emergence_core/tests/integration/test_edge_cases_integration.py -v
```

### Run Specific Test Class

```bash
pytest emergence_core/tests/integration/test_workspace_integration.py::TestWorkspaceBroadcasting -v
pytest emergence_core/tests/integration/test_action_integration.py::TestActionProposal -v
```

### Run Specific Test

```bash
pytest emergence_core/tests/integration/test_workspace_integration.py::TestWorkspaceBroadcasting::test_broadcast_returns_immutable_snapshot -v
```

### Run with Coverage

```bash
pytest emergence_core/tests/integration/ --cov=emergence_core/lyra/cognitive_core --cov-report=html
```

### Exclude Integration Tests (for fast unit testing)

```bash
pytest -m "not integration"
```

## Test Categories

| Category | Files | Purpose |
|----------|-------|---------|
| **Workspace** | `test_workspace_integration.py` | Workspace state management and broadcasting |
| **Attention** | `test_attention_integration.py` | Attention selection mechanisms |
| **Cognitive Cycle** | `test_cognitive_cycle_integration.py` | Complete cognitive loop execution |
| **Memory** | `test_memory_integration.py` | Memory consolidation and retrieval |
| **Meta-Cognition** | `test_meta_cognition_integration.py` | Self-monitoring and introspection |
| **Actions** | `test_action_integration.py` | Action proposal and execution |
| **Language** | `test_language_interfaces_integration.py` | Input parsing and output generation |
| **Edge Cases** | `test_edge_cases_integration.py` | Boundary conditions and error handling |
| **End-to-End** | `test_end_to_end.py` | Complete conversation flows |
| **Scenarios** | `test_scenarios.py` | Realistic interaction patterns |

## Expected Test Duration

- **Workspace tests**: ~2 seconds
- **Attention tests**: ~3 seconds  
- **Cognitive cycle tests**: ~5 seconds (includes async operations)
- **Memory tests**: ~4 seconds
- **Action tests**: ~3 seconds
- **Language tests**: ~6 seconds (mock models)
- **Edge case tests**: ~2 seconds
- **End-to-end tests**: ~10-15 seconds per test
- **Scenario tests**: ~20-30 seconds per test

**Total suite runtime**: ~30-60 seconds with mock models

## Interpreting Test Results

### All Tests Pass ✅

```
==================== 30 passed in 35.47s ====================
```

System is functioning correctly. All integration points validated.

### Some Tests Fail ❌

```
==================== 25 passed, 5 failed in 32.12s ====================
```

Check failure details:
- **AssertionError**: Expected behavior not met
- **AttributeError**: Missing method/property
- **TimeoutError**: Operation took too long
- **ValidationError**: Invalid data structure
- **ImportError**: Missing dependency

### Test Skipped ⚠️

```
==================== 25 passed, 5 skipped in 28.34s ====================
```

Tests may be skipped due to:
- Missing optional dependencies
- LLM/model not available
- Platform-specific features

Skipped tests are acceptable for local development but should pass in CI with full dependencies.

### Test Hangs or Timeout

If tests hang:
1. Check for deadlocks in async code
2. Verify cognitive core is stopping properly
3. Check for infinite loops in subsystems
4. Increase timeout values in test configuration

## Debugging Failed Tests

### Enable Debug Logging

```bash
pytest emergence_core/tests/integration/test_workspace_integration.py -v -s --log-cli-level=DEBUG
```

### Run Single Test with PDB

```bash
pytest emergence_core/tests/integration/test_workspace_integration.py::TestWorkspaceBroadcasting::test_broadcast_returns_immutable_snapshot -v --pdb
```

### Check Test Isolation

If tests pass individually but fail in suite:
```bash
# Run tests in random order to detect dependencies
pytest --random-order emergence_core/tests/integration/
```

### Verbose Output

```bash
pytest -vv emergence_core/tests/integration/
```

## Test Configuration

### pytest.ini Settings

Integration tests are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "strict"
testpaths = ["emergence_core/tests"]
python_files = ["test_*.py"]
markers = [
    "integration: marks tests as integration tests",
]
```

### Markers

- `@pytest.mark.integration`: Integration test (slower, tests multiple components)
- `@pytest.mark.asyncio`: Async test requiring event loop

## Continuous Integration

Integration tests run automatically on:
- Pull requests
- Merges to main
- Scheduled nightly builds

Check GitHub Actions for CI status.

## Contributing New Tests

When adding integration tests:

1. **Mark with `@pytest.mark.integration`**
   ```python
   @pytest.mark.integration
   def test_my_integration():
       ...
   ```

2. **Use `@pytest.mark.asyncio` for async tests**
   ```python
   @pytest.mark.asyncio
   async def test_my_async_integration():
       ...
   ```

3. **Follow naming convention**: `test_<what>_<does>_<what>`
   - Good: `test_workspace_broadcasts_immutable_snapshot`
   - Bad: `test_1`, `test_workspace`

4. **Use fixtures from `conftest.py`**
   ```python
   def test_with_workspace(workspace):
       # workspace fixture automatically provided
       ...
   ```

5. **Clean up resources in `finally` blocks**
   ```python
   async def test_with_cleanup():
       resource = await create_resource()
       try:
           # test code
           ...
       finally:
           await resource.cleanup()
   ```

6. **Add docstrings explaining what's being tested**
   ```python
   def test_example():
       """Test that X does Y when Z happens."""
       ...
   ```

7. **Update this guide** with new test categories

## Test Coverage Goals

Target coverage for cognitive core components:
- **Workspace**: 95%+ (critical component)
- **Attention**: 90%+
- **Cognitive Core**: 85%+
- **Action Subsystem**: 85%+
- **Language Interfaces**: 80%+
- **Subsystems**: 80%+

Check coverage:
```bash
pytest --cov=emergence_core/lyra/cognitive_core --cov-report=term-missing
```

Generate HTML coverage report:
```bash
pytest --cov=emergence_core/lyra/cognitive_core --cov-report=html
# Open htmlcov/index.html in browser
```

## Common Issues and Solutions

### Issue: Tests fail with "ModuleNotFoundError"

**Solution**: Install dependencies
```bash
pip install -e .
pip install -e ".[dev]"
```

### Issue: Async warnings or errors

**Solution**: Ensure pytest-asyncio is installed
```bash
pip install pytest-asyncio>=1.2.0
```

### Issue: Tests timeout

**Solution**: Increase timeout in test or LLM config
```python
config = {"timeout": 30.0}  # Increase from default
```

### Issue: LLM/model not available

**Solution**: Tests should skip gracefully
```python
try:
    result = await llm_operation()
except Exception as e:
    pytest.skip(f"Skipping due to: {e}")
```

### Issue: Pydantic validation errors

**Solution**: Check data model constraints
- Goal priority: 0.0-1.0
- Percept complexity: >= 0
- Emotion values: -1.0 to 1.0

## Best Practices

### Do ✅

- Test one integration point per test
- Use descriptive test names
- Test happy path and edge cases
- Use fixtures for common setup
- Clean up resources after tests
- Document what's being tested
- Keep tests fast and focused
- Mock external dependencies
- Test error handling

### Don't ❌

- Test implementation details
- Create test interdependencies
- Leave resources uncleaned
- Test private methods directly
- Write tests that depend on timing
- Hardcode paths or credentials
- Ignore skipped tests
- Test multiple things in one test

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [Cognitive Core Implementation](../../COGNITIVE_CORE_IMPLEMENTATION.md)
- [Test Documentation](../../TEST_DOCUMENTATION.md)
- [Integration Tests README](./README.md)

## Quick Reference

### Run subset of tests
```bash
# By marker
pytest -m integration

# By keyword
pytest -k "workspace"

# By file pattern
pytest emergence_core/tests/integration/test_*_integration.py
```

### Common pytest options
```bash
-v          # Verbose
-vv         # Extra verbose
-s          # Show print statements
-x          # Stop on first failure
--lf        # Run last failed
--ff        # Run failed first
--pdb       # Drop into debugger on failure
--maxfail=3 # Stop after 3 failures
```

### Check what will run
```bash
pytest --collect-only emergence_core/tests/integration/
```

### Run in parallel (if pytest-xdist installed)
```bash
pytest -n auto emergence_core/tests/integration/
```
