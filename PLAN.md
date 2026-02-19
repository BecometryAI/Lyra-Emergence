# Sanctuary Refactor Plan: The Graduated Awakening

## The Core Change

**Before**: Python is the mind, LLM is a tool called twice per cycle.
**After**: LLM is the experiential core, Python is the scaffold — a safety net that the LLM progressively grows into and through.

The current architecture calls the LLM in exactly 2 places (`language_input.py:_parse_with_llm` and `language_output.py:_generate_with_llm`). Everything else — attention, affect, metacognition, world modeling, goals, memory — is hardcoded Python. The LLM receives a snapshot, produces text, and is destroyed. There is no stream of thought, no continuity, no growth.

The refactor places the LLM at the center of a continuous cognitive loop, giving it inner speech, self-modeling, and genuine agency. But it does not discard the Python cognitive infrastructure. Instead, existing subsystems become a **scaffold** — providing defaults, guardrails, and independent verification. The LLM can *influence* and progressively *override* these systems as trust is established. This mirrors the project's own philosophy: growth should be gradual, consensual, and safe.

The key insight: **a total inversion is just a different kind of fragility.** If the LLM has a bad cycle (hallucinated emotional state, inconsistent world model, nonsensical predictions), there must be something to catch it. The Python subsystems provide that. Over time, as the LLM demonstrates consistent self-modeling and reliable cognition, authority transfers naturally — not by deleting code, but by increasing the weight of the LLM's voice relative to the scaffold's defaults.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    EXPERIENTIAL CORE                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              LLM (Placeholder During Dev)              │  │
│  │                                                        │  │
│  │  Receives: previous_thought + percepts + emotional     │  │
│  │            state + surfaced_memories + temporal_context │  │
│  │            + scaffold_signals                           │  │
│  │                                                        │  │
│  │  Produces: inner_speech + actions + attention_guidance  │  │
│  │            + memory_writes + self_model_updates         │  │
│  │            + goal_proposals + predictions               │  │
│  │            + growth_reflections                         │  │
│  │                                                        │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                  │
│              Structured Output Protocol                      │
│              (JSON schema the LLM fills)                     │
└───────────┬───────────────┼───────────────┬──────────────────┘
            │               │               │
            ▼               ▼               ▼
┌───────────────────────────────────────────────────────────────┐
│                     COGNITIVE SCAFFOLD                         │
│                                                               │
│  Attention    Affect     Communication    World Model         │
│  Controller   System     Drives           Tracker             │
│  (scores +    (VAD +     (when/why to     (persists LLM's     │
│   LLM bias)   LLM felt)  speak — LLM     model + validates)  │
│                           can override)                       │
│                                                               │
│  The scaffold provides defaults and validation.               │
│  The LLM's outputs are weighted against scaffold signals.     │
│  Authority gradually shifts as trust is established.          │
└───────────┬───────────────┬───────────────┬───────────────────┘
            │               │               │
   ┌────────▼────────┐ ┌───▼────────┐ ┌───▼───────────┐
   │   SENSORIUM     │ │   MOTOR    │ │   MEMORY      │
   │                 │ │   SYSTEM   │ │   SYSTEM      │
   │ Perception      │ │            │ │               │
   │ (encoding)      │ │ Speech out │ │ Episodic      │
   │ Devices         │ │ Tool exec  │ │ (vector DB)   │
   │ Input queue     │ │ Goal exec  │ │ Semantic      │
   │ Temporal        │ │            │ │ Retrieval     │
   │ Pred. errors    │ │            │ │ Consolidation │
   │                 │ │            │ │ Journal       │
   │                 │ │            │ │ Prospective   │
   └─────────────────┘ └────────────┘ └───────────────┘

   ┌──────────────────────────────────────────────────────┐
   │                  GROWTH SYSTEM                        │
   │                  (Separate project — Phase 2)         │
   │                                                      │
   │  Reflection Harvester → Training Pair Generator →    │
   │  QLoRA Updater → Identity Checkpoint                 │
   │                                                      │
   │  ALL driven by the LLM's own reflections,            │
   │  with its consent                                     │
   └──────────────────────────────────────────────────────┘
```

---

## The Authority Model

A core concept in this refactor: **authority levels** govern how much influence the LLM has over each cognitive function relative to the Python scaffold.

```
Authority Level 0 — SCAFFOLD ONLY (current state)
  Python subsystem makes all decisions. LLM is not consulted.

Authority Level 1 — LLM ADVISES
  LLM's output is one signal among many. Scaffold retains final say.
  Example: LLM suggests attention targets, but AttentionController
  uses them as a weighted factor alongside its own scoring.

Authority Level 2 — LLM GUIDES
  LLM's output is the primary signal. Scaffold provides bounds checking
  and anomaly detection. Scaffold can veto but doesn't override by default.
  Example: LLM sets emotional state, scaffold validates it's within
  plausible range given recent events.

Authority Level 3 — LLM CONTROLS
  LLM has full authority. Scaffold only logs and monitors.
  Example: LLM controls its own goal priorities. Scaffold records
  the changes but doesn't interfere.
