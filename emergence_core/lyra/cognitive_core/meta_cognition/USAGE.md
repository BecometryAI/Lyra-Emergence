# Meta-Cognitive Capabilities - Usage Guide

## Overview

The meta-cognitive system provides three interconnected capabilities for self-observation and learning:

1. **Processing Monitoring** - Track and analyze cognitive process performance
2. **Action-Outcome Learning** - Learn what actions actually achieve
3. **Attention History** - Track attention allocation patterns and effectiveness

## Quick Start

```python
from lyra.cognitive_core.meta_cognition import MetaCognitiveSystem
from lyra.cognitive_core.goals.resources import CognitiveResources

# Initialize the system
meta_system = MetaCognitiveSystem()
```

## 1. Processing Monitoring

### Observing Cognitive Processes

Use the context manager to monitor any cognitive process:

```python
# Monitor a reasoning process
with meta_system.monitor.observe('reasoning') as ctx:
    ctx.input_complexity = 0.7  # Rate input complexity (0-1)
    
    # Perform your cognitive work
    result = perform_reasoning(input_data)
    
    ctx.output_quality = 0.9  # Rate output quality (0-1)
    ctx.resources = CognitiveResources(
        attention_budget=0.5,
        processing_budget=0.6
    )
```

### Getting Process Statistics

```python
# Get statistics for a specific process type
stats = meta_system.monitor.get_process_statistics('reasoning')
print(f"Total executions: {stats.total_executions}")
print(f"Success rate: {stats.success_rate:.2%}")
print(f"Avg duration: {stats.avg_duration_ms:.1f}ms")
print(f"Avg quality: {stats.avg_quality:.2f}")
```

### Identifying Patterns

```python
# Get identified patterns
patterns = meta_system.monitor.get_identified_patterns()

for pattern in patterns:
    print(f"Pattern Type: {pattern.pattern_type}")
    print(f"Description: {pattern.description}")
    print(f"Confidence: {pattern.confidence:.2f}")
    if pattern.actionable:
        print(f"Suggested Adaptation: {pattern.suggested_adaptation}")
```

## 2. Action-Outcome Learning

### Recording Action Outcomes

```python
# Execute an action and record what it achieves
action_id = "act_123"
action_type = "speak"
intended_outcome = "provide helpful response to user query"

# ... perform the action ...

actual_outcome = "provided detailed answer with examples"

# Record the outcome
meta_system.record_action_outcome(
    action_id=action_id,
    action_type=action_type,
    intended=intended_outcome,
    actual=actual_outcome,
    context={
        "user_query_complexity": 0.6,
        "available_context": True,
        "time_pressure": False
    }
)
```

### Assessing Action Reliability

```python
# Get reliability assessment for an action type
reliability = meta_system.get_action_reliability("speak")

print(f"Success rate: {reliability.success_rate:.2%}")
print(f"Avg partial success: {reliability.avg_partial_success:.2f}")

# Check common side effects
for effect, probability in reliability.common_side_effects:
    print(f"Side effect '{effect}' occurs {probability:.1%} of the time")

# See what contexts work best
if reliability.best_contexts:
    print("Best contexts:")
    for ctx in reliability.best_contexts[:3]:
        print(f"  {ctx}")
```

### Predicting Outcomes

```python
# Predict likely outcome before taking action
prediction = meta_system.predict_action_outcome(
    action_type="speak",
    context={
        "user_query_complexity": 0.8,
        "available_context": False
    }
)

print(f"Confidence: {prediction.confidence:.2f}")
print(f"Probability of success: {prediction.probability_success:.2%}")
print(f"Prediction: {prediction.prediction}")
print(f"Likely side effects: {prediction.likely_side_effects}")
```

## 3. Attention Allocation History

### Recording Attention Allocation

```python
# Record where attention is allocated
allocation = {
    "goal_1": 0.6,  # 60% to goal 1
    "goal_2": 0.3,  # 30% to goal 2
    "goal_3": 0.1   # 10% to goal 3
}

alloc_id = meta_system.record_attention(
    allocation=allocation,
    trigger="goal_priority",
    workspace_state=current_workspace_snapshot
)
```

### Recording Attention Outcomes

```python
# After processing, record what was achieved
meta_system.record_attention_outcome(
    allocation_id=alloc_id,
    goal_progress={
        "goal_1": 0.4,  # Made 40% progress on goal 1
        "goal_2": 0.1,  # Made 10% progress on goal 2
        "goal_3": 0.0   # No progress on goal 3
    },
    discoveries=["new_insight_about_goal_1"],
    missed=["missed_important_signal"]
)
```

### Getting Recommended Allocation

```python
# Get recommendation based on learned patterns
recommendation = meta_system.get_recommended_attention(
    context=current_workspace,
    goals=active_goals
)

print("Recommended attention allocation:")
for item, amount in recommendation.items():
    print(f"  {item}: {amount:.1%}")
```

## 4. Self-Assessment and Introspection

### Getting Self-Assessment

