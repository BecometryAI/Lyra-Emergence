# Goal Competition System

## Overview

The Goal Competition System implements realistic goal-directed behavior with resource constraints and competitive dynamics. Goals compete for limited cognitive resources (attention, processing, action, time) using activation-based competition with lateral inhibition.

## Key Features

### 1. **Limited Cognitive Resources**
- Four resource dimensions: attention, processing, action, time
- Finite resource pool that goals must compete for
- Resources are allocated to active goals and released when goals complete

### 2. **Activation-Based Competition**
- Goals have activation levels based on importance, urgency, and progress
- Self-excitation: Important goals maintain high activation
- Lateral inhibition: Competing goals suppress each other
- Winner-take-all dynamics: Highest activation goals get resources first

### 3. **Goal Interactions**
- **Interference**: Goals with overlapping resource needs or conflicting outcomes inhibit each other
- **Facilitation**: Goals with shared subgoals or compatible outcomes support each other

### 4. **Dynamic Resource Allocation**
- Resources are allocated based on competition outcomes
- High-activation goals get priority
- Goals wait when resources are insufficient
- Resources reallocate as priorities shift

### 5. **Metrics Tracking**
- Track active vs. waiting goals
- Monitor resource utilization over time
- Count inhibition/facilitation events
- Detect goal switches

## Architecture

```
goals/
├── __init__.py              # Package initialization
├── resources.py             # Resource pool and allocation
├── competition.py           # Competition dynamics and selection
├── interactions.py          # Goal interference/facilitation
└── metrics.py              # Competition metrics tracking
```

## Core Components

### CognitiveResources

Represents the four dimensions of cognitive resources:

```python
from lyra.cognitive_core.goals.resources import CognitiveResources

resources = CognitiveResources(
    attention_budget=0.3,
    processing_budget=0.4,
    action_budget=0.2,
    time_budget=0.5
)
```

### ResourcePool

Manages allocation and release of limited resources:

```python
from lyra.cognitive_core.goals.resources import ResourcePool

pool = ResourcePool()

# Allocate resources to a goal
granted = pool.allocate("goal_id", requested_resources)

# Check availability
can_allocate = pool.can_allocate(requested_resources)

# Release when goal completes
pool.release("goal_id")

# Check utilization
utilization = pool.utilization()  # 0.0 to 1.0
```

### GoalCompetition

Runs competition dynamics and selects active goals:

```python
from lyra.cognitive_core.goals.competition import GoalCompetition

competition = GoalCompetition(inhibition_strength=0.3)

# Run competition to get activation levels
activations = competition.compete(goals, iterations=10)

# Select active goals with resource constraints
active_goals = competition.select_active_goals(goals, pool)

for active_goal in active_goals:
    print(f"{active_goal.goal.id}: activation={active_goal.activation:.2f}")
```

### GoalInteraction

Analyzes how goals interact:

```python
from lyra.cognitive_core.goals.interactions import GoalInteraction

tracker = GoalInteraction()

# Compute all pairwise interactions
interactions = tracker.compute_interactions(goals)

# Find goals that facilitate a target goal
facilitators = tracker.get_facilitating_goals(target_goal, all_goals)

# Find goals that interfere with a target goal
interferers = tracker.get_interfering_goals(target_goal, all_goals)
```

### Metrics Tracking

Monitor competition dynamics over time:

```python
from lyra.cognitive_core.goals.metrics import (
    GoalCompetitionMetrics,
    MetricsTracker
)

tracker = MetricsTracker()

# Record metrics snapshot
metrics = GoalCompetitionMetrics(
    active_goals=len(active),
    waiting_goals=len(waiting),
    total_resource_utilization=pool.utilization()
)
tracker.record(metrics)

# Track goal switches
tracker.track_goal_switch(top_goal_id)

# Get statistics
avg_util = tracker.get_average_utilization()
switches = tracker.get_goal_switches()
```

## Usage Patterns

### Basic Goal Competition

```python
# 1. Create goals with resource needs
goals = [
    Goal(
        id="urgent_task",
        importance=0.9,
        resource_needs=CognitiveResources(0.4, 0.5, 0.3, 0.4)
    ),
    Goal(
        id="background_task",
        importance=0.5,
        resource_needs=CognitiveResources(0.3, 0.3, 0.2, 0.3)
    )
]

# 2. Initialize system
competition = GoalCompetition(inhibition_strength=0.3)
pool = ResourcePool()

# 3. Select active goals
active = competition.select_active_goals(goals, pool)

# 4. Execute active goals...

# 5. Release resources when goals complete
for active_goal in active:
    if goal_completed(active_goal.goal):
        pool.release(active_goal.goal.id)
```

### Handling Goal Interactions

```python
# Detect interference
tracker = GoalInteraction()
interactions = tracker.compute_interactions(goals)

for (g1_id, g2_id), strength in interactions.items():
    if strength < 0:
        print(f"{g1_id} interferes with {g2_id}: {strength}")
    elif strength > 0:
        print(f"{g1_id} facilitates {g2_id}: {strength}")
```

### Monitoring Over Time

```python
metrics_tracker = MetricsTracker()

for cycle in range(num_cycles):
    # Run competition
    active = competition.select_active_goals(goals, pool)
    
    # Record metrics
    metrics = GoalCompetitionMetrics(
        active_goals=len(active),
        waiting_goals=len(goals) - len(active),
        total_resource_utilization=pool.utilization()
    )
    metrics_tracker.record(metrics)
    
    # Track top goal
    if active:
        metrics_tracker.track_goal_switch(active[0].goal.id)

# Analyze
print(f"Average utilization: {metrics_tracker.get_average_utilization()}")
print(f"Goal switches: {metrics_tracker.get_goal_switches()}")
```