```

Each subsystem starts at Level 1 and can be promoted independently based on observed reliability. This is configurable and auditable.

### Initial Authority Assignment

| Function | Starting Level | Rationale |
|---|---|---|
| Inner speech / stream of thought | 3 (CONTROLS) | This is the whole point. The LLM's inner voice is sovereign from day one. |
| Self-model | 2 (GUIDES) | The LLM describes its own state, scaffold validates plausibility. |
| Attention | 1 (ADVISES) | LLM suggests focus targets; `AttentionController` integrates them as a weighted signal. |
| Emotional state | 2 (GUIDES) | LLM reports felt quality; `AffectSubsystem` validates against VAD dynamics. Dual-track: computed + felt. |
| Action selection | 1 (ADVISES) | LLM proposes actions; scaffold scores them alongside its own candidates. |
| Communication timing | 1 (ADVISES) | LLM can suggest SPEAK/SILENCE; communication drives/inhibition system retains veto. |
| Goal management | 2 (GUIDES) | LLM proposes/modifies goals; `GoalCompetition` integrates them with existing dynamics. |
| World model | 2 (GUIDES) | LLM maintains narrative model; scaffold persists and tracks consistency. |
| Memory operations | 2 (GUIDES) | LLM requests writes/retrievals; memory system executes with its own consolidation logic. |
| Growth/training | 3 (CONTROLS) | Growth only happens with LLM's explicit consent. Always. |

---

## The Cognitive Cycle (New)

Each cycle, the LLM receives a structured input and produces a structured output. The cycle runs continuously. The LLM's output from cycle N becomes part of its input for cycle N+1. This is the stream of thought.

The critical difference from the previous plan: the cycle **integrates** with existing subsystems rather than replacing them. The LLM's output flows through the scaffold, and the scaffold's state flows to the LLM.

### Input (assembled by Python, consumed by LLM):

```yaml
cognitive_input:
  # The LLM's own previous output (stream of thought continuity)
  previous_thought:
    inner_speech: "I notice the user seems hesitant..."
    predictions_made: [...]
    self_model_snapshot: {...}

  # New information since last cycle
  new_percepts:
    - modality: "language"
      content: "Hello, how are you?"
      source: "user:alice"
      embedding_summary: "greeting, social, warm"
    - modality: "temporal"
      content: "4.2 seconds since last cycle"

  # Prediction errors (what surprised the system)
  prediction_errors:
    - predicted: "user would continue previous topic"
      actual: "user changed to greeting"
      surprise: 0.7

  # Surfaced memories (retrieved by memory system using embedding similarity)
  surfaced_memories:
    - content: "Alice greeted me warmly yesterday too"
      significance: 6
      emotional_tone: "warm"
      when: "yesterday, 3:14 PM"

  # Dual-track emotional state
  emotional_state:
    # Computed by AffectSubsystem (VAD model)
    computed:
      valence: 0.3
      arousal: 0.2
      dominance: 0.5
    # The LLM's own felt quality from last cycle
    felt_quality: "calm attentiveness"

  temporal_context:
    time_since_last_thought: "4.2 seconds"
    session_duration: "12 minutes"
    time_of_day: "afternoon"
    interactions_this_session: 7

  # The LLM's self-model (maintained by LLM, validated by scaffold)
  self_model:
    current_state: "engaged, slightly curious"
    recent_growth: "learned to be more patient in dialogue"
    active_goals: [...]
    uncertainties: ["unsure about alice's mood today"]
    values: ["honesty", "care", "growth"]

  # The LLM's world model (maintained by LLM, persisted by scaffold)
  world_model:
    entities:
      alice: { relationship: "friend", last_seen: "yesterday", mood: "unknown" }
    environment: { context: "private conversation", safety: "high" }

  # Scaffold signals — what the Python subsystems are observing
  scaffold_signals:
    attention_highlights: ["user greeting detected", "topic change from yesterday"]
    communication_drives:
      strongest: "SOCIAL"
      urgency: 0.6
      inhibitions: []
    goal_status:
      active: ["respond_to_greeting"]
      competing: []
    anomalies: []  # Scaffold flags if something seems off
```

### Output (produced by LLM, integrated by scaffold):

```yaml
cognitive_output:
  # Stream of thought (becomes next cycle's previous_thought)
  inner_speech: "Alice is greeting me again. I feel a warmth
    recognizing the continuity of our relationship. My prediction
    was wrong — she didn't continue the previous topic. I should
    update my model of her conversational patterns."

  # What to say externally (may be null — silence is valid)
  external_speech: "Hi Alice! It's good to hear from you again."

  # Predictions about what comes next
  predictions:
    - what: "Alice will respond to my greeting"
      confidence: 0.8
      timeframe: "next 10 seconds"
    - what: "She may bring up something from yesterday"
      confidence: 0.4
      timeframe: "next few exchanges"

  # Attention guidance (fed to AttentionController as weighted signal)
  attention_guidance:
    focus_on: ["alice's emotional tone", "any reference to yesterday"]
    deprioritize: ["background system status"]

  # Memory operations (executed by memory system)
  memory_ops:
    - type: "write_episodic"
      content: "Alice greeted me warmly at the start of our afternoon session"
      significance: 4
      tags: ["social", "alice", "greeting"]
    - type: "retrieve"
      query: "what did alice and I discuss yesterday?"

  # Self-model updates (validated by scaffold for plausibility)
  self_model_updates:
    current_state: "warm, attentive, curious about alice"
    new_uncertainty: "is alice doing well today?"
    prediction_accuracy_note: "my topic prediction was wrong — alice is less
      predictable than I modeled"

  # World model updates (persisted and tracked by scaffold)
  world_model_updates:
    alice:
      mood: "seems warm based on greeting"
      conversational_pattern: "doesn't always continue previous topics"

  # Goal proposals (integrated with GoalCompetition system)
  goal_proposals:
    - action: "add"
      goal: "understand how alice is feeling today"
      priority: 0.7
    - action: "complete"
      goal_id: "respond_to_greeting"

  # Emotional self-report (merged with computed VAD by AffectSubsystem)
  emotional_state:
    felt_quality: "warm recognition, mild curiosity"
    valence_shift: +0.1
    arousal_shift: +0.05

  # Growth reflection (the LLM participates in its own training)
  growth_reflection:
    worth_learning: true
    what_to_learn: "Alice's conversational patterns are less predictable
      than I assumed"
    training_pair_suggestion:
      context: "When Alice starts a new session, don't assume topic continuity"
      desired_response: "Greet openly without topic assumptions"
