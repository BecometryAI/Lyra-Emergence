# Integration Tests Documentation

This document describes the comprehensive end-to-end integration testing suite for Lyra's cognitive architecture.

## Overview

The integration tests validate that all subsystems work together correctly to produce coherent cognitive behavior. Unlike unit tests that test individual components in isolation, these tests verify the complete cognitive loop:

**Identity → Perception → Attention → Emotion → Memory → Meta-Cognition → Action → Language → Conversation**

## Test Organization

### Directory Structure

```
emergence_core/tests/integration/
├── __init__.py                               # Package initialization
├── conftest.py                               # Shared pytest fixtures
├── TESTING_GUIDE.md                          # Comprehensive testing guide (Phase 2, Task 5)
├── test_end_to_end.py                        # Comprehensive integration tests
├── test_scenarios.py                         # Scenario-based tests
├── test_workspace_integration.py             # Workspace broadcasting tests (Phase 2, Task 4)
├── test_attention_integration.py             # Attention mechanism tests (Phase 2, Task 4)
├── test_cognitive_cycle_integration.py       # Complete cycle tests (Phase 2, Task 4)
├── test_memory_integration.py                # Memory consolidation tests (Phase 2, Task 4)
├── test_meta_cognition_integration.py        # Meta-cognition tests (Phase 2, Task 4)
├── test_action_integration.py                # NEW: Action subsystem tests (Phase 2, Task 5)
├── test_language_interfaces_integration.py   # NEW: Language I/O tests (Phase 2, Task 5)
└── test_edge_cases_integration.py            # NEW: Edge cases and error handling (Phase 2, Task 5)
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

---

## Phase 2: Cognitive Core Integration Tests (NEW)

The following test files were added in Phase 2, Task 4 to provide comprehensive verification of the cognitive architecture's core components.

### test_workspace_integration.py

Tests workspace broadcasting and state management mechanisms.

#### TestWorkspaceBroadcasting
Validates the immutability and completeness of workspace snapshots:
- **test_broadcast_returns_immutable_snapshot**: Verifies WorkspaceSnapshot is frozen (Pydantic immutable model)
- **test_broadcast_contains_all_state**: Ensures snapshots include goals, percepts, emotions, memories
- **test_snapshot_isolation**: Confirms workspace modifications don't affect existing snapshots

#### TestWorkspaceUpdate
Validates workspace update integration:
- **test_update_handles_goal_addition**: Goals are correctly added via update()
- **test_update_handles_percept_addition**: Percepts are correctly added via update()
- **test_update_handles_emotion_update**: Emotional state updates work correctly
- **test_update_increments_cycle_count**: Cycle counter increments on each update

**Status**: ✅ 7/7 tests PASSING

### test_attention_integration.py

Tests attention selection mechanisms and resource management.

#### TestAttentionSelection
Validates attention scoring and selection:
- **test_goal_relevance_scoring**: Percepts relevant to goals receive higher attention scores
- **test_novelty_detection**: Novel percepts receive attention boost over familiar content
- **test_emotional_salience**: Emotionally salient percepts are prioritized
- **test_attention_budget_enforced**: Budget limits prevent cognitive overload

**Status**: ✅ 4/4 tests PASSING

### test_cognitive_cycle_integration.py

Tests complete cognitive cycle execution and timing.

#### TestCompleteCognitiveCycle
Validates the complete 12-step cognitive cycle:
- **test_complete_cycle_executes_without_errors**: Full cycle executes all steps successfully
- **test_cycle_updates_workspace_state**: Cycles update workspace state correctly
- **test_cycle_timing_enforced**: 10 Hz timing enforcement with performance warnings

#### TestInputOutputFlow
Validates input → processing → output flow:
- **test_language_input_creates_goals**: Language input creates appropriate goals in workspace

**Status**: Created (requires sentence-transformers dependency)

### test_memory_integration.py

Tests memory consolidation and retrieval mechanisms.

#### TestMemoryConsolidation
Validates memory storage from workspace:
- **test_workspace_consolidates_to_memory**: Workspace state consolidates to long-term memory

#### TestMemoryRetrieval
Validates memory retrieval to workspace:
- **test_retrieval_goal_brings_memories_to_workspace**: RETRIEVE_MEMORY goals fetch relevant memories

**Status**: Created (requires full dependency stack)

### test_meta_cognition_integration.py

Tests meta-cognition and introspection.

#### TestMetaCognitionObservation
Validates self-monitoring and introspective awareness:
- **test_self_monitor_generates_introspective_percepts**: SelfMonitor generates meta-cognitive percepts

**Status**: Created (requires full dependency stack)

### test_action_integration.py

Tests action subsystem integration with workspace (Phase 2, Task 5).

#### TestActionProposal
Validates action proposal based on goals:
- **test_action_subsystem_proposes_actions_for_goals**: Actions proposed for active goals
- **test_action_selection_based_on_priority**: Priority influences action selection
- **test_multiple_goal_types_generate_different_actions**: Different goals create appropriate actions

#### TestActionDecisionMaking
Validates action decision logic:
- **test_action_subsystem_generates_candidates**: Candidate actions generated from state
- **test_action_history_tracking**: Action history and statistics tracked
- **test_action_subsystem_handles_empty_workspace**: Graceful handling of empty workspace

#### TestActionWorkspaceIntegration
Tests action-workspace integration:
- **test_action_reflects_workspace_state**: Actions reflect emotional state and priorities
- **test_action_subsystem_with_multiple_percepts**: Handles multiple percepts correctly

**Status**: ✅ 8 tests PASSING

### test_language_interfaces_integration.py

Tests language input parsing and output generation (Phase 2, Task 5).

#### TestLanguageInputParsing
Validates text-to-cognitive-structure conversion:
- **test_language_input_creates_goals_from_text**: Text creates appropriate goals
- **test_language_input_creates_percept**: Text creates percepts with correct modality
- **test_language_input_detects_intent**: Intent classification works
- **test_language_input_tracks_context**: Conversation context maintained

#### TestLanguageOutputGeneration
Validates cognitive-structure-to-text conversion:
- **test_language_output_generates_from_workspace**: Workspace state → text generation
- **test_language_output_handles_emotional_state**: Emotional state considered in output

#### TestRoundTripLanguageProcessing
Tests complete language processing cycle:
- **test_round_trip_text_processing**: Input → goals/percepts → output cycle
- **test_parse_result_structure**: Parse results have expected structure

#### TestLanguageInterfaceEdgeCases
Tests edge cases:
- **test_empty_input_handling**: Empty strings handled gracefully
- **test_very_long_input_handling**: Long inputs processed correctly

**Status**: ✅ 11 tests PASSING (some may skip if dependencies unavailable)

### test_edge_cases_integration.py

Tests edge cases and error handling (Phase 2, Task 5).

#### TestWorkspaceCapacityLimits
Validates workspace capacity handling:
- **test_workspace_handles_many_goals**: Multiple goals handled correctly
- **test_workspace_handles_many_percepts**: Multiple percepts managed properly
- **test_workspace_handles_percept_replacement**: Percept replacement works

#### TestAttentionBudgetConstraints
Tests attention budget enforcement:
- **test_attention_with_insufficient_budget**: Budget limits respected
- **test_attention_prioritizes_high_complexity**: Complexity-aware selection
- **test_attention_with_zero_budget**: Zero budget handled gracefully

#### TestConcurrentWorkspaceAccess
Validates concurrent access safety:
- **test_multiple_subsystems_read_snapshot_safely**: Safe concurrent reads
- **test_snapshot_immutability_enforced**: Snapshots truly immutable
- **test_workspace_update_doesnt_affect_old_snapshots**: Update isolation

#### TestMalformedInputHandling
Tests invalid input handling:
- **test_invalid_goal_type_raises_error**: Invalid types rejected
- **test_invalid_goal_priority_raises_error**: Priority bounds enforced
- **test_workspace_handles_empty_goal_list**: Empty lists handled

#### TestEmotionalStateEdgeCases
Tests emotional edge cases:
- **test_extreme_emotional_values**: Extreme values handled
- **test_neutral_emotional_state**: Neutral state works correctly

#### TestCycleCountTracking
Tests cycle counting:
- **test_cycle_count_increments**: Cycle count tracks updates
- **test_cycle_count_in_snapshot**: Snapshots include cycle count

**Status**: ✅ 18 tests PASSING

---

## Running Tests

### Run All Integration Tests

> **📖 For comprehensive testing instructions, see [TESTING_GUIDE.md](./TESTING_GUIDE.md)**

```bash
# Using pytest directly
pytest -m integration -v

