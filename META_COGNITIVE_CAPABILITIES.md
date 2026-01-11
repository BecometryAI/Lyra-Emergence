# Meta-Cognitive Capabilities Implementation

This document describes the new meta-cognitive capabilities added to the Lyra Emergence cognitive core.

## Overview

Three interconnected meta-cognitive systems have been implemented:

1. **Meta-Cognitive Monitoring** - Observes and tracks cognitive processing patterns
2. **Action-Outcome Learning** - Tracks what actions actually achieve vs intentions  
3. **Attention Allocation History** - Tracks attention patterns and their outcomes

These are unified through the `MetaCognitiveSystem` class which provides self-assessment and introspection capabilities.

## Components

### 1. Processing Monitor (`processing_monitor.py`)

Tracks cognitive processing episodes and identifies patterns.

```python
from lyra.cognitive_core.meta_cognition import MetaCognitiveMonitor

monitor = MetaCognitiveMonitor()

# Observe a cognitive process
with monitor.observe("reasoning") as ctx:
    ctx.set_complexity(0.7)  # Input complexity (0-1)
    ctx.set_quality(0.8)     # Output quality (0-1)
    # ... perform reasoning ...

# Get statistics
stats = monitor.get_process_statistics("reasoning")
print(f"Success rate: {stats.success_rate}")
print(f"Avg duration: {stats.avg_duration_ms}ms")

# Get identified patterns
patterns = monitor.get_identified_patterns()
for pattern in patterns:
    print(f"{pattern.pattern_type}: {pattern.description}")
    if pattern.actionable:
        print(f"  → {pattern.suggested_adaptation}")
```

**Key Classes:**
- `MetaCognitiveMonitor` - Main monitoring interface
- `ProcessingObservation` - Records a processing episode
- `ProcessingContext` - Context manager for observation
- `CognitivePattern` - Identified processing pattern
- `PatternDetector` - Detects patterns in observations

### 2. Action-Outcome Learner (`action_learning.py`)

Learns what actions actually accomplish by tracking outcomes.

```python
from lyra.cognitive_core.meta_cognition import ActionOutcomeLearner

learner = ActionOutcomeLearner()

# Record action outcome
learner.record_outcome(
    action_id="action_123",
    action_type="speak",
    intended="provide helpful response",
    actual="provided detailed helpful response with examples",
    context={"user_sentiment": "positive"}
)

# Get reliability metrics
reliability = learner.get_action_reliability("speak")
print(f"Success rate: {reliability.success_rate}")
print(f"Common side effects: {reliability.common_side_effects}")

# Predict outcome
prediction = learner.predict_outcome("speak", context={"user_sentiment": "neutral"})
print(f"Predicted success: {prediction.probability_success}")
```

**Key Classes:**
- `ActionOutcomeLearner` - Main learning interface
- `ActionOutcome` - Records what an action achieved
- `ActionReliability` - Reliability metrics for an action type
- `ActionModel` - Learned model of action behavior
- `OutcomePrediction` - Prediction of action outcome

### 3. Attention History (`attention_history.py`)

Tracks attention allocation patterns and learns effective strategies.

```python
from lyra.cognitive_core.meta_cognition import AttentionHistory

history = AttentionHistory()

# Record allocation
allocation_id = history.record_allocation(
    allocation={"goal1": 0.6, "goal2": 0.4},
    trigger="new_percept",
    workspace_state=current_state
)

# Record outcome
history.record_outcome(
    allocation_id=allocation_id,
    goal_progress={"goal1": 0.3, "goal2": 0.2},
    discoveries=["insight_x"],
    missed=[]
)

# Get learned patterns
patterns = history.get_attention_patterns()
for pattern in patterns:
    print(f"{pattern.pattern}: efficiency={pattern.avg_efficiency}")

# Get recommendation
recommended = history.get_recommended_allocation(
    context=current_state,
    goals=current_goals
)
```

**Key Classes:**
- `AttentionHistory` - Main history tracking interface
- `AttentionAllocation` - Record of attention allocation
- `AttentionOutcome` - Outcome of an allocation
- `AttentionPattern` - Learned attention pattern
- `AttentionPatternLearner` - Learns effective patterns

### 4. Unified Meta-Cognitive System (`system.py`)

Provides integrated access to all meta-cognitive capabilities.

