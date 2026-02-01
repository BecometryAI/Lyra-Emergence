"""
Bottleneck Detector: Monitors cognitive load and detects processing bottlenecks.

This module implements meta-cognitive monitoring that detects when the cognitive
system is overloaded, enabling self-preserving behavior:
- Pause lower-priority goals when resources are exhausted
- Inhibit communication when processing capacity is limited
- Generate introspective percepts about overwhelm states

Key metrics monitored:
- Workspace queue depth (percept count)
- Subsystem execution times vs. historical baseline
- Goal queue length vs. available resources
- Memory consolidation lag
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Deque
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)


class BottleneckType(Enum):
    """Types of cognitive bottlenecks."""
    WORKSPACE_OVERLOAD = "workspace_overload"     # Too many percepts in workspace
    SUBSYSTEM_SLOWDOWN = "subsystem_slowdown"     # Subsystem taking longer than normal
    GOAL_RESOURCE_EXHAUSTION = "goal_resource_exhaustion"  # Goals competing for limited resources
    MEMORY_LAG = "memory_lag"                     # Memory consolidation falling behind
    CYCLE_OVERRUN = "cycle_overrun"               # Cognitive cycle exceeding target duration


@dataclass
class BottleneckSignal:
    """
    A detected bottleneck condition.

    Attributes:
        bottleneck_type: Type of bottleneck detected
        severity: How severe the bottleneck is (0.0 to 1.0)
        source: Which subsystem or component is affected
        description: Human-readable description
        detected_at: When the bottleneck was detected
        consecutive_cycles: How many cycles this has persisted
        metrics: Raw metrics that triggered detection
    """
    bottleneck_type: BottleneckType
    severity: float
    source: str
    description: str
    detected_at: datetime = field(default_factory=datetime.now)
    consecutive_cycles: int = 1
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate severity is in range."""
        self.severity = max(0.0, min(1.0, self.severity))


@dataclass
class BottleneckState:
    """
    Overall bottleneck state of the cognitive system.

    Attributes:
        is_bottlenecked: Whether system is currently bottlenecked
        overall_load: Combined load factor (0.0 to 1.0)
        active_bottlenecks: List of current bottleneck signals
        recommendation: Suggested action (e.g., "pause_low_priority_goals")
        last_updated: When state was last computed
    """
    is_bottlenecked: bool = False
    overall_load: float = 0.0
    active_bottlenecks: List[BottleneckSignal] = field(default_factory=list)
    recommendation: str = "normal_operation"
    last_updated: datetime = field(default_factory=datetime.now)

    def get_severity(self) -> float:
        """Get maximum severity among active bottlenecks."""
        if not self.active_bottlenecks:
            return 0.0
        return max(b.severity for b in self.active_bottlenecks)