```python
# Get comprehensive self-assessment
assessment = meta_system.get_self_assessment()

print("Strengths:")
for strength in assessment.identified_strengths:
    print(f"  ✓ {strength}")

print("\nAreas for Improvement:")
for weakness in assessment.identified_weaknesses:
    print(f"  ⚠ {weakness}")

print("\nSuggested Adaptations:")
for adaptation in assessment.suggested_adaptations:
    print(f"  → {adaptation}")
```

### Introspection Queries

```python
# Ask questions about own cognitive patterns
response = meta_system.introspect("What do I tend to fail at?")
print(response)

response = meta_system.introspect("What am I good at?")
print(response)

response = meta_system.introspect("How effective is my attention?")
print(response)

response = meta_system.introspect("How reliable are my actions?")
print(response)
```

## Integration with Cognitive Loop

### Typical Integration Pattern

```python
class CognitiveCore:
    def __init__(self):
        self.meta_system = MetaCognitiveSystem()
        # ... other initialization ...
    
    def process_cycle(self):
        # Monitor the entire cognitive cycle
        with self.meta_system.monitor.observe('cognitive_cycle') as ctx:
            ctx.input_complexity = self._assess_input_complexity()
            
            # 1. Attention allocation
            allocation = self._allocate_attention()
            alloc_id = self.meta_system.record_attention(
                allocation=allocation,
                trigger="cycle_start",
                workspace_state=self.workspace.snapshot()
            )
            
            # 2. Process and act
            results = self._process_and_act()
            
            # 3. Record action outcomes
            for action in results['actions']:
                self.meta_system.record_action_outcome(
                    action_id=action.id,
                    action_type=action.type,
                    intended=action.intended_outcome,
                    actual=action.actual_outcome,
                    context=action.context
                )
            
            # 4. Record attention outcome
            self.meta_system.record_attention_outcome(
                allocation_id=alloc_id,
                goal_progress=self._compute_goal_progress(),
                discoveries=results['discoveries'],
                missed=results['missed']
            )
            
            ctx.output_quality = self._assess_output_quality(results)
        
        # 5. Periodically check for patterns and adapt
        if self.cycle_count % 100 == 0:
            self._adapt_from_meta_cognition()
    
    def _adapt_from_meta_cognition(self):
        """Adapt behavior based on meta-cognitive insights."""
        assessment = self.meta_system.get_self_assessment()
        
        # Apply suggested adaptations
        for adaptation in assessment.suggested_adaptations:
            self._apply_adaptation(adaptation)
```

## Best Practices

1. **Monitor Important Processes**: Focus on monitoring processes that are critical or error-prone
2. **Provide Context**: Include relevant context when recording outcomes to enable better learning
3. **Record Consistently**: Record outcomes for all actions, not just successes
4. **Review Periodically**: Check self-assessments regularly to identify improvement opportunities
5. **Act on Insights**: Use identified patterns to actually adapt behavior
6. **Rate Honestly**: Provide accurate complexity and quality ratings for better pattern detection

## Advanced Usage

### Custom Process Types

```python
# You can monitor any type of process
with meta_system.monitor.observe('memory_consolidation') as ctx:
    ctx.input_complexity = 0.5
    consolidate_memories()
    ctx.output_quality = 0.8

with meta_system.monitor.observe('goal_selection') as ctx:
    ctx.input_complexity = 0.7
    selected_goals = select_goals()
    ctx.output_quality = 0.9
```

### Filtering Patterns

```python
# Get patterns for specific process type
reasoning_patterns = meta_system.monitor.get_patterns_for_process('reasoning')

# Filter by pattern type
failure_modes = [
    p for p in patterns 
    if p.pattern_type == 'failure_mode'
]
```

### Analyzing Trends

```python
# Get summary of all meta-cognitive data
summary = meta_system.get_summary()

print(f"Total observations: {summary['monitoring']['total_observations']}")
print(f"Total action outcomes: {summary['action_learning']['total_outcomes']}")
print(f"Attention efficiency: {summary['attention_history']['avg_efficiency']:.2f}")
```

## Error Handling

The system gracefully handles failures:

```python
# If a process fails, it's still recorded
with meta_system.monitor.observe('risky_operation') as ctx:
    ctx.input_complexity = 0.9
    try:
        risky_operation()
        ctx.output_quality = 1.0
    except Exception as e:
        ctx.output_quality = 0.0
        # Exception is automatically recorded in observation
        raise  # Re-raise if needed
```

## Performance Considerations

- **Memory Management**: Observations are automatically pruned to prevent unbounded growth
- **Pattern Caching**: Pattern detection results are cached and only recomputed when needed
- **Minimal Overhead**: Context managers add negligible overhead (~1ms) to operations
- **Async-Safe**: All operations are thread-safe and can be used in async contexts

## See Also

- [ARCHITECTURE.md](../../ARCHITECTURE.md) - Overall system architecture
- [test_metacognitive_system.py](../../tests/test_metacognitive_system.py) - Example usage in tests