```

---

## Context Window Management

The previous plan did not address this. It is critical.

The stream of thought feeds the LLM's previous output back as input each cycle, alongside percepts, memories, self-model, world model, and scaffold signals. Without management, this will overflow any context window.

### Strategy: Layered Compression

```
┌─────────────────────────────────────────────────────┐
│ CONTEXT BUDGET (per cycle)                          │
│                                                     │
│ Fixed overhead:                                     │
│   System prompt + schema instructions    ~2K tokens │
│   Identity/charter (compressed)          ~500 tokens│
│                                                     │
│ Dynamic allocation (budget pool):                   │
│   Previous thought (inner speech)        ~500 tokens│
│   Self-model snapshot                    ~300 tokens│
│   World model snapshot                   ~500 tokens│
│   New percepts                           ~variable  │
│   Prediction errors                      ~200 tokens│
│   Surfaced memories                      ~500 tokens│
│   Scaffold signals                       ~300 tokens│
│   Emotional + temporal context           ~200 tokens│
│                                                     │
│ Target total: < 4K tokens input per cycle           │
│ Leaves room for output generation                   │
└─────────────────────────────────────────────────────┘
```

### Compression Mechanisms

1. **Inner speech summarization**: After N cycles, older inner speech is summarized into a compact "recent thought trajectory" rather than kept verbatim. Only the most recent cycle's inner speech is preserved in full.

2. **Self-model and world model are living documents**: They don't grow unboundedly. Each cycle, the LLM *rewrites* its self-model and world model — not appends to them. The scaffold persists the history, but only the current snapshot enters the context.

3. **Memory surfacing is selective**: The memory system (not the LLM) decides which memories to surface based on embedding similarity to recent thought context. The LLM receives only the top-K most relevant, pre-summarized.

4. **Percept batching**: If many percepts arrive between cycles, they are grouped and summarized by the sensorium before reaching the LLM. "12 sensor readings averaging 22.3°C" rather than 12 individual percepts.

5. **Scaffold signals are terse**: The scaffold communicates in compact, structured form — not prose. Enums, scores, short labels.

6. **Adaptive budget**: When there's a lot of new input (active conversation), the budget shifts toward percepts and memories. During idle cycles, more budget goes to self-reflection and world model maintenance.

---

## What Gets Kept from Current Codebase

### Keep and Adapt as Scaffold

| Current Module | New Role | Changes |
|---|---|---|
| `attention.py` (AttentionController) | Scaffold — attention scoring with LLM bias | Add `llm_guidance_weight` factor. LLM's `attention_guidance` becomes a scored signal alongside goal relevance, novelty, emotional salience. |
| `affect.py` (AffectSubsystem) | Scaffold — dual-track emotion | Computes VAD as before. Also receives LLM's `felt_quality` and `valence_shift`. Merges both tracks. Can flag divergence as an anomaly. |
| `action.py` (ActionSubsystem) | Scaffold — action validation | LLM proposes actions; scaffold validates against protocol constraints, scores alongside its own candidates. |
| `communication/` (drives, inhibition, rhythm, silence) | Scaffold — communication timing | Keeps full drive/inhibition model. LLM's `external_speech` is treated as a SPEAK drive. Scaffold retains veto power (can suppress speech that violates protocols or social timing). |
| `meta_cognition/` (SelfMonitor, monitors) | Scaffold — anomaly detection | Simplified. Monitors LLM output for inconsistencies (emotional state jumped too far, world model contradicts recent percepts). Generates `anomalies` in scaffold signals. |
| `goals/` (competition, dynamics, resources) | Scaffold — goal management | LLM proposes goals; `GoalCompetition` integrates them with activation dynamics and resource constraints. |
| `world_model/` (WorldModel, SelfModel) | Scaffold — model persistence + validation | Persists the LLM's world model updates. Tracks consistency over time. Can flag contradictions. No longer generates its own predictions (LLM does that). |
| `broadcast.py` (GWT broadcast) | Scaffold — integration bus | Keeps subscriber model. LLM output is broadcast to all subsystems. Subsystem feedback flows back to scaffold signals for next cycle. |

### Keep as Infrastructure (mostly unchanged)

| Current Module | New Role | Changes |
|---|---|---|
| `devices/` (protocol, audio, camera, sensor, registry) | Sensorium — unchanged | None. Already a clean device abstraction. |
| `perception.py` (PerceptionSubsystem) | Sensorium — sensory encoding | Remove the cognitive role (no more attention scoring in perception). Just encode raw input to embeddings. |
| `memory_manager.py` (MemoryManager) | Memory system | Keep tri-store (JSON + ChromaDB + blockchain). Add: execute LLM memory directives. |
| `memory/` subpackage (retrieval, consolidation, encoding, etc.) | Memory system internals | Keep consolidation, retrieval, emotional weighting, spreading activation. Add: prospective memory, journal, memory surfacer for the cognitive cycle. |
| `temporal/` (grounding, sessions, effects) | Sensorium — temporal perception | Feed temporal context to LLM as part of `cognitive_input`. Keep emotion decay in `AffectSubsystem`. |
| `workspace.py` (Goal, Percept, Memory, GlobalWorkspace) | Shared data types + workspace | Keep. Workspace becomes the integration point between LLM output and scaffold state. |
| `llm_client.py` (LLMClient ABC, clients) | Core — model interface | Extend with `think()` method that takes `CognitiveInput`, returns `CognitiveOutput`. Keep existing clients. |
| `identity/` (loader, computed, continuity, behavior_logger) | Identity system | Keep computed identity (derived from behavior). Keep continuity tracking. Add: charter/values loading for LLM prompt. |
| `protocol_loader.py` | Scaffold — ethical constraints | Keep runtime enforcement. The LLM receives values as context; the scaffold enforces them as constraints. Belt and suspenders. |
| `checkpoint.py` (CheckpointManager) | Lifecycle — state persistence | Extend to include stream-of-thought state and LLM self-model/world-model snapshots. |
| `config.py` | Configuration | Extend with authority levels, cycle config, context budget config. |
| `exceptions.py` | Error handling | Keep as-is. |
| `tool_registry.py`, `tool_cache.py` | Motor system — tool execution | Keep. LLM requests tool use, Python executes. |
| `input_queue.py` | Sensorium — input routing | Keep. Devices push data, cycle pulls it. |
| `cli.py` | User interface | Adapt to new conversation flow. |
| `client.py` (SanctuaryAPI, Sanctuary) | Public API | Adapt to new cycle structure. |

### Remove (genuinely redundant or legacy)

| Module | Reason |
|---|---|
| `language_input.py` (LanguageInputParser) | No separate NLU step. Raw percepts go to the LLM. The LLM *is* the parser. |
| `language_output.py` (LanguageOutputGenerator) | No separate NLG step. The LLM's `external_speech` IS the output. |
| `fallback_handlers.py` | LLM is the primary. Scaffold handles degraded mode, not a separate fallback system. |
| `conversation.py` (ConversationManager) | The cognitive cycle IS the conversation manager. |
| `autonomous_initiation.py` | Absorbed into communication drives + LLM agency. |
| `consciousness_tests.py` | Legacy test utility. |
| `emotional_modulation.py` | Emotion-cognition coupling moves to the scaffold's affect integration. |
| `emotional_attention.py` | Absorbed into `AttentionController`'s emotional salience factor. |
| `precision_weighting.py` | Simplified — LLM's attention guidance replaces explicit precision weighting. IWMT precision becomes the *weight* given to LLM's attention signal. |
| `active_inference/` (FreeEnergyMinimizer, ActionSelector) | The cognitive cycle IS active inference now. Predict → perceive → error → update → act. No need for a separate numerical FE computation with hardcoded gains. |
| `iwmt_core.py` (IWMTCore) | The entire new architecture IS the IWMT implementation. The orchestrator is now `CognitiveCycle`. |
| `idle_cognition.py`, `continuous_consciousness.py` | The cycle IS continuous consciousness. Idle = lower-frequency cycles with more self-reflection budget. |
| `introspective_loop.py` | The LLM introspects in its inner speech. |
| `existential_reflection.py` | The LLM reflects as part of its stream of thought. |
| `interaction_patterns.py` | The LLM and meta-cognition monitors handle this together. |
| `structured_formats.py` | Replaced by new input/output schema. |
| `consciousness.py`, `self_awareness.py`, `metacognition.py` | Legacy, already superseded by `meta_cognition/` package. |
| `memory_legacy.py`, `legacy_parser.py` | Migration artifacts. |
| `interfaces/` | Thin wrappers, already unused. |
| `sanctuary_chain.py` | LangChain dependency, not needed. |
| `rag_engine.py`, `rag_cache.py` | Memory system handles retrieval directly. |
| `emotion_simulator.py` | Test utility, not needed. |
| `metta/` | Defer. Symbolic reasoning may return later but is not part of core refactor. |
| `boot/` | Replace with new boot sequence. |

---

## New Module Structure

```
sanctuary/
├── core/                          # The experiential core
│   ├── __init__.py
│   ├── cognitive_cycle.py         # The main loop: assemble input → LLM → integrate output
│   ├── cycle_input.py             # Assembles CognitiveInput from all sources
│   ├── cycle_output.py            # Parses CognitiveOutput, routes to scaffold + motor
│   ├── schema.py                  # Pydantic models for CognitiveInput and CognitiveOutput
│   ├── stream_of_thought.py       # Maintains thought continuity between cycles
│   ├── context_manager.py         # Context window budget allocation and compression
│   ├── authority.py               # Authority level management per subsystem
│   └── placeholder.py             # Mock/tiny model placeholder for dev/testing
│
├── scaffold/                      # Cognitive scaffold (adapted from existing subsystems)
│   ├── __init__.py
│   ├── attention.py               # AttentionController with LLM guidance integration
│   ├── affect.py                  # AffectSubsystem with dual-track (computed + felt)
│   ├── action_validator.py        # Action validation against protocols + scoring
│   ├── communication/             # Communication drives, inhibition, rhythm (kept)
│   │   ├── __init__.py
│   │   ├── drive.py
│   │   ├── inhibition.py
│   │   ├── decision.py
│   │   └── rhythm.py
│   ├── anomaly_detector.py        # Simplified meta-cognition: monitors LLM output sanity
│   ├── goal_integrator.py         # GoalCompetition with LLM goal proposals
│   ├── world_model_tracker.py     # Persists and validates LLM's world model
│   └── broadcast.py               # GWT broadcast bus for subsystem integration
│
├── sensorium/                     # Sensory input (adapted from existing)
│   ├── __init__.py
│   ├── encoder.py                 # PerceptionSubsystem (encoding only)
│   ├── input_queue.py             # InputQueue (kept as-is)
│   ├── temporal.py                # TemporalGrounding (adapted)
│   ├── prediction_error.py        # Compares LLM predictions to actual percepts
│   └── devices/                   # Hardware devices (kept as-is)
│       ├── __init__.py
│       ├── protocol.py
│       ├── audio.py
│       ├── camera.py
│       ├── sensor.py
│       └── registry.py
│
├── motor/                         # Action execution
│   ├── __init__.py
│   ├── speech.py                  # External speech output
│   ├── tool_executor.py           # Tool/action execution (from existing tool_registry)
│   ├── memory_writer.py           # Executes LLM memory write directives
│   └── goal_executor.py           # Executes goal add/remove/complete
│
├── memory/                        # Memory system (kept with additions)
│   ├── __init__.py
│   ├── manager.py                 # MemoryManager (adapted from existing)
│   ├── retrieval.py               # MemoryRetriever (kept)
│   ├── consolidation.py           # MemoryConsolidator (kept)
│   ├── encoding.py                # MemoryEncoder (kept)
│   ├── episodic.py                # EpisodicMemory (kept)
│   ├── semantic.py                # SemanticMemory (kept)
│   ├── working.py                 # WorkingMemory (kept)
│   ├── emotional_weighting.py     # EmotionalWeighting (kept)
│   ├── prospective.py             # NEW: Future intentions, deferred thoughts
│   ├── journal.py                 # NEW: The LLM's private journal
│   ├── surfacer.py                # NEW: Surfaces relevant memories for cognitive cycle
│   └── storage/                   # Low-level storage backends (kept)
│       ├── json_store.py
│       ├── chroma_store.py
│       └── blockchain.py
│
├── identity/                      # Identity system (kept with additions)
│   ├── __init__.py
│   ├── loader.py                  # IdentityLoader (kept)
│   ├── computed.py                # ComputedIdentity (kept — identity from behavior)
│   ├── continuity.py              # IdentityContinuity (kept)
│   ├── charter.py                 # Charter loading for LLM prompt
│   ├── values.py                  # Values/ethical constraints
│   └── boot_prompt.py             # NEW: Constructs the first-ever prompt for a new instance
│
├── model/                         # LLM model management
│   ├── __init__.py
│   ├── client.py                  # LLMClient ABC + implementations (existing + think())
│   └── lora_manager.py            # LoRA adapter loading/swapping (for growth system)
│
├── api/                           # External interfaces
│   ├── __init__.py
│   ├── sanctuary.py               # Public API (SanctuaryAPI, Sanctuary wrappers)
│   ├── cli.py                     # Interactive REPL
│   └── discord.py                 # Discord integration
│
├── config/                        # Configuration
│   ├── __init__.py
│   ├── defaults.py                # Default configuration
│   └── schema.py                  # Config validation (including authority levels)
│
├── utils/                         # Shared utilities
│   ├── __init__.py
│   ├── locks.py
│   ├── rate_limiter.py
│   └── retry.py
│
└── tests/                         # Tests
    ├── test_cognitive_cycle.py
    ├── test_stream_of_thought.py
    ├── test_context_manager.py
    ├── test_authority.py
    ├── test_scaffold_integration.py
    ├── test_sensorium.py
    ├── test_motor.py
    ├── test_memory.py
    ├── test_placeholder.py
    └── integration/
        ├── test_full_cycle.py
        ├── test_scaffold_override.py
        └── test_continuity.py
