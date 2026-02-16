"""
Interruption System - Urgent mid-turn communication capability.

Enables breaking turn-taking rhythm when urgency exceeds a threshold.
Produces interruption requests that override normal timing inhibitions,
allowing Sanctuary to speak during a human turn when something is
sufficiently important (safety, value conflicts, critical insights).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class InterruptionReason(Enum):
    """Why an interruption is warranted."""
    SAFETY = "safety"                      # Safety concern requiring immediate attention
    VALUE_CONFLICT = "value_conflict"      # Detected value conflict needing external check
    CRITICAL_INSIGHT = "critical_insight"  # High-salience introspective breakthrough
    EMOTIONAL_URGENCY = "emotional_urgency"  # Extreme emotional state requiring expression
    CORRECTION = "correction"              # Must correct dangerous misunderstanding


@dataclass
class InterruptionRequest:
    """
    A request to interrupt the current conversational turn.

    Attributes:
        reason: Why the interruption is warranted
        urgency: How urgent (0.0-1.0) — must exceed system threshold to fire
        content_hint: Brief description of what needs to be said
        created_at: When this request was generated
    """
    reason: InterruptionReason
    urgency: float
    content_hint: str
    created_at: datetime = field(default_factory=datetime.now)


class InterruptionSystem:
    """
    Evaluates whether the system should interrupt a human turn.

    The system is deliberately conservative: interruptions are rare and
    reserved for genuinely urgent situations. The threshold is high,
    and a cooldown prevents rapid-fire interruptions.

    Attributes:
        config: Configuration dictionary
        urgency_threshold: Minimum urgency to allow interruption (default: 0.85)
        cooldown_seconds: Minimum seconds between interruptions (default: 60)
        last_interruption_time: When the last interruption occurred
        interruption_count: Total interruptions made
        interruption_history: Recent interruption records
    """

    DEFAULT_URGENCY_THRESHOLD = 0.85
    DEFAULT_COOLDOWN_SECONDS = 60
    DEFAULT_MAX_HISTORY = 20

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize interruption system.

        Args:
            config: Optional configuration dict with keys:
                - urgency_threshold: Min urgency for interruption (default: 0.85)
                - cooldown_seconds: Min seconds between interruptions (default: 60)
                - max_history: Maximum history entries to keep (default: 20)
        """
        config = config or {}
        self.urgency_threshold = max(0.5, min(1.0, config.get(
            "urgency_threshold", self.DEFAULT_URGENCY_THRESHOLD
        )))
        self.cooldown_seconds = max(10, config.get(
            "cooldown_seconds", self.DEFAULT_COOLDOWN_SECONDS
        ))
        self.max_history = max(1, config.get(
            "max_history", self.DEFAULT_MAX_HISTORY
        ))

        self.last_interruption_time: Optional[datetime] = None
        self.interruption_count: int = 0
        self.interruption_history: List[Dict[str, Any]] = []

        logger.debug(
            f"InterruptionSystem initialized: threshold={self.urgency_threshold:.2f}, "
            f"cooldown={self.cooldown_seconds}s"
        )

    def evaluate(
        self,
        workspace_state: Any,
        emotional_state: Dict[str, float],
        active_urges: List[Any],
        is_human_speaking: bool
    ) -> Optional[InterruptionRequest]:
        """
        Evaluate whether an interruption is warranted.

        Only produces a request when:
        1. The human is currently speaking
        2. Cooldown has elapsed since last interruption
        3. A trigger condition is detected with urgency above threshold

        Args:
            workspace_state: Current workspace snapshot
            emotional_state: Current VAD emotional state
            active_urges: Active communication urges
            is_human_speaking: Whether the human is currently mid-turn

        Returns:
            InterruptionRequest if warranted, None otherwise
        """
        if not is_human_speaking:
            return None

        if self._is_on_cooldown():
            return None

        # Check triggers in priority order
        request = (
            self._check_safety_trigger(workspace_state)
            or self._check_value_conflict_trigger(workspace_state)
            or self._check_critical_insight_trigger(workspace_state)
            or self._check_emotional_urgency_trigger(emotional_state)
            or self._check_correction_trigger(workspace_state, active_urges)
        )

        if request and request.urgency >= self.urgency_threshold:
            return request

        return None

    def record_interruption(self, request: InterruptionRequest) -> None:
        """
        Record that an interruption was executed.

        Args:
            request: The interruption request that was acted on
        """
        self.last_interruption_time = datetime.now()
        self.interruption_count += 1
        self.interruption_history.append({
            "timestamp": datetime.now(),
            "reason": request.reason.value,
            "urgency": request.urgency,
            "content_hint": request.content_hint
        })

        # Limit history
        if len(self.interruption_history) > self.max_history:
            self.interruption_history = self.interruption_history[-self.max_history:]

        logger.info(
            f"Interruption recorded: reason={request.reason.value}, "
            f"urgency={request.urgency:.2f}, total={self.interruption_count}"
        )

    def _is_on_cooldown(self) -> bool:
        """Check if cooldown period has not elapsed."""
        if self.last_interruption_time is None:
            return False
        elapsed = (datetime.now() - self.last_interruption_time).total_seconds()
        return elapsed < self.cooldown_seconds

    def _check_safety_trigger(self, workspace_state: Any) -> Optional[InterruptionRequest]:
        """Check for safety-related percepts that warrant interruption."""
        if not hasattr(workspace_state, 'percepts'):
            return None

        for percept in workspace_state.percepts.values():
            metadata = getattr(percept, 'metadata', {})
            if not isinstance(metadata, dict):
                continue

            if metadata.get("safety_concern") or metadata.get("type") == "safety_alert":
                return InterruptionRequest(
                    reason=InterruptionReason.SAFETY,
                    urgency=0.95,
                    content_hint="Safety concern detected"
                )
        return None

    def _check_value_conflict_trigger(self, workspace_state: Any) -> Optional[InterruptionRequest]:
        """Check for active value conflicts requiring immediate attention."""
        if not hasattr(workspace_state, 'percepts'):
            return None

        for percept in workspace_state.percepts.values():
            if getattr(percept, 'modality', '') != 'introspection':
                continue
            raw = getattr(percept, 'raw', {})
            if isinstance(raw, dict) and raw.get("type") == "value_conflict":
                severity = raw.get("severity", 0.5)
                if severity > 0.8:
                    return InterruptionRequest(
                        reason=InterruptionReason.VALUE_CONFLICT,
                        urgency=0.90,
                        content_hint="Significant value conflict detected"
                    )
        return None

    def _check_critical_insight_trigger(self, workspace_state: Any) -> Optional[InterruptionRequest]:
        """Check for breakthrough insights that cannot wait."""
        if not hasattr(workspace_state, 'percepts'):
            return None

        for percept in workspace_state.percepts.values():
            if getattr(percept, 'modality', '') != 'introspection':
                continue
            salience = getattr(percept, 'salience', 0)
            complexity = getattr(percept, 'complexity', 0)
            if salience > 0.9 and complexity > 20:
                return InterruptionRequest(
                    reason=InterruptionReason.CRITICAL_INSIGHT,
                    urgency=0.87,
                    content_hint="Critical introspective insight"
                )
        return None

    def _check_emotional_urgency_trigger(
        self, emotional_state: Dict[str, float]
    ) -> Optional[InterruptionRequest]:
        """Check for extreme emotional states requiring expression."""
        arousal = emotional_state.get("arousal", 0.0)
        valence = emotional_state.get("valence", 0.0)

        # Only interrupt for extreme distress (high arousal + strongly negative valence)
        if arousal > 0.9 and valence < -0.7:
            return InterruptionRequest(
                reason=InterruptionReason.EMOTIONAL_URGENCY,
                urgency=0.88,
                content_hint="Extreme emotional distress"
            )
        return None

    def _check_correction_trigger(
        self, workspace_state: Any, active_urges: List[Any]
    ) -> Optional[InterruptionRequest]:
        """Check for correction urges that are critically urgent."""
        for urge in active_urges:
            drive_type = getattr(urge, 'drive_type', None)
            if drive_type is None:
                continue
            drive_value = drive_type.value if hasattr(drive_type, 'value') else str(drive_type)
            if drive_value == "correction" and getattr(urge, 'intensity', 0) > 0.9:
                return InterruptionRequest(
                    reason=InterruptionReason.CORRECTION,
                    urgency=0.86,
                    content_hint=getattr(urge, 'content', "Critical correction needed")
                )
        return None

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of interruption system state."""
        return {
            "interruption_count": self.interruption_count,
            "last_interruption": self.last_interruption_time,
            "on_cooldown": self._is_on_cooldown(),
            "urgency_threshold": self.urgency_threshold,
            "cooldown_seconds": self.cooldown_seconds,
            "recent_interruptions": self.interruption_history[-5:]
        }
