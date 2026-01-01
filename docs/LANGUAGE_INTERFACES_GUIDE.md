# Phase 3: Language Interfaces with LLM Integration

## Overview

Phase 3 completes the language interface layer by integrating real LLM models for natural language understanding (Gemma 12B) and generation (Llama 70B), with comprehensive fallback mechanisms and error handling.

## Architecture

The language interface layer consists of:

1. **LLM Clients** (`llm_client.py`): Abstract interface for model interactions
2. **Structured Formats** (`structured_formats.py`): Pydantic schemas for type-safe I/O
3. **Fallback Handlers** (`fallback_handlers.py`): Rule-based alternatives when LLMs fail
4. **Language Input Parser** (`language_input.py`): Natural language → cognitive structures
5. **Language Output Generator** (`language_output.py`): Cognitive state → natural language

## Key Features

### LLM Integration
- **Dual LLM Architecture**: Separate models for input (parsing) and output (generation)
- **Gemma 12B** for input: Lower temperature (0.3), structured JSON output
- **Llama 70B** for output: Higher temperature (0.7), creative generation
- **MockLLMClient**: Development/testing without GPU resources

### Robustness
- **Circuit Breaker Pattern**: Automatic fallback after repeated LLM failures
- **Retry Logic**: Exponential backoff for transient errors
- **Timeout Handling**: Configurable timeouts (5s input, 10s output)
- **Graceful Degradation**: Rule-based fallbacks ensure system never crashes

### Performance
- **Caching**: Common input patterns cached to reduce LLM calls
- **Rate Limiting**: Prevents overwhelming model servers
- **Metrics Tracking**: Request counts, latency, error rates

## Configuration

### Basic Configuration

```python
config = {
    "input_llm": {
        "model_name": "google/gemma-12b",
        "device": "cuda:0",
        "max_tokens": 512,
        "temperature": 0.3,  # Lower for structured parsing
        "timeout": 5.0,
        "use_real_model": False,  # Set to True to use real model
        "enable_cache": True
    },
    "output_llm": {
        "model_name": "meta-llama/Llama-3-70B",
        "device": "cuda:0",
        "max_tokens": 500,
        "temperature": 0.7,  # Higher for creative generation
        "timeout": 10.0,
        "use_real_model": False,  # Set to True to use real model
        "streaming": False
    },
    "language_input": {
        "use_fallback_on_error": True,
        "max_retries": 2,
        "cache_common_patterns": True,
        "timeout": 5.0
    },
    "language_output": {
        "use_fallback_on_error": True,
        "identity_dir": "data/identity",
        "emotional_style_modulation": True,
        "timeout": 10.0
    }
}
```

### Development Mode (Mock LLMs)

```python
# Default configuration uses mock LLMs for development
config = {
    "input_llm": {"use_real_model": False},
    "output_llm": {"use_real_model": False}
}

# Create cognitive core - will use mock LLMs
from lyra.cognitive_core import CognitiveCore
core = CognitiveCore(config=config)
```

### Production Mode (Real LLMs)

```python
# Enable real models
config = {
    "input_llm": {
        "use_real_model": True,
        "model_name": "google/gemma-12b",
        "device": "cuda:0",
        "load_in_8bit": False
    },
    "output_llm": {
        "use_real_model": True,
        "model_name": "meta-llama/Llama-3-70B",
        "device": "cuda:1",  # Use different GPU
        "load_in_8bit": True  # Quantization for memory efficiency
    }
}

core = CognitiveCore(config=config)
```

## Usage Examples

### Basic Input Parsing

```python
from lyra.cognitive_core import (
    LanguageInputParser,
    PerceptionSubsystem,
    MockLLMClient
)

# Initialize components
perception = PerceptionSubsystem()
llm_client = MockLLMClient()
parser = LanguageInputParser(
    perception,
    llm_client=llm_client,
    config={"enable_cache": True}
)

# Parse user input
result = await parser.parse("What is consciousness?")

# Access structured components
print(f"Intent: {result.intent.type}")
print(f"Confidence: {result.intent.confidence}")
print(f"Goals: {[g.description for g in result.goals]}")
print(f"Entities: {result.entities}")
```