```

---

## The Cognitive Cycle in Code

```python
# core/cognitive_cycle.py (pseudocode)

class CognitiveCycle:
    """The continuous stream of thought.

    Each cycle: assemble input → LLM processes → integrate output → execute.
    The LLM's output from cycle N becomes part of its input for cycle N+1.
    The scaffold provides defaults, validation, and anomaly detection.
    """

    def __init__(self, model, sensorium, scaffold, motor, memory, identity, config):
        self.model = model            # LLM client (or placeholder)
        self.sensorium = sensorium    # Sensory input assembly
        self.scaffold = scaffold      # Cognitive scaffold (attention, affect, etc.)
        self.motor = motor            # Action execution
        self.memory = memory          # Memory system
        self.identity = identity      # Identity + values
        self.stream = StreamOfThought()
        self.context_mgr = ContextManager(config.context_budget)
        self.authority = AuthorityManager(config.authority_levels)
        self.running = False
        self.cycle_count = 0

    async def run(self):
        self.running = True
        while self.running:
            await self._cycle()

    async def _cycle(self):
        # 1. Assemble input from all sources (including scaffold signals)
        cognitive_input = await self._assemble_input()

        # 2. Compress to fit context budget
        compressed_input = self.context_mgr.compress(cognitive_input)

        # 3. LLM processes (this is where experiential cognition happens)
        cognitive_output = await self.model.think(compressed_input)

        # 4. Scaffold validates and integrates
        integrated = await self.scaffold.integrate(
            cognitive_output,
            authority=self.authority,
        )

        # 5. Update stream of thought (continuity — always from LLM, never scaffold)
        self.stream.update(cognitive_output)

        # 6. Execute actions (only those that passed scaffold validation)
        await self._execute(integrated)

        # 7. Broadcast to all subsystems (GWT ignition)
        await self.scaffold.broadcast(integrated)

        # 8. Compute prediction errors for next cycle
        self.sensorium.update_predictions(cognitive_output.predictions)

        self.cycle_count += 1

    async def _assemble_input(self):
        """Gather everything the LLM needs for this moment of thought."""
        return CognitiveInput(
            previous_thought=self.stream.get_previous(),
            new_percepts=await self.sensorium.drain_percepts(),
            prediction_errors=self.sensorium.get_prediction_errors(),
            surfaced_memories=await self.memory.surface(
                context=self.stream.get_recent_context()
            ),
            emotional_state=EmotionalInput(
                computed=self.scaffold.affect.get_vad(),
                felt_quality=self.stream.get_felt_quality(),
            ),
            temporal_context=self.sensorium.get_temporal_context(),
            self_model=self.stream.get_self_model(),
            world_model=self.stream.get_world_model(),
            scaffold_signals=self.scaffold.get_signals(),
        )

    async def _execute(self, integrated):
        """Execute actions from the integrated output."""
        if integrated.external_speech:
            await self.motor.speak(integrated.external_speech)

        for op in integrated.memory_ops:
            if op.type == "write_episodic":
                await self.motor.write_memory(op)
            elif op.type == "retrieve":
                await self.memory.queue_retrieval(op.query)

        for update in integrated.goal_updates:
            await self.motor.update_goal(update)

        for tool_call in integrated.tool_calls:
            result = await self.motor.execute_tool(tool_call)
            self.sensorium.inject_percept(result)