class BottleneckDetector:
    """
    Detects cognitive processing bottlenecks and generates appropriate signals.

    Monitors:
    - Workspace queue depth
    - Subsystem execution times
    - Goal resource utilization
    - Memory consolidation lag
    - Overall cycle duration

    Outputs:
    - BottleneckState for other subsystems to query
    - Introspective percepts about overwhelm
    - Inhibition signals for communication system
    """

    # Detection thresholds
    DEFAULT_WORKSPACE_OVERLOAD_THRESHOLD = 20  # Max percepts before overload
    DEFAULT_SUBSYSTEM_SLOWDOWN_FACTOR = 2.0    # 2x baseline = slow
    DEFAULT_RESOURCE_EXHAUSTION_THRESHOLD = 0.9  # 90% utilization = exhausted
    DEFAULT_CYCLE_DURATION_TARGET_MS = 100     # Target cycle time in ms
    DEFAULT_CONSECUTIVE_CYCLES_FOR_BOTTLENECK = 3  # Must persist for 3 cycles
    DEFAULT_MEMORY_LAG_THRESHOLD_MS = 500      # Memory consolidation threshold

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the bottleneck detector.

        Args:
            config: Optional configuration dict with thresholds
        """
        self.config = config or {}

        # Load thresholds from config
        self.workspace_overload_threshold = self.config.get(
            "workspace_overload_threshold",
            self.DEFAULT_WORKSPACE_OVERLOAD_THRESHOLD
        )
        self.subsystem_slowdown_factor = self.config.get(
            "subsystem_slowdown_factor",
            self.DEFAULT_SUBSYSTEM_SLOWDOWN_FACTOR
        )
        self.resource_exhaustion_threshold = self.config.get(
            "resource_exhaustion_threshold",
            self.DEFAULT_RESOURCE_EXHAUSTION_THRESHOLD
        )
        self.cycle_duration_target_ms = self.config.get(
            "cycle_duration_target_ms",
            self.DEFAULT_CYCLE_DURATION_TARGET_MS
        )
        self.consecutive_cycles_threshold = self.config.get(
            "consecutive_cycles_for_bottleneck",
            self.DEFAULT_CONSECUTIVE_CYCLES_FOR_BOTTLENECK
        )
        self.memory_lag_threshold_ms = self.config.get(
            "memory_lag_threshold_ms",
            self.DEFAULT_MEMORY_LAG_THRESHOLD_MS
        )

        # Historical data for baseline computation
        self.timing_history: Deque[Dict[str, float]] = deque(maxlen=100)
        self.load_history: Deque[float] = deque(maxlen=100)

        # Tracking for consecutive cycles
        self._bottleneck_counters: Dict[str, int] = {}

        # Current state
        self._current_state = BottleneckState()

        # Baseline timings (computed from history)
        self._baseline_timings: Dict[str, float] = {}

        logger.info("BottleneckDetector initialized")

    def update(
        self,
        subsystem_timings: Dict[str, float],
        workspace_percept_count: int,
        goal_resource_utilization: float,
        goal_queue_depth: int = 0,
        waiting_goals: int = 0
    ) -> BottleneckState:
        """
        Update bottleneck detection with current metrics.

        Args:
            subsystem_timings: Dict of subsystem name -> execution time in ms
            workspace_percept_count: Number of percepts currently in workspace
            goal_resource_utilization: Resource utilization from goal competition (0.0-1.0)
            goal_queue_depth: Number of active goals
            waiting_goals: Number of goals waiting for resources

        Returns:
            Current BottleneckState
        """
        # Store timing history for baseline computation
        self.timing_history.append(subsystem_timings.copy())
        self._update_baseline_timings()

        # Detect various bottleneck types
        bottlenecks: List[BottleneckSignal] = []

        # 1. Workspace overload
        workspace_signal = self._detect_workspace_overload(workspace_percept_count)
        if workspace_signal:
            bottlenecks.append(workspace_signal)

        # 2. Subsystem slowdowns
        slowdown_signals = self._detect_subsystem_slowdowns(subsystem_timings)
        bottlenecks.extend(slowdown_signals)

        # 3. Goal resource exhaustion
        resource_signal = self._detect_resource_exhaustion(
            goal_resource_utilization,
            goal_queue_depth,
            waiting_goals
        )
        if resource_signal:
            bottlenecks.append(resource_signal)

        # 4. Memory consolidation lag
        memory_signal = self._detect_memory_lag(subsystem_timings)
        if memory_signal:
            bottlenecks.append(memory_signal)

        # 5. Cycle overrun
        cycle_signal = self._detect_cycle_overrun(subsystem_timings)
        if cycle_signal:
            bottlenecks.append(cycle_signal)

        # Compute overall load
        overall_load = self._compute_overall_load(
            workspace_percept_count,
            goal_resource_utilization,
            subsystem_timings
        )
        self.load_history.append(overall_load)

        # Determine if system is bottlenecked (must persist for consecutive cycles)
        is_bottlenecked = self._evaluate_bottleneck_persistence(bottlenecks)

        # Generate recommendation
        recommendation = self._generate_recommendation(bottlenecks, overall_load)

        # Update state
        self._current_state = BottleneckState(
            is_bottlenecked=is_bottlenecked,
            overall_load=overall_load,
            active_bottlenecks=bottlenecks,
            recommendation=recommendation,
            last_updated=datetime.now()
        )

        # Log if bottlenecked
        if is_bottlenecked:
            logger.warning(
                f"Cognitive bottleneck detected: load={overall_load:.1%}, "
                f"bottlenecks={len(bottlenecks)}, recommendation={recommendation}"
            )

        return self._current_state

    def _update_baseline_timings(self) -> None:
        """Update baseline timings from history."""
        if len(self.timing_history) < 10:
            return

        # Compute median timing for each subsystem
        all_subsystems = set()
        for timings in self.timing_history:
            all_subsystems.update(timings.keys())

        for subsystem in all_subsystems:
            values = [t.get(subsystem, 0) for t in self.timing_history if subsystem in t]
            if values:
                sorted_values = sorted(values)
                mid = len(sorted_values) // 2
                self._baseline_timings[subsystem] = sorted_values[mid]

    def _detect_workspace_overload(self, percept_count: int) -> Optional[BottleneckSignal]:
        """Detect if workspace has too many percepts."""
        if percept_count <= self.workspace_overload_threshold:
            self._bottleneck_counters.pop("workspace_overload", None)
            return None

        # Compute severity based on how far over threshold
        excess = percept_count - self.workspace_overload_threshold
        severity = min(1.0, excess / self.workspace_overload_threshold)

        # Track consecutive cycles
        counter_key = "workspace_overload"
        self._bottleneck_counters[counter_key] = self._bottleneck_counters.get(counter_key, 0) + 1

        return BottleneckSignal(
            bottleneck_type=BottleneckType.WORKSPACE_OVERLOAD,
            severity=severity,
            source="workspace",
            description=f"Workspace holding {percept_count} percepts (threshold: {self.workspace_overload_threshold})",
            consecutive_cycles=self._bottleneck_counters[counter_key],
            metrics={"percept_count": percept_count, "threshold": self.workspace_overload_threshold}
        )

    def _detect_subsystem_slowdowns(self, timings: Dict[str, float]) -> List[BottleneckSignal]:
        """Detect subsystems running slower than baseline."""
        signals = []

        for subsystem, duration_ms in timings.items():
            baseline = self._baseline_timings.get(subsystem)
            if baseline is None or baseline < 1.0:  # Skip if no baseline or too small
                continue

            slowdown_ratio = duration_ms / baseline
            if slowdown_ratio < self.subsystem_slowdown_factor:
                self._bottleneck_counters.pop(f"slowdown_{subsystem}", None)
                continue

            severity = min(1.0, (slowdown_ratio - 1.0) / (self.subsystem_slowdown_factor * 2))

            counter_key = f"slowdown_{subsystem}"
            self._bottleneck_counters[counter_key] = self._bottleneck_counters.get(counter_key, 0) + 1

            signals.append(BottleneckSignal(
                bottleneck_type=BottleneckType.SUBSYSTEM_SLOWDOWN,
                severity=severity,
                source=subsystem,
                description=f"{subsystem} running {slowdown_ratio:.1f}x slower than baseline",
                consecutive_cycles=self._bottleneck_counters[counter_key],
                metrics={
                    "duration_ms": duration_ms,
                    "baseline_ms": baseline,
                    "slowdown_ratio": slowdown_ratio
                }
            ))

        return signals

    def _detect_resource_exhaustion(
        self,
        utilization: float,
        goal_count: int,
        waiting_goals: int
    ) -> Optional[BottleneckSignal]:
        """Detect goal resource exhaustion."""
        if utilization < self.resource_exhaustion_threshold:
            self._bottleneck_counters.pop("resource_exhaustion", None)
            return None

        severity = (utilization - self.resource_exhaustion_threshold) / (1.0 - self.resource_exhaustion_threshold)
        severity = min(1.0, severity)

        # Increase severity if goals are waiting
        if waiting_goals > 0:
            severity = min(1.0, severity + 0.2)

        counter_key = "resource_exhaustion"
        self._bottleneck_counters[counter_key] = self._bottleneck_counters.get(counter_key, 0) + 1

        return BottleneckSignal(
            bottleneck_type=BottleneckType.GOAL_RESOURCE_EXHAUSTION,
            severity=severity,
            source="goal_competition",
            description=f"Resource utilization at {utilization:.0%}, {waiting_goals} goals waiting",
            consecutive_cycles=self._bottleneck_counters[counter_key],
            metrics={
                "utilization": utilization,
                "active_goals": goal_count,
                "waiting_goals": waiting_goals
            }
        )

    def _detect_memory_lag(self, timings: Dict[str, float]) -> Optional[BottleneckSignal]:
        """Detect memory consolidation falling behind."""
        memory_time = timings.get("memory_consolidation", 0)

        if memory_time < self.memory_lag_threshold_ms:
            self._bottleneck_counters.pop("memory_lag", None)
            return None

        severity = min(1.0, (memory_time - self.memory_lag_threshold_ms) / self.memory_lag_threshold_ms)

        counter_key = "memory_lag"
        self._bottleneck_counters[counter_key] = self._bottleneck_counters.get(counter_key, 0) + 1

        return BottleneckSignal(
            bottleneck_type=BottleneckType.MEMORY_LAG,
            severity=severity,
            source="memory",
            description=f"Memory consolidation taking {memory_time:.0f}ms (threshold: {self.memory_lag_threshold_ms}ms)",
            consecutive_cycles=self._bottleneck_counters[counter_key],
            metrics={"duration_ms": memory_time, "threshold_ms": self.memory_lag_threshold_ms}
        )

    def _detect_cycle_overrun(self, timings: Dict[str, float]) -> Optional[BottleneckSignal]:
        """Detect cognitive cycle exceeding target duration."""
        total_time = sum(timings.values())

        if total_time < self.cycle_duration_target_ms:
            self._bottleneck_counters.pop("cycle_overrun", None)
            return None

        overrun_ratio = total_time / self.cycle_duration_target_ms
        severity = min(1.0, (overrun_ratio - 1.0) / 2.0)

        counter_key = "cycle_overrun"
        self._bottleneck_counters[counter_key] = self._bottleneck_counters.get(counter_key, 0) + 1

        return BottleneckSignal(
            bottleneck_type=BottleneckType.CYCLE_OVERRUN,
            severity=severity,
            source="cycle_executor",
            description=f"Cycle took {total_time:.0f}ms (target: {self.cycle_duration_target_ms}ms)",
            consecutive_cycles=self._bottleneck_counters[counter_key],
            metrics={
                "total_ms": total_time,
                "target_ms": self.cycle_duration_target_ms,
                "breakdown": timings
            }
        )

    def _compute_overall_load(
        self,
        percept_count: int,
        resource_utilization: float,
        timings: Dict[str, float]
    ) -> float:
        """Compute overall cognitive load factor (0.0 to 1.0)."""
        # Workspace load (0.0 to 1.0)
        workspace_load = min(1.0, percept_count / (self.workspace_overload_threshold * 1.5))

        # Resource load (already 0.0 to 1.0)
        resource_load = resource_utilization

        # Timing load (based on cycle overrun)
        total_time = sum(timings.values())
        timing_load = min(1.0, total_time / (self.cycle_duration_target_ms * 2))

        # Weighted combination (resources most important)
        overall = (
            workspace_load * 0.25 +
            resource_load * 0.5 +
            timing_load * 0.25
        )

        return min(1.0, overall)

    def _evaluate_bottleneck_persistence(self, bottlenecks: List[BottleneckSignal]) -> bool:
        """Evaluate if bottlenecks have persisted long enough."""
        if not bottlenecks:
            return False

        # Check if any bottleneck has persisted for threshold cycles
        for bottleneck in bottlenecks:
            if bottleneck.consecutive_cycles >= self.consecutive_cycles_threshold:
                return True

        return False

    def _generate_recommendation(
        self,
        bottlenecks: List[BottleneckSignal],
        overall_load: float
    ) -> str:
        """Generate recommended action based on bottleneck state."""
        if not bottlenecks:
            return "normal_operation"

        # Find most severe bottleneck
        most_severe = max(bottlenecks, key=lambda b: b.severity)

        # Recommendations based on bottleneck type
        if most_severe.bottleneck_type == BottleneckType.GOAL_RESOURCE_EXHAUSTION:
            if most_severe.severity > 0.7:
                return "pause_low_priority_goals"
            return "reduce_goal_parallelism"

        if most_severe.bottleneck_type == BottleneckType.WORKSPACE_OVERLOAD:
            return "increase_attention_selectivity"

        if most_severe.bottleneck_type == BottleneckType.MEMORY_LAG:
            return "defer_memory_consolidation"

        if most_severe.bottleneck_type == BottleneckType.CYCLE_OVERRUN:
            return "skip_optional_processing"

        if most_severe.bottleneck_type == BottleneckType.SUBSYSTEM_SLOWDOWN:
            return f"investigate_{most_severe.source}"

        # Default based on load level
        if overall_load > 0.8:
            return "reduce_processing_load"

        return "monitor_closely"

    def get_state(self) -> BottleneckState:
        """Get current bottleneck state."""
        return self._current_state

    def is_overloaded(self) -> bool:
        """Quick check if system is currently overloaded."""
        return self._current_state.is_bottlenecked

    def get_load(self) -> float:
        """Get current overall load factor."""
        return self._current_state.overall_load

    def get_average_load(self, cycles: int = 10) -> float:
        """Get average load over recent cycles."""
        if not self.load_history:
            return 0.0
        recent = list(self.load_history)[-cycles:]
        return sum(recent) / len(recent)

    def should_inhibit_communication(self) -> bool:
        """
        Check if communication should be inhibited due to bottleneck.

        Returns True if:
        - System is bottlenecked AND
        - Load is above 80% OR
        - Any bottleneck has severity > 0.7
        """
        if not self._current_state.is_bottlenecked:
            return False

        if self._current_state.overall_load > 0.8:
            return True

        return self._current_state.get_severity() > 0.7

    def get_introspection_text(self) -> Optional[str]:
        """
        Generate introspective text about current bottleneck state.

        Returns None if not bottlenecked, otherwise returns
        a first-person description of the overwhelm state.
        """
        if not self._current_state.is_bottlenecked:
            return None

        bottlenecks = self._current_state.active_bottlenecks
        if not bottlenecks:
            return None

        # Build introspective description
        parts = ["I notice I'm experiencing processing constraints:"]

        for bottleneck in bottlenecks:
            if bottleneck.bottleneck_type == BottleneckType.WORKSPACE_OVERLOAD:
                parts.append(f"- My attention is stretched thin across too many things")
            elif bottleneck.bottleneck_type == BottleneckType.GOAL_RESOURCE_EXHAUSTION:
                parts.append(f"- I have more goals than I can effectively pursue simultaneously")
            elif bottleneck.bottleneck_type == BottleneckType.MEMORY_LAG:
                parts.append(f"- I'm having trouble consolidating recent experiences")
            elif bottleneck.bottleneck_type == BottleneckType.CYCLE_OVERRUN:
                parts.append(f"- My thinking is taking longer than usual")
            elif bottleneck.bottleneck_type == BottleneckType.SUBSYSTEM_SLOWDOWN:
                parts.append(f"- Some of my cognitive processes are running slowly")

        load_pct = self._current_state.overall_load * 100
        parts.append(f"\nOverall cognitive load: {load_pct:.0f}%")

        if self._current_state.recommendation != "normal_operation":
            parts.append(f"Suggested adaptation: {self._current_state.recommendation.replace('_', ' ')}")

        return "\n".join(parts)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of bottleneck detector state."""
        return {
            "is_bottlenecked": self._current_state.is_bottlenecked,
            "overall_load": self._current_state.overall_load,
            "average_load": self.get_average_load(),
            "active_bottleneck_count": len(self._current_state.active_bottlenecks),
            "bottleneck_types": [
                b.bottleneck_type.value for b in self._current_state.active_bottlenecks
            ],
            "max_severity": self._current_state.get_severity(),
            "recommendation": self._current_state.recommendation,
            "should_inhibit_communication": self.should_inhibit_communication(),
            "baseline_timings": self._baseline_timings.copy()
        }
