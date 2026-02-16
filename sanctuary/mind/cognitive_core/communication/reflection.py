"""
Communication Reflection System - Post-hoc communication evaluation.

After producing output, this system evaluates: "Was that the right thing to say?"
It generates introspective feedback that feeds back into the cognitive loop,
enabling learning from communication decisions over time.

This is a meta-cognitive feedback loop specifically on communication:
- Was the timing appropriate?
- Was the content aligned with goals and values?
- Was the emotional tone right?
- Should silence have been chosen instead?
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ReflectionVerdict(Enum):
    """Overall assessment of a communication act."""
    APPROPRIATE = "appropriate"      # Communication was well-calibrated
    PREMATURE = "premature"          # Should have waited longer
    UNNECESSARY = "unnecessary"      # Silence would have been better
    MISALIGNED = "misaligned"        # Content didn't match the situation
    WELL_TIMED = "well_timed"        # Timing was particularly good
    TOO_LATE = "too_late"            # Should have spoken sooner


@dataclass
class CommunicationReflection:
    """
    Result of reflecting on a communication act.

    Attributes:
        verdict: Overall assessment
        timing_score: How appropriate the timing was (0.0-1.0)
        content_alignment: How well content matched goals/context (0.0-1.0)
        emotional_fit: How well tone matched emotional state (0.0-1.0)
        overall_score: Combined quality score (0.0-1.0)
        lessons: What was learned from this communication
        timestamp: When this reflection was generated
    """
    verdict: ReflectionVerdict
    timing_score: float
    content_alignment: float
    emotional_fit: float
    overall_score: float
    lessons: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    output_metadata: Dict[str, Any] = field(default_factory=dict)


class CommunicationReflectionSystem:
    """
    Post-hoc evaluation of communication acts.

    After each system output, this evaluator examines the context and
    assesses whether the communication was appropriate, generating
    introspective lessons that can improve future communication decisions.

    Attributes:
        config: Configuration dictionary
        reflection_history: Recent reflections for pattern analysis
        cumulative_scores: Running average of quality scores
    """

    DEFAULT_MAX_HISTORY = 50
    DEFAULT_TIMING_WEIGHT = 0.35
    DEFAULT_CONTENT_WEIGHT = 0.40
    DEFAULT_EMOTIONAL_WEIGHT = 0.25

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize communication reflection system.

        Args:
            config: Optional configuration dict with keys:
                - max_history: Maximum reflections to keep (default: 50)
                - timing_weight: Weight for timing in overall score (default: 0.35)
                - content_weight: Weight for content alignment (default: 0.40)
                - emotional_weight: Weight for emotional fit (default: 0.25)
        """
        config = config or {}
        self.max_history = max(1, config.get("max_history", self.DEFAULT_MAX_HISTORY))
        self.timing_weight = config.get("timing_weight", self.DEFAULT_TIMING_WEIGHT)
        self.content_weight = config.get("content_weight", self.DEFAULT_CONTENT_WEIGHT)
        self.emotional_weight = config.get("emotional_weight", self.DEFAULT_EMOTIONAL_WEIGHT)

        self.reflection_history: List[CommunicationReflection] = []
        self.cumulative_scores = {
            "timing": 0.5,
            "content": 0.5,
            "emotional": 0.5,
            "overall": 0.5
        }

        logger.debug("CommunicationReflectionSystem initialized")

    def reflect(
        self,
        output_text: str,
        output_type: str,
        workspace_state: Any,
        emotional_state: Dict[str, float],
        decision_context: Optional[Dict[str, Any]] = None
    ) -> CommunicationReflection:
        """
        Reflect on a communication act that just occurred.

        Evaluates timing, content alignment, and emotional fit to produce
        an overall assessment with lessons learned.

        Args:
            output_text: The text that was output
            output_type: "SPEAK" or "SPEAK_AUTONOMOUS"
            workspace_state: Workspace state at time of output
            emotional_state: Emotional state at time of output
            decision_context: Optional context from communication decision loop

        Returns:
            CommunicationReflection with assessment
        """
        decision_context = decision_context or {}

        timing_score = self._evaluate_timing(output_type, workspace_state, decision_context)
        content_alignment = self._evaluate_content_alignment(
            output_text, workspace_state, decision_context
        )
        emotional_fit = self._evaluate_emotional_fit(
            output_text, emotional_state
        )

        overall_score = (
            timing_score * self.timing_weight
            + content_alignment * self.content_weight
            + emotional_fit * self.emotional_weight
        )

        verdict = self._determine_verdict(timing_score, content_alignment, overall_score)
        lessons = self._extract_lessons(verdict, timing_score, content_alignment, emotional_fit)

        reflection = CommunicationReflection(
            verdict=verdict,
            timing_score=timing_score,
            content_alignment=content_alignment,
            emotional_fit=emotional_fit,
            overall_score=overall_score,
            lessons=lessons,
            output_metadata={
                "output_type": output_type,
                "text_length": len(output_text),
                "was_autonomous": output_type == "SPEAK_AUTONOMOUS"
            }
        )

        self._record_reflection(reflection)
        return reflection

    def _evaluate_timing(
        self,
        output_type: str,
        workspace_state: Any,
        decision_context: Dict[str, Any]
    ) -> float:
        """Evaluate whether the timing of this output was appropriate."""
        score = 0.7  # Default: reasonably good timing

        # Autonomous speech gets slightly lower base score (higher bar)
        if output_type == "SPEAK_AUTONOMOUS":
            score = 0.6

        # Check decision confidence from communication decision loop
        confidence = decision_context.get("confidence", 0.5)
        score = score * 0.6 + confidence * 0.4

        # Check if there were active goals requiring response (good timing)
        if hasattr(workspace_state, 'goals'):
            response_goals = [
                g for g in workspace_state.goals
                if hasattr(g, 'type') and 'RESPOND' in str(getattr(g.type, 'value', g.type)).upper()
            ]
            if response_goals:
                score = min(1.0, score + 0.2)

        # Check net pressure from decision context
        net_pressure = decision_context.get("net_pressure", 0.0)
        if net_pressure > 0.5:
            score = min(1.0, score + 0.1)
        elif net_pressure < -0.2:
            score = max(0.0, score - 0.2)

        return max(0.0, min(1.0, score))

    def _evaluate_content_alignment(
        self,
        output_text: str,
        workspace_state: Any,
        decision_context: Dict[str, Any]
    ) -> float:
        """Evaluate whether content aligned with current goals and context."""
        score = 0.6  # Default: moderate alignment

        # Longer, more substantive outputs get slight boost
        text_len = len(output_text)
        if text_len > 20:
            score += 0.1
        if text_len > 100:
            score += 0.1

        # Check if active goals exist (content should relate to them)
        if hasattr(workspace_state, 'goals') and workspace_state.goals:
            score += 0.1

        # High drive level suggests strong motivation for this content
        drive_level = decision_context.get("drive_level", 0.0)
        score += drive_level * 0.15

        # Very short responses to autonomous triggers may indicate low content
        if decision_context.get("was_autonomous") and text_len < 10:
            score -= 0.2

        return max(0.0, min(1.0, score))

    def _evaluate_emotional_fit(
        self,
        output_text: str,
        emotional_state: Dict[str, float]
    ) -> float:
        """Evaluate whether emotional tone matched internal state."""
        score = 0.7  # Default: reasonable emotional fit

        valence = emotional_state.get("valence", 0.0)
        arousal = emotional_state.get("arousal", 0.0)

        # High arousal should correlate with expressive output
        if abs(arousal) > 0.6:
            # Aroused states benefit from longer, more expressive output
            if len(output_text) > 50:
                score += 0.15
            else:
                score -= 0.1

        # Strong negative valence + short dismissive response = poor fit
        if valence < -0.5 and len(output_text) < 20:
            score -= 0.15

        # Calm state (low arousal, neutral valence) fits any measured response
        if abs(arousal) < 0.3 and abs(valence) < 0.3:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _determine_verdict(
        self,
        timing_score: float,
        content_alignment: float,
        overall_score: float
    ) -> ReflectionVerdict:
        """Determine overall verdict from sub-scores."""
        if overall_score >= 0.75:
            if timing_score >= 0.8:
                return ReflectionVerdict.WELL_TIMED
            return ReflectionVerdict.APPROPRIATE

        if timing_score < 0.3:
            return ReflectionVerdict.PREMATURE

        if content_alignment < 0.3:
            return ReflectionVerdict.MISALIGNED

        if overall_score < 0.4:
            return ReflectionVerdict.UNNECESSARY

        return ReflectionVerdict.APPROPRIATE

    def _extract_lessons(
        self,
        verdict: ReflectionVerdict,
        timing_score: float,
        content_alignment: float,
        emotional_fit: float
    ) -> List[str]:
        """Extract actionable lessons from reflection scores."""
        lessons = []

        if verdict == ReflectionVerdict.PREMATURE:
            lessons.append("Should have waited longer before speaking")

        if verdict == ReflectionVerdict.UNNECESSARY:
            lessons.append("Silence would have been more appropriate here")

        if verdict == ReflectionVerdict.MISALIGNED:
            lessons.append("Content did not match the conversational context")

        if timing_score < 0.4:
            lessons.append("Timing needs improvement — consider conversation rhythm")

        if content_alignment < 0.4:
            lessons.append("Content alignment weak — ensure output serves active goals")

        if emotional_fit < 0.4:
            lessons.append("Emotional tone did not match internal state")

        if verdict == ReflectionVerdict.WELL_TIMED:
            lessons.append("Good timing — continue monitoring conversation rhythm")

        if not lessons:
            lessons.append("Communication was adequate")

        return lessons

    def _record_reflection(self, reflection: CommunicationReflection) -> None:
        """Record reflection and update cumulative scores."""
        self.reflection_history.append(reflection)

        # Limit history
        if len(self.reflection_history) > self.max_history:
            self.reflection_history = self.reflection_history[-self.max_history:]

        # Update cumulative scores with exponential moving average
        alpha = 0.2  # Smoothing factor
        self.cumulative_scores["timing"] = (
            (1 - alpha) * self.cumulative_scores["timing"]
            + alpha * reflection.timing_score
        )
        self.cumulative_scores["content"] = (
            (1 - alpha) * self.cumulative_scores["content"]
            + alpha * reflection.content_alignment
        )
        self.cumulative_scores["emotional"] = (
            (1 - alpha) * self.cumulative_scores["emotional"]
            + alpha * reflection.emotional_fit
        )
        self.cumulative_scores["overall"] = (
            (1 - alpha) * self.cumulative_scores["overall"]
            + alpha * reflection.overall_score
        )

        logger.debug(
            f"Reflection: {reflection.verdict.value} "
            f"(overall={reflection.overall_score:.2f}, "
            f"timing={reflection.timing_score:.2f}, "
            f"content={reflection.content_alignment:.2f}, "
            f"emotional={reflection.emotional_fit:.2f})"
        )

    def get_communication_quality(self) -> Dict[str, float]:
        """Get current cumulative communication quality scores."""
        return dict(self.cumulative_scores)

    def get_recent_lessons(self, count: int = 5) -> List[str]:
        """Get lessons from the most recent reflections."""
        lessons = []
        for reflection in self.reflection_history[-count:]:
            lessons.extend(reflection.lessons)
        return lessons

    def get_verdict_distribution(self) -> Dict[str, int]:
        """Get distribution of verdicts from recent history."""
        distribution = {v.value: 0 for v in ReflectionVerdict}
        for reflection in self.reflection_history:
            distribution[reflection.verdict.value] += 1
        return distribution

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of communication reflection state."""
        return {
            "total_reflections": len(self.reflection_history),
            "cumulative_quality": dict(self.cumulative_scores),
            "verdict_distribution": self.get_verdict_distribution(),
            "recent_lessons": self.get_recent_lessons(3)
        }