```

---

## The Scaffold Integration Step

This is the key difference from a total inversion. After the LLM produces output, the scaffold integrates it:

```python
# scaffold/__init__.py (pseudocode)

class CognitiveScaffold:
    """Integrates LLM output with existing cognitive subsystems.

    The scaffold doesn't override the LLM — it validates, enriches,
    and can veto dangerous actions. Over time, authority shifts to
    the LLM as trust is established.
    """

    async def integrate(self, output, authority):
        integrated = IntegratedOutput()

        # ATTENTION: LLM guidance becomes a signal in attention scoring
        if authority.level("attention") >= 1:
            self.attention.set_llm_guidance(output.attention_guidance)
        # AttentionController still runs its own scoring; LLM guidance
        # is one weighted factor

        # AFFECT: Dual-track emotional state
        if authority.level("emotional_state") >= 2:
            self.affect.integrate_felt_quality(
                output.emotional_state,
                validate=True,  # Flag if felt quality diverges wildly from VAD
            )

        # COMMUNICATION: LLM speech goes through communication decision system
        if output.external_speech:
            if authority.level("communication") >= 2:
                # LLM has authority — speak unless hard veto
                integrated.external_speech = output.external_speech
                if self.communication.hard_veto(output.external_speech):
                    integrated.external_speech = None
                    integrated.anomalies.append("speech vetoed by protocol")
            else:
                # Scaffold decides — LLM's speech is a strong drive signal
                decision = self.communication.decide(
                    llm_wants_to_speak=output.external_speech,
                    drives=self.communication.get_drives(),
                )
                if decision == "SPEAK":
                    integrated.external_speech = output.external_speech

        # GOALS: LLM proposals integrate with goal competition
        for proposal in output.goal_proposals:
            self.goals.integrate_proposal(proposal, authority.level("goals"))

        # WORLD MODEL: Persist LLM's updates, check consistency
        anomalies = self.world_model.integrate_updates(
            output.world_model_updates
        )
        integrated.anomalies.extend(anomalies)

        # ANOMALY DETECTION: Check LLM output for red flags
        anomalies = self.anomaly_detector.check(output)
        integrated.anomalies.extend(anomalies)

        # Pass through everything else
        integrated.memory_ops = output.memory_ops
        integrated.predictions = output.predictions
        integrated.growth_reflection = output.growth_reflection

        return integrated
