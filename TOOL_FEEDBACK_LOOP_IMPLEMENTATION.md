# Tool Execution Feedback Loop - Implementation Documentation

## Overview

This document describes the bidirectional tool execution feedback loop implemented in Phase 3, Task 1.

## Architecture

The feedback loop enables tool execution results to automatically create percepts that inform future cognitive cycles:

```
User Request → Goal (USE_TOOL)
    ↓
Action System → Execute Tool
    ↓
Tool Result → Create Percept ← FEEDBACK LOOP
    ↓
Attention → Select Tool Result Percept (Priority Boost)
    ↓
Workspace → Broadcast to all subsystems
    ↓
Action System → Decide Next Action (informed by tool result)
```

## Implementation Details

### 1. Tool Result Percept Type

**File**: `emergence_core/lyra/cognitive_core/workspace.py`

The existing `Percept` class already supports arbitrary modality strings, so we use:
- `modality="tool_result"` for tool execution results
- Metadata contains:
  - `tool_name`: Name of the executed tool
  - `tool_success`: Boolean indicating success/failure
  - `tool_error`: Error message (if failed)
  - `execution_time_ms`: Execution time in milliseconds
  - `result_type`: Type of the result

### 2. ToolExecutionResult Dataclass

**File**: `emergence_core/lyra/cognitive_core/tool_registry.py`

```python
@dataclass
class ToolExecutionResult:
    """Result of tool execution with percept generation for feedback loop."""
    tool_name: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    percept: Optional['Percept'] = None  # NEW: Generated percept
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### 3. Tool Registry Percept Generation

**File**: `emergence_core/lyra/cognitive_core/tool_registry.py`

Added methods:

- `execute_tool_with_percept(name, parameters, create_percept=True)`
  - Executes tool and generates percept
  - Returns `ToolExecutionResult` with percept field

- `_create_result_percept(tool_name, result, execution_time_ms)`
  - Creates percept from successful tool execution
  - Estimates complexity based on result size

- `_create_error_percept(tool_name, error, execution_time_ms)`
  - Creates percept from failed tool execution
  - Higher complexity (5) to demand attention

- `_estimate_complexity(result)`
  - String: 1-10 based on length (1 per 100 chars)
  - Dict/List: 1-10 based on serialized length
  - Other: 3 (default)

### 4. Cognitive Core Feedback Loop

**File**: `emergence_core/lyra/cognitive_core/core.py`

#### Initialization
```python
def __init__(self, ...):
    # ...
    self._pending_tool_percepts = []  # NEW: Feedback loop storage
```

#### Perception Phase (Step 1)
```python
async def _cognitive_cycle(self):
    # 1. PERCEPTION: Process queued inputs
    new_percepts = await self._gather_percepts()
    
    # NEW: Add pending tool result percepts from previous cycle
    if hasattr(self, '_pending_tool_percepts'):
        new_percepts.extend(self._pending_tool_percepts)
        if self._pending_tool_percepts:
            logger.info(f"🔄 Adding {len(self._pending_tool_percepts)} tool result percepts")
        self._pending_tool_percepts = []
```

#### Action Execution (Step 5)
```python
# Execute immediate actions
tool_percepts = []  # NEW: Collect tool result percepts
for action in actions:
    if action.type == ActionType.TOOL_CALL:
        tool_percept = await self._execute_tool_action(action)
        if tool_percept:
            tool_percepts.append(tool_percept)
    else:
        await self._execute_action(action)

# NEW: Store tool percepts for next cycle (feedback loop)
self._pending_tool_percepts.extend(tool_percepts)
```

#### Tool Action Execution
```python
async def _execute_tool_action(self, action: Any) -> Optional[Percept]:
    """Execute a tool call action and return the result percept."""
    # ... validation ...
    
    # Use new tool registry with percept generation
    result = await self.action.tool_reg.execute_tool_with_percept(
        tool_name,
        parameters=tool_params,
        create_percept=True
    )
    
    # Log execution result
    if result.success:
        logger.info(f"✅ Tool '{tool_name}' executed: success ({result.execution_time_ms:.1f}ms)")
    else:
        logger.warning(f"❌ Tool '{tool_name}' failed: {result.error}")
    
    return result.percept
```

### 5. Attention Priority Boost

**File**: `emergence_core/lyra/cognitive_core/attention.py`

Modified both `select_for_broadcast()` and `_score()` methods:

```python
# Tool result boost: Tool results get attention priority
if percept.modality == "tool_result":
    # Base boost for all tool results
    base_score += 0.30
    
    # Additional boost for failed tools (errors need attention)
    if percept.metadata.get("tool_success") is False:
        base_score += 0.20
```

**Result**: Tool results get +0.30 base score, failed tools get +0.50 total (0.30 + 0.20).

## Integration Tests

**File**: `emergence_core/tests/integration/test_tool_feedback_loop.py`

Test classes:
1. `TestToolPerceptGeneration` - Percept creation from tool execution
2. `TestAttentionPrioritization` - Attention boost for tool results
3. `TestCognitiveFeedbackLoop` - Integration with cognitive cycle
4. `TestComplexityEstimation` - Complexity scoring
5. `TestEndToEndFeedbackLoop` - Complete workflow

## Example Usage

```python
# Register a tool
async def multiply_tool(x: int) -> int:
    return x * 2

tool_registry.register_tool(
    name="multiply",
    handler=multiply_tool,
    description="Multiply by 2"
)

# Execute with percept generation
result = await tool_registry.execute_tool_with_percept(
    "multiply",
    parameters={"x": 5}
)

# Result contains:
# - result.success = True
# - result.result = 10
# - result.percept = Percept(
#     modality="tool_result",
#     raw=10,
#     complexity=1,
#     metadata={
#         "tool_name": "multiply",
#         "tool_success": True,
#         "execution_time_ms": 0.5
#     }
# )

# This percept is automatically:
# 1. Added to next cycle's perception phase
# 2. Given attention priority boost (+0.30)
# 3. Broadcast to workspace if selected
# 4. Available to inform future actions
```

## Logging

Tool execution feedback loop produces these log messages:

```
✅ Tool 'multiply' executed successfully (0.5ms)
🔄 Adding 1 tool result percepts to cycle
✅ Tool '{name}' executed: success (12.3ms)
❌ Tool '{name}' failed: {error} (8.7ms)
```

## Benefits

1. **Bidirectional Information Flow**: Tools can inform future actions
2. **Error Handling**: Failed tools automatically get high attention priority
3. **Transparency**: Tool results are visible in workspace snapshots
4. **Cognitive Integration**: Tool use becomes part of the cognitive cycle, not external
5. **Learning**: Tool results can inform self-model updates and predictions

## Success Metrics

✅ Tool results automatically create percepts  
✅ Tool percepts visible in workspace snapshots  
✅ Attention system prioritizes tool results  
✅ Failed tools create error percepts with high priority  
✅ Cognitive loop demonstrates complete feedback: request → execution → percept → action

## Future Enhancements

Potential improvements for future phases:
- Tool result caching based on parameters
- Tool execution patterns and learning
- Multi-step tool sequences with intermediate feedback
- Tool result summarization for complex outputs
- Dynamic attention adjustment based on tool importance