```python
from lyra.cognitive_core.meta_cognition import MetaCognitiveSystem

system = MetaCognitiveSystem()

# All subsystems are accessible
system.monitor.observe("reasoning")
system.action_learner.record_outcome(...)
system.attention_history.record_allocation(...)

# Get comprehensive self-assessment
assessment = system.get_self_assessment()
print(f"Strengths: {assessment.identified_strengths}")
print(f"Weaknesses: {assessment.identified_weaknesses}")
print(f"Adaptations: {assessment.suggested_adaptations}")

# Introspect about cognitive patterns
response = system.introspect("What do I tend to fail at?")
response = system.introspect("How effective is my attention?")
response = system.introspect("What are my strengths?")
```

**Key Classes:**
- `MetaCognitiveSystem` - Unified interface to all subsystems
- `SelfAssessment` - Comprehensive self-assessment data

## Integration with Existing System

The new meta-cognitive capabilities are designed to work alongside the existing `SelfMonitor` class. They can be:

1. **Used independently** - Each subsystem can be instantiated and used separately
2. **Used through the unified system** - `MetaCognitiveSystem` provides integrated access
3. **Integrated into SelfMonitor** - The existing `SelfMonitor` can incorporate these capabilities

### Example Integration into Cognitive Loop

```python
# In cognitive loop initialization
from lyra.cognitive_core.meta_cognition import MetaCognitiveSystem

meta_system = MetaCognitiveSystem(config=config.get("meta_cognitive", {}))

# During processing
with meta_system.monitor.observe("goal_selection") as ctx:
    ctx.set_complexity(calculate_complexity(workspace_state))
    selected_goal = select_goal(workspace_state)
    ctx.set_quality(assess_quality(selected_goal))

# After action execution
meta_system.action_learner.record_outcome(
    action_id=action.id,
    action_type=str(action.type),
    intended=action.reason,
    actual=actual_outcome,
    context=get_context(workspace_state)
)

# After attention allocation
allocation_id = meta_system.attention_history.record_allocation(
    allocation=attention_allocation,
    trigger=attention_trigger,
    workspace_state=workspace_state
)

# Later, after observing outcomes
meta_system.attention_history.record_outcome(
    allocation_id=allocation_id,
    goal_progress=measured_progress,
    discoveries=identified_insights,
    missed=identified_misses
)

# Periodic self-assessment
if cycle % 100 == 0:
    assessment = meta_system.get_self_assessment()
    logger.info(f"Meta-cognitive assessment: {len(assessment.identified_strengths)} strengths, "
                f"{len(assessment.identified_weaknesses)} weaknesses")
```

## Pattern Detection

The system automatically detects several types of patterns:

### Success Conditions
- Identifies conditions that lead to successful processing
- E.g., "reasoning succeeds more often on simpler inputs"

### Failure Modes
- Identifies conditions associated with failures
- E.g., "memory_retrieval tends to fail on high-complexity inputs"
- Provides actionable adaptations

### Efficiency Factors
- Identifies factors affecting processing efficiency
- E.g., "introspection is relatively slow (avg 850ms)"
- Suggests optimization strategies

## Configuration

Each subsystem accepts configuration:

```python
config = {
    "monitor": {
        "max_observations": 1000  # Max observations to keep in memory
    },
    "action_learner": {
        "max_outcomes": 1000,           # Max outcomes to keep
        "min_samples_for_model": 5      # Min samples to build prediction model
    },
    "attention_history": {
        "max_allocations": 1000         # Max allocations to keep
    }
}

system = MetaCognitiveSystem(config=config)
```

## Testing

Tests are provided in `tests/test_meta_cognitive_capabilities.py`:

```bash
pytest emergence_core/tests/test_meta_cognitive_capabilities.py -v
```

The tests verify:
- Pattern detection from processing observations
- Action reliability computation and prediction
- Attention pattern learning and recommendations
- Unified system integration and introspection

## Future Enhancements

Potential future improvements:

1. **Persistence** - Save/load learned patterns and models
2. **Advanced Pattern Detection** - More sophisticated ML-based pattern recognition
3. **Cross-Subsystem Learning** - Learn correlations between processing, actions, and attention
4. **Adaptive Strategies** - Automatically adjust strategies based on learned patterns
5. **Visualization** - Dashboard for monitoring meta-cognitive insights

## References

- Global Workspace Theory (Baars, 1988)
- Meta-cognitive monitoring and control (Nelson & Narens, 1990)
- Self-modeling systems (Schmidhuber, 2009)