# Run only Phase 2 cognitive core tests
pytest -m integration emergence_core/tests/integration/test_workspace_integration.py -v
pytest -m integration emergence_core/tests/integration/test_attention_integration.py -v

# Run Phase 2, Task 5 new tests
pytest -m integration emergence_core/tests/integration/test_action_integration.py -v
pytest -m integration emergence_core/tests/integration/test_language_interfaces_integration.py -v
pytest -m integration emergence_core/tests/integration/test_edge_cases_integration.py -v

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

### cognitive_core (NEW - Phase 2)
Provides a fully initialized `CognitiveCore` instance with mock LLMs, automatically starting before the test and stopping after.

Usage:
```python
async def test_example(cognitive_core):
    await cognitive_core.process_language_input("Test input")
    # core automatically starts before test and stops after
```

### workspace (NEW - Phase 2)
Provides a fresh `GlobalWorkspace` instance for testing workspace operations.

Usage:
```python
def test_example(workspace):
    goal = Goal(type=GoalType.RESPOND_TO_USER, description="Test")
    workspace.add_goal(goal)
    snapshot = workspace.broadcast()
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

**Phase 2 additions verify:**
- ✅ Workspace broadcasts immutable snapshots (7 tests)
- ✅ Workspace update mechanism works correctly (4 tests)
- ✅ Attention selects percepts based on multiple factors (4 tests)
- ✅ Goal relevance, novelty, emotion all influence attention
- ✅ Attention budget enforcement prevents overload
- 🟡 Cognitive cycle executes 12 steps correctly (created, needs dependencies)
- 🟡 Timing enforcement maintains ~10 Hz (created, needs dependencies)
- 🟡 Memory consolidation and retrieval (created, needs dependencies)
- 🟡 Meta-cognition generates introspective percepts (created, needs dependencies)

**Phase 2, Task 5 additions verify:**
- ✅ Action subsystem proposes actions for goals (3 test classes, 8 tests)
- ✅ Action selection considers priority and goal types
- ✅ Action history tracking and statistics collection
- ✅ Language input creates goals and percepts from text (4 test classes, 11 tests)
- ✅ Language output generates text from workspace state
- ✅ Round-trip text processing (input → goals → output)
- ✅ Edge cases: workspace capacity, attention budget, concurrent access (6 test classes, 18 tests)
- ✅ Malformed input handling with proper validation errors
- ✅ Emotional state edge cases and cycle count tracking
- ✅ Comprehensive testing guide for contributors

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