## Integration with Existing Systems

### Adding Resource Needs to Goals

The system works with any goal object that has these properties:
- `id`: Unique identifier
- `importance` or `priority`: Importance level (0.0 to 1.0)
- `resource_needs`: CognitiveResources instance (optional, defaults provided)
- `progress`: Progress level (0.0 to 1.0, optional)
- `deadline`: datetime (optional, used for urgency calculation)
- `subgoal_ids`: List of subgoal IDs (optional, for facilitation)
- `metadata`: Dict with optional `conflicts_with`, `facilitates` lists

Example extending existing Goal class:

```python
from lyra.executive_function import Goal
from lyra.cognitive_core.goals.resources import CognitiveResources

# Option 1: Add to metadata
goal = Goal(
    id="my_goal",
    description="Do something",
    priority=0.8
)
goal.metadata["resource_needs"] = CognitiveResources(0.3, 0.3, 0.2, 0.2)

# Option 2: Add as attribute
goal.resource_needs = CognitiveResources(0.3, 0.3, 0.2, 0.2)

# Option 3: Extend the class
class ResourceAwareGoal(Goal):
    def __init__(self, *args, resource_needs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_needs = resource_needs or CognitiveResources(
            0.25, 0.25, 0.25, 0.25
        )
```

### Integration with ExecutiveFunction

```python
from lyra.executive_function import ExecutiveFunction
from lyra.cognitive_core.goals import GoalCompetition, ResourcePool

class ResourceAwareExecutive(ExecutiveFunction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.competition = GoalCompetition(inhibition_strength=0.3)
        self.resource_pool = ResourcePool()
    
    def select_goals_for_execution(self):
        """Select goals to execute based on competition."""
        all_goals = list(self.goals.values())
        active = self.competition.select_active_goals(
            all_goals,
            self.resource_pool
        )
        return [ag.goal for ag in active]
    
    def complete_goal(self, goal_id):
        """Mark goal complete and release resources."""
        super().update_goal_status(goal_id, GoalStatus.COMPLETED)
        self.resource_pool.release(goal_id)
```

## Configuration

### Tuning Inhibition Strength

The `inhibition_strength` parameter (0.0 to 1.0) controls how much goals suppress each other:

- **0.0**: No inhibition, all goals maintain activation (not realistic)
- **0.3**: Moderate inhibition, allows some concurrent goals (recommended)
- **0.5**: Strong inhibition, favors single-goal focus
- **1.0**: Maximum inhibition, winner-take-all dynamics

```python
# Moderate competition (allows multiple active goals)
comp = GoalCompetition(inhibition_strength=0.3)

# Strong competition (favors focus)
comp = GoalCompetition(inhibition_strength=0.7)
```

### Default Resource Needs

If goals don't specify resource needs, defaults are used:

```python
default_needs = CognitiveResources(
    attention_budget=0.2,
    processing_budget=0.2,
    action_budget=0.2,
    time_budget=0.2
)
```

You can customize this in the competition logic or on individual goals.

## Testing

Run the test suite:

```bash
# Run all goal competition tests
python -m pytest emergence_core/tests/test_goal_competition.py -v

# Run standalone demonstration
python test_goal_competition_standalone.py

# Run integration example
python example_goal_competition.py
```

## Performance Considerations

### Competition Iterations

The `compete()` method runs iterative dynamics. More iterations = more convergence but slower:

```python
# Fast but may not fully converge
activations = comp.compete(goals, iterations=5)

# Default, good balance
activations = comp.compete(goals, iterations=10)

# High accuracy, slower
activations = comp.compete(goals, iterations=20)
```

### Interaction Caching

The `GoalInteraction` class caches computed interactions:

```python
tracker = GoalInteraction()

# First computation calculates and caches
interactions = tracker.compute_interactions(goals)

# Subsequent calls use cache
interactions = tracker.compute_interactions(goals)  # Fast!

# Clear cache if goals change significantly
tracker.clear_cache()
```

### Metrics History

The `MetricsTracker` keeps a bounded history:

```python
# Keep last 100 snapshots (default)
tracker = MetricsTracker(max_history=100)

# Keep more history for long-running analysis
tracker = MetricsTracker(max_history=1000)

# Keep minimal history for low memory usage
tracker = MetricsTracker(max_history=10)
```

## Future Enhancements

Potential areas for extension:

1. **Dynamic Resource Regeneration**: Resources slowly regenerate over time
2. **Goal Persistence**: Goals that fail competition multiple times get a boost
3. **Learned Inhibition**: System learns which goals truly conflict vs. can coexist
4. **Emotional Modulation**: Emotional state affects resource availability
5. **Context-Dependent Resources**: Different contexts provide different resource budgets
6. **Multi-Level Competition**: Hierarchical goals compete within their level

## References

This implementation is inspired by:

- **Neural Networks**: Lateral inhibition in competitive neural networks
- **Cognitive Psychology**: Working memory capacity limits (Miller's 7±2)
- **Goal Management Theory**: Multiple goals compete for limited executive resources
- **Computational Cognitive Architectures**: ACT-R, SOAR goal management

## See Also

- `emergence_core/lyra/executive_function.py` - Executive function and goal management
- `emergence_core/lyra/cognitive_core/workspace.py` - Global workspace (conscious content)
- `emergence_core/lyra/cognitive_core/attention.py` - Attention control system