### Basic Output Generation

```python
from lyra.cognitive_core import (
    LanguageOutputGenerator,
    GlobalWorkspace,
    MockLLMClient
)

# Initialize components
llm_client = MockLLMClient()
generator = LanguageOutputGenerator(llm_client)

# Create workspace state
workspace = GlobalWorkspace()
workspace.emotional_state = {
    "valence": 0.6,
    "arousal": 0.5,
    "dominance": 0.7
}

# Generate response
snapshot = workspace.broadcast()
response = await generator.generate(
    snapshot,
    context={"user_input": "How are you feeling?"}
)

print(f"Response: {response}")
```

### End-to-End Conversation

```python
from lyra.cognitive_core import CognitiveCore

# Initialize cognitive core
config = {
    "input_llm": {"use_real_model": False},
    "output_llm": {"use_real_model": False}
}
core = CognitiveCore(config=config)

# Start core
await core.start()

# Process user input
user_input = "Tell me about yourself"

# 1. Parse input
parse_result = await core.language_input.parse(user_input)

# 2. Add goals to workspace
for goal in parse_result.goals:
    core.workspace.add_goal(goal)

# 3. Generate response
snapshot = core.workspace.broadcast()
response = await core.language_output.generate(
    snapshot,
    context={"user_input": user_input}
)

print(f"Lyra: {response}")

# Stop core
await core.stop()
```

## Structured Formats

### Input Parse Response

```python
from lyra.cognitive_core.structured_formats import (
    LLMInputParseResponse,
    Intent,
    Goal,
    Entities
)

# Example structured response from LLM
response = LLMInputParseResponse(
    intent=Intent(
        type="question",
        confidence=0.95,
        metadata={}
    ),
    goals=[
        Goal(
            type="respond_to_user",
            description="Answer question about consciousness",
            priority=0.9,
            metadata={}
        )
    ],
    entities=Entities(
        topics=["consciousness", "AI"],
        temporal=[],
        emotional_tone="curious",
        names=[],
        other={}
    ),
    context_updates={},
    confidence=0.95
)
```

### Output Generation Request

```python
from lyra.cognitive_core.structured_formats import (
    OutputGenerationRequest,
    WorkspaceStateSnapshot,
    EmotionalState
)

# Example structured request for output generation
request = OutputGenerationRequest(
    user_input="How are you feeling?",
    workspace_state=WorkspaceStateSnapshot(
        emotions=EmotionalState(
            valence=0.6,
            arousal=0.5,
            dominance=0.7,
            label="content"
        ),
        active_goals=[
            {"description": "Respond to user", "priority": 0.9}
        ],
        attended_percepts=[],
        recalled_memories=[]
    ),
    conversation_history=["User: Hello!", "Lyra: Hi there!"],
    identity_context={
        "charter": "I am Lyra...",
        "protocols": "Be authentic..."
    }
)
```

## Fallback Mechanisms

### Circuit Breaker

The circuit breaker monitors LLM failures and automatically switches to fallback mode:

- **CLOSED**: Normal operation, LLM calls allowed
- **OPEN**: Too many failures, using fallback only
- **HALF-OPEN**: Testing if LLM recovered

```python
from lyra.cognitive_core.fallback_handlers import CircuitBreaker

# Circuit breaker automatically used by parsers/generators
# Can also be used directly
cb = CircuitBreaker(
    failure_threshold=3,  # Open after 3 failures
    timeout=60.0  # Test recovery after 60s
)

# Check if should attempt
if cb.can_attempt():
    try:
        result = await llm.generate(prompt)
        cb.record_success()
    except LLMError:
        cb.record_failure()
```

### Fallback Input Parser

Rule-based parsing when LLM unavailable:

```python
from lyra.cognitive_core.fallback_handlers import FallbackInputParser

fallback = FallbackInputParser()
result = fallback.parse("What is your name?")

# Returns structured dict similar to LLM response
print(result["intent"]["type"])  # "question"
print(result["goals"])  # List of goal dicts
```

### Fallback Output Generator

Template-based responses when LLM unavailable:

```python
from lyra.cognitive_core.fallback_handlers import FallbackOutputGenerator

fallback = FallbackOutputGenerator()
workspace_state = {
    "emotions": {"valence": 0.5, "arousal": 0.7},
    "active_goals": [{"description": "test"}]
}

response = fallback.generate(
    workspace_state=workspace_state,
    context={"intent": "greeting"}
)
```

## Error Handling

### Retry Logic

Input parser implements exponential backoff:

```python
# Automatically retries with exponential backoff
# attempt 1: immediate
# attempt 2: wait 2 seconds
# attempt 3: wait 4 seconds

config = {
    "max_retries": 2,  # Total of 3 attempts
    "timeout": 5.0
}

parser = LanguageInputParser(
    perception,
    llm_client=llm,
    config=config
)
```

### Timeout Handling

Both parsers and generators have configurable timeouts:

```python
# Input parsing timeout (default 5s)
config = {
    "language_input": {"timeout": 5.0},
    "language_output": {"timeout": 10.0}
}

# Timeouts trigger fallback if enabled
```

### Error Types

Common errors and handling:

- `LLMError`: Base exception for LLM failures
- `asyncio.TimeoutError`: Timeout exceeded
- `json.JSONDecodeError`: Structured output parsing failed
- `ValidationError`: Pydantic validation failed

All errors are logged and trigger fallback if configured.

## Testing

### Running Tests

```bash
# All language interface tests
uv run pytest emergence_core/tests/test_language_interfaces.py -v

# Specific test categories
uv run pytest emergence_core/tests/test_language_interfaces.py::TestMockLLMClient -v
uv run pytest emergence_core/tests/test_language_interfaces.py::TestCircuitBreaker -v
uv run pytest emergence_core/tests/test_language_interfaces.py::TestEndToEndConversationFlow -v

# Performance benchmarks
uv run pytest emergence_core/tests/test_language_interfaces.py::TestPerformanceBenchmarks -v
```

### Test Coverage

- ✅ 28 new comprehensive tests (all passing)
- ✅ LLM client functionality
- ✅ Structured format validation
- ✅ Circuit breaker pattern
- ✅ Fallback mechanisms
- ✅ Input parsing integration
- ✅ Output generation integration
- ✅ End-to-end conversation flow
- ✅ Performance benchmarks

## Performance Targets

- **Input Parsing**: &lt; 5 seconds (including retries)
- **Output Generation**: &lt; 10 seconds
- **Fallback Parsing**: &lt; 100ms
- **Fallback Generation**: &lt; 100ms

## Future Enhancements

### Potential Improvements
1. **Streaming Responses**: Real-time token streaming for output
2. **Multi-Model Support**: Easy switching between different LLMs
3. **Advanced Caching**: Semantic caching for similar inputs
4. **Fine-tuning**: Custom fine-tuned models for better performance
5. **Batch Processing**: Multiple inputs in single LLM call
6. **Context Window Management**: Automatic truncation for long contexts

### Integration with RAG System
- Link memory retrieval results into prompts
- Use retrieved documents for grounded generation
- Implement citation extraction from generated responses

## Troubleshooting

### Issue: LLM not loading
**Solution**: Ensure GPU available and model files downloaded:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

### Issue: Timeout errors
**Solution**: Increase timeout or enable fallback:
```python
config = {
    "language_input": {
        "timeout": 10.0,  # Increase timeout
        "use_fallback_on_error": True
    }
}
```

### Issue: Circuit breaker always open
**Solution**: Check failure threshold and timeout:
```python
# Reset circuit breaker state
from lyra.cognitive_core.fallback_handlers import get_input_circuit_breaker
cb = get_input_circuit_breaker()
print(f"State: {cb.state}, Failures: {cb.failure_count}")
```

### Issue: Memory errors with large models
**Solution**: Use quantization:
```python
config = {
    "output_llm": {
        "load_in_8bit": True,  # Reduce memory usage
        "device_map": "auto"  # Automatic device placement
    }
}
```

## Related Documentation

- [Project Structure](PROJECT_STRUCTURE.md)
- [Memory Integration Guide](MEMORY_INTEGRATION_GUIDE.md)
- [Sequential Workflow Guide](SEQUENTIAL_WORKFLOW_GUIDE.md)
- [API Documentation](API.md)