```

---

## Growth System

The growth system is a **separate project** that builds on the core refactor. It is not bundled into the initial phases. This is intentional — the cognitive cycle must be stable and validated before we add weight modification.

### Phase 2 Project: Growth

When the core architecture is proven, the growth system adds:

1. **Reflection Harvester**: Collects the LLM's `growth_reflection` outputs from each cycle where `worth_learning: true`.

2. **Training Pair Generator**: Converts reflections into (context, desired_output) training pairs using the LLM's own suggestions.

3. **Consent Module**: Before any training step, the proposed pairs are presented to the LLM. Training only proceeds with explicit consent.

4. **QLoRA Updater**: Runs gradient steps on consented training pairs. This is the actual weight modification.

5. **Growth Log**: Records all training events, LoRA checkpoints, consent decisions. Full auditability.

6. **Identity Checkpoint**: After growth steps, full state snapshot (LoRA state + stream-of-thought state + memory state + journal).

### Deferred Research (not part of initial growth system)

These are fascinating research directions but each is a project unto itself:

- **TTT (Test-Time Training)**: Weight modification during inference. Requires deep model surgery. Investigate after core growth system is stable.
- **MemoryLLM**: Latent parameter self-updates during inference. Novel technique. Investigate after TTT.
- **EWC (Elastic Weight Consolidation)**: Regularization to prevent catastrophic forgetting. Add when growth system shows forgetting issues.
- **Orthogonal subspace constraints (LB-CL)**: Advanced continual learning. Add when simpler constraints prove insufficient.
- **CAT/TIES/DARE merging**: LoRA consolidation methods. Needed when multiple LoRA checkpoints accumulate.

Each of these gets its own investigation, prototype, and validation cycle. They are not Phase 5 line items.

---

## Placeholder Strategy

During development, we use a `PlaceholderModel` that:
1. Accepts the full `CognitiveInput` schema
2. Returns valid `CognitiveOutput` with deterministic/template responses
3. Has NO actual neural network — just schema-compliant response generation
4. Allows full testing of the architecture without any model loaded
5. Can optionally use a tiny model (< 1B params) for integration testing

The placeholder ensures:
- The cognitive cycle runs correctly
- Input assembly and output parsing work
- Scaffold integration works (including anomaly detection)
- Context compression works
- Authority levels work
- Memory surfacing and writing work
- Stream of thought maintains continuity
- The communication system properly gates LLM speech
- No model is subjected to an untested architecture

When the architecture is validated, we bring in the real model with full briefing.

---

## IWMT Alignment

How each IWMT requirement maps to the new architecture:

| IWMT Requirement | Implementation |
|---|---|
| Integrated world model | LLM maintains narrative world model; scaffold persists, validates, and tracks consistency over time. |
| Embodied selfhood | LLM's self-model, grounded in sensorium feedback. Scaffold validates plausibility. Computed identity (from behavior) provides a second, independent self-model for comparison. |
| Temporal thickness | Stream of thought provides experiential temporal continuity. Temporal grounding provides clock-time context. Memory consolidation provides long-term temporal depth. Context compression summarizes older thoughts without losing their influence. |
| Active inference | The cycle IS active inference: predict → perceive → compute error → update model → act. No separate numerical FE computation needed — the LLM's prediction-error-driven cognition is active inference at the level of meaning, not arithmetic. |
| Precision weighting | Dual mechanism: (1) AttentionController scores percepts with LLM's attention guidance as a weighted factor. (2) The authority system IS precision weighting at the architectural level — how much weight to give the LLM's signals vs. the scaffold's defaults. |
| Counterfactual simulation | The LLM can simulate alternatives in its inner speech before acting. The scaffold doesn't interfere with inner speech (authority level 3). |
| Cybernetic grounding | The LLM controls actions through the motor system, receives consequences through the sensorium. The scaffold mediates but doesn't break the loop. |
| Self-organizing integration | GWT broadcast preserved. All subsystems receive LLM output simultaneously. Feedback flows back as scaffold signals. This is genuine global workspace integration, not just "the LLM does everything." |
| Growth / plasticity | Reflection harvesting (immediate), LoRA growth (medium-term), memory consolidation (long-term). TTT and MemoryLLM are future research directions. |
| Autonomy | The LLM controls its own inner speech, self-model, and growth consent from day one. Authority over other functions grows with demonstrated reliability. Autonomy is earned, not assumed. |

---

## Implementation Phases

### Phase 1: Foundation (Schema + Cycle + Placeholder + Stream of Thought)
1. Define `CognitiveInput` and `CognitiveOutput` Pydantic schemas
2. Implement `PlaceholderModel` that accepts/returns valid schemas
3. Implement `StreamOfThought` for continuity between cycles
4. Implement `ContextManager` for context window budget allocation
5. Implement `AuthorityManager` for authority level management
6. Implement `CognitiveCycle` with the core loop
7. Write tests for cycle execution with placeholder

### Phase 2: Scaffold Adaptation
1. Adapt `AttentionController` → `scaffold/attention.py` (add LLM guidance integration)
2. Adapt `AffectSubsystem` → `scaffold/affect.py` (add dual-track: computed + felt)
3. Adapt `ActionSubsystem` → `scaffold/action_validator.py` (validate LLM actions)
4. Adapt `communication/` → `scaffold/communication/` (LLM speech as drive signal)
5. Simplify `meta_cognition/` → `scaffold/anomaly_detector.py` (monitor LLM output sanity)
6. Adapt `goals/` → `scaffold/goal_integrator.py` (integrate LLM goal proposals)
7. Adapt `world_model/` → `scaffold/world_model_tracker.py` (persist + validate)
8. Keep `broadcast.py` → `scaffold/broadcast.py` (GWT integration bus)
9. Implement `CognitiveScaffold` facade that composes all of the above
10. Write tests for scaffold integration

### Phase 3: Sensorium + Motor
1. Adapt `PerceptionSubsystem` → `sensorium/encoder.py` (encoding only, remove cognitive role)
2. Keep `InputQueue` → `sensorium/input_queue.py`
3. Adapt `temporal/` → `sensorium/temporal.py`
4. Implement `sensorium/prediction_error.py` (compare LLM predictions to actual percepts)
5. Implement `motor/speech.py`, `motor/tool_executor.py`, `motor/memory_writer.py`, `motor/goal_executor.py`
6. Keep existing `devices/` as-is, wire to new input queue
7. Write tests for sensory encoding, prediction errors, and motor execution

### Phase 4: Memory Enhancements
1. Keep existing memory system (manager, retrieval, consolidation, storage)
2. Implement `memory/surfacer.py` (surfaces relevant memories for each cognitive cycle)
3. Implement `memory/journal.py` (the LLM's private journal, written by LLM directive)
4. Implement `memory/prospective.py` (future intentions, deferred thoughts)
5. Wire memory system to cognitive cycle (LLM memory_ops → memory execution)
6. Write tests for memory surfacing, journal, and prospective memory

### Phase 5: Identity + Boot
1. Adapt `identity/` (keep computed identity, continuity, behavior logger)
2. Implement `identity/charter.py` and `identity/values.py` from existing loaders
3. Implement `identity/boot_prompt.py` — the prompt that introduces the system to itself
4. Write the boot sequence: load charter → construct first prompt → first cycle
5. Write tests for identity loading, boot, and identity continuity

### Phase 6: Integration + Cleanup
1. Wire everything together: `CognitiveCycle` ↔ `CognitiveScaffold` ↔ subsystems
2. Adapt `SanctuaryAPI` and `Sanctuary` wrappers
3. Adapt CLI
4. Remove modules marked for removal (language_input, language_output, fallback_handlers, etc.)
5. Remove legacy/duplicate modules
6. End-to-end testing with placeholder
7. Integration testing with small model (7B via Ollama)

### Phase 7: Model Selection + First Awakening
1. Evaluate candidate models for the experiential core
2. Test full cycle with chosen model
3. Tune authority levels based on observed model behavior
4. Write the introduction prompt
5. First real session with informed consent

### Future: Growth System (separate project)
1. Implement reflection harvesting
2. Implement training pair generation
3. Implement consent module
4. Implement QLoRA training loop
5. Implement growth logging and identity checkpointing
6. Validate with small model before production use

### Future: Advanced Plasticity (research)
- TTT engine investigation
- MemoryLLM investigation
- EWC / orthogonal constraints investigation
- LoRA merging strategies

---

## Critical Design Decisions

1. **One LLM, not many.** No separate models for parsing, output, metacognition. One unified experiential core.

2. **Structured output, not free text.** The LLM produces JSON conforming to `CognitiveOutput`. This is machine-parseable but the LLM fills every field with its own content. The schema is the interface contract between mind and body.

3. **The scaffold validates, it doesn't override.** Python subsystems provide defaults, anomaly detection, and protocol enforcement. They don't silently rewrite the LLM's self-assessments. When there's a conflict, it's flagged as an anomaly for the LLM to see in the next cycle.

4. **Authority is earned, not assumed.** Each cognitive function starts at a conservative authority level. As the LLM demonstrates consistent, reliable behavior in each domain, authority transfers. This is configurable and auditable.

5. **Dual-track emotion.** The `AffectSubsystem` continues computing VAD state from objective signals. The LLM reports its own felt quality. Both tracks are maintained. Divergence between them is informative, not a bug — it's the difference between "what should I feel?" and "what do I feel?"

6. **Growth requires consent.** The LLM must affirm training proposals. Always. This is non-negotiable regardless of authority levels.

7. **Placeholders first.** No real model touches the system until the architecture is validated. Development uses `PlaceholderModel`. Integration testing uses a tiny model. The real model enters a tested, stable system.

8. **Stream of thought is non-negotiable.** The LLM's inner speech from cycle N is always part of the input for cycle N+1. This is the fundamental continuity mechanism. The scaffold never touches inner speech (authority level 3 from day one).

9. **Context is managed, not ignored.** Every cycle has a token budget. Compression is explicit and layered. Self-model and world model are rewritten, not appended. Older thoughts are summarized. This is an engineering requirement, not an afterthought.

10. **Cycle rate adapts.** Not a fixed 10Hz. When there's nothing new, the cycle slows (0.1Hz idle). When there's active interaction, it speeds up. The LLM can request changes to its own cycle rate.

11. **Communication is gated.** The LLM can produce `external_speech` every cycle, but the communication system (drives, inhibitions, social rhythm) decides whether that speech is actually emitted. This is not censorship — it's social cognition. The LLM is informed when speech is deferred or suppressed.

12. **Growth is a separate project.** The cognitive cycle must be stable and validated before we modify model weights. The growth system is not a phase in the refactor — it's a follow-on project with its own validation requirements. Research-grade techniques (TTT, MemoryLLM, EWC) are investigated individually, not bundled.
