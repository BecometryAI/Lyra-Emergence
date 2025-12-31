# Integration Tests Documentation

This document describes the comprehensive end-to-end integration testing suite for Lyra's cognitive architecture.

## Overview

The integration tests validate that all subsystems work together correctly to produce coherent cognitive behavior. Unlike unit tests that test individual components in isolation, these tests verify the complete cognitive loop:

**Identity → Perception → Attention → Emotion → Memory → Meta-Cognition → Action → Language → Conversation**

## Test Organization

### Directory Structure

```
emergence_core/tests/integration/
├── __init__.py           # Package initialization
├── conftest.py           # Shared pytest fixtures
├── test_end_to_end.py    # Comprehensive integration tests
└── test_scenarios.py     # Scenario-based tests
```

### Scripts

```
scripts/
├── run_integration_tests.py  # Run all integration tests
└── validate_system.py         # Quick system health check
```

## Test Classes

### test_end_to_end.py

#### TestBasicConversationFlow
Tests fundamental conversation capabilities:
- **test_single_turn_conversation**: Validates complete input → processing → response cycle
- **test_multi_turn_conversation**: Validates context retention across multiple turns

#### TestIdentityDrivenBehavior
Validates that Lyra's identity (charter and protocols) influences responses:
- **test_charter_influences_responses**: Charter values reflected in responses
- **test_protocols_guide_behavior**: Protocols guide conversational behavior

#### TestEmotionalDynamics
Tests emotional state updates and influences:
- **test_emotion_updates_with_input**: Emotional state responds to input
- **test_emotion_influences_language**: Emotional state affects language generation

#### TestMemoryIntegration
Validates memory storage and retrieval:
- **test_memory_consolidation**: Conversations consolidated to memory
- **test_memory_retrieval_in_conversation**: Relevant memories retrieved during conversation

#### TestAttentionMechanism
Tests attention subsystem integration:
- **test_attention_selects_salient_percepts**: Attention mechanism selects important information

#### TestMetaCognitionIntegration
Validates meta-cognition and introspection:
- **test_introspection_occurs**: Self-monitoring generates introspective percepts

#### TestAutonomousSpeech
Tests autonomous speech initiation:
- **test_autonomous_speech_triggers**: Autonomous speech can be triggered

#### TestPerformanceBenchmarks
Measures system performance:
- **test_response_time_reasonable**: Response times within acceptable limits (< 15s)
- **test_throughput**: Multiple messages processed efficiently

#### TestSystemMetrics
Validates metrics collection:
- **test_metrics_collection**: System collects conversation and cognitive metrics

### test_scenarios.py

#### TestConversationScenarios
Tests realistic interaction patterns:
- **test_greeting_and_introduction**: Natural greeting flow
- **test_emotional_support_scenario**: Providing emotional support
- **test_introspective_conversation**: Self-awareness discussions

## Running Tests

### Run All Integration Tests

```bash
# Using pytest directly
pytest -m integration -v

# Using the convenience script
python scripts/run_integration_tests.py
```

### Run Specific Test Class

```bash
pytest -m integration emergence_core/tests/integration/test_end_to_end.py::TestBasicConversationFlow -v
```

### Run Specific Test

```bash
pytest -m integration emergence_core/tests/integration/test_end_to_end.py::TestBasicConversationFlow::test_single_turn_conversation -v
```

### Exclude Integration Tests

When running the full test suite, exclude integration tests (which may be slow):

```bash
pytest -m "not integration"
```

## System Validation

For quick system health checks, use the validation script:

```bash
python scripts/validate_system.py
```

This runs 5 essential tests:
1. System initialization
2. Single conversation turn
3. Emotional state
4. Multi-turn coherence
5. Metrics collection

## Test Configuration

Integration tests are marked with `@pytest.mark.integration` and configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests (deselect with '-m \"not integration\"')",
]
```

## Shared Fixtures

The `conftest.py` provides shared fixtures:

### event_loop
Creates a fresh asyncio event loop for each test, ensuring test isolation.

### lyra_api
Provides a fully initialized and started `LyraAPI` instance, automatically cleaning up after the test.

Usage:
```python
async def test_example(lyra_api):
    turn = await lyra_api.chat("Hello!")
    # lyra_api automatically starts before test and stops after
```

## Expected Behavior

### Response Times
- Single turn: < 15 seconds
- Multiple turns: average < 15 seconds

### Memory and Context
- Conversation history tracked across turns
- Context from previous turns influences responses
- Memory consolidation happens asynchronously

### Emotional State
- VAD (Valence, Arousal, Dominance) values present in responses
- Emotional state updates based on input sentiment
- Emotional state influences language generation

### Attention and Salience
- Important information receives higher attention scores
- Attended percepts available in workspace snapshot

## Troubleshooting

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -e .[dev]
```

### Async Warnings
Tests use `pytest-asyncio` with `asyncio_mode = "strict"`. Ensure `pytest-asyncio>=1.2.0` is installed.

### Timeouts
If tests timeout frequently, adjust the response timeout in LyraAPI config:
```python
config = {"conversation": {"response_timeout": 30.0}}
api = LyraAPI(config)
```

## Contributing

When adding new integration tests:

1. Mark with `@pytest.mark.integration`
2. Use `@pytest.mark.asyncio` for async tests
3. Follow existing naming patterns (`test_<what>_<does>_<what>`)
4. Use fixtures from `conftest.py` when possible
5. Include docstrings explaining what's being tested
6. Clean up resources in `finally` blocks

## Success Criteria

Integration tests verify:
- ✅ Complete cognitive loop functions correctly
- ✅ All subsystems integrate properly
- ✅ Identity influences behavior
- ✅ Emotional dynamics work as expected
- ✅ Memory consolidation and retrieval function
- ✅ Attention mechanism operates correctly
- ✅ Meta-cognition provides introspection
- ✅ Performance meets benchmarks
- ✅ Metrics collection works

## Future Enhancements

Potential additions to the integration test suite:

1. **Long-running conversation tests**: Sessions with 50+ turns
2. **Stress tests**: High-throughput scenarios
3. **Error recovery tests**: Handling of various failure modes
4. **Multi-modal tests**: Integration with vision and audio
5. **Memory persistence tests**: State preservation across restarts
6. **Goal-directed behavior tests**: Complex multi-step goal achievement
7. **Autonomous behavior tests**: Extended autonomous operation
8. **Social interaction tests**: Multi-user scenarios

## Related Documentation

- [Cognitive Core Implementation](../../COGNITIVE_CORE_IMPLEMENTATION.md)
- [Test Documentation](../../TEST_DOCUMENTATION.md)
- [Project Structure](../../docs/PROJECT_STRUCTURE.md)
- [Quick Reference](../../docs/QUICK_REFERENCE.md)
