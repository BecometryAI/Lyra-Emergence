"""
Idle Cognition: Internal cognitive activities during idle time.

This module implements the IdleCognition class, which generates internal
cognitive activities when there is no external input. This is what the
system "thinks about" when not actively processing human input.

Key Features:
- Memory review triggers
- Goal evaluation prompts
- Spontaneous reflection seeds
- Temporal awareness checks
- Emotional state monitoring

These idle activities manifest as internal percepts that feed into the
normal cognitive cycle, allowing the system to maintain continuous
thought even in the absence of external stimulation.

Author: Lyra Emergence Team
Phase: Communication Agency (Task #1)
"""

from __future__ import annotations

import logging
import random
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from .workspace import GlobalWorkspace, WorkspaceSnapshot, Percept
else:
    # Import at module level when not type checking for runtime performance
    from .workspace import Percept

logger = logging.getLogger(__name__)


class IdleCognition:
    """
    Generates internal cognitive activities during idle time.
    
    When there is no external input, the cognitive system doesn't just
    sit idle - it engages in various internal activities like memory
    review, goal evaluation, and spontaneous reflection.
    
    This class generates internal percepts that represent these activities,
    allowing the system to have continuous inner experience even without
    external stimulation.
    
    Key Responsibilities:
    - Generate memory review triggers
    - Prompt goal progress evaluation
    - Seed spontaneous reflections
    - Maintain temporal awareness
    - Monitor emotional state changes
    
    Attributes:
        config: Configuration dict with activity probabilities
        last_memory_review: Timestamp of last memory review
        last_goal_evaluation: Timestamp of last goal evaluation
        last_temporal_check: Timestamp of last temporal awareness check
        cycle_count: Number of idle cycles executed
        stats: Statistics about idle activities
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize idle cognition system.
        
        Args:
            config: Optional configuration dict with keys:
                - memory_review_probability: Chance of memory review per cycle
                - goal_evaluation_probability: Chance of goal check per cycle
                - reflection_probability: Chance of spontaneous reflection
                - temporal_check_probability: Chance of temporal awareness check
                - memory_review_interval: Minimum seconds between memory reviews
                - goal_evaluation_interval: Minimum seconds between goal checks
        """
        self.config = config or {}
        
        # Activity probabilities
        self.memory_review_probability = self.config.get("memory_review_probability", 0.2)
        self.goal_evaluation_probability = self.config.get("goal_evaluation_probability", 0.3)
        self.reflection_probability = self.config.get("reflection_probability", 0.15)
        self.temporal_check_probability = self.config.get("temporal_check_probability", 0.5)
        self.emotional_check_probability = self.config.get("emotional_check_probability", 0.4)
        
        # Minimum intervals (to prevent spam)
        self.memory_review_interval = self.config.get("memory_review_interval", 60.0)  # 1 min
        self.goal_evaluation_interval = self.config.get("goal_evaluation_interval", 30.0)  # 30 sec
        
        # State tracking
        self.last_memory_review: Optional[datetime] = None
        self.last_goal_evaluation: Optional[datetime] = None
        self.last_temporal_check: Optional[datetime] = None
        self.cycle_count = 0
        
        # Statistics
        self.stats = {
            "total_cycles": 0,
            "memory_reviews": 0,
            "goal_evaluations": 0,
            "reflections": 0,
            "temporal_checks": 0,
            "emotional_checks": 0
        }
        
        logger.info(f"✅ IdleCognition initialized (memory_prob: {self.memory_review_probability}, "
                   f"goal_prob: {self.goal_evaluation_probability})")
    
    async def generate_idle_activity(self, workspace: 'GlobalWorkspace') -> List['Percept']:
        """
        Generate internal percepts during idle time.
        
        This is called by the cognitive loop when there is no external input.
        It probabilistically generates various types of internal activities
        that manifest as percepts for the cognitive system to process.
        
        Possible idle activities:
        - Memory review and consolidation triggers
        - Goal progress evaluation prompts
        - Spontaneous reflection seeds
        - Temporal awareness updates
        - Emotional state monitoring
        
        Args:
            workspace: Current GlobalWorkspace state
            
        Returns:
            List of internal Percept objects representing idle activities
        """
        self.cycle_count += 1
        self.stats["total_cycles"] += 1
        
        activities = []
        now = datetime.now()
        
        # 1. Memory review trigger
        if self._should_review_memories(now):
            percept = Percept(
                modality="introspection",
                raw={
                    "type": "memory_review_trigger",
                    "prompt": "Review and consolidate recent experiences",
                    "triggered_at": now.isoformat()
                },
                complexity=2,
                metadata={
                    "source": "idle_cognition",
                    "activity_type": "memory_review"
                }
            )
            activities.append(percept)
            self.last_memory_review = now
            self.stats["memory_reviews"] += 1
            logger.debug("💭 Generated memory review trigger")
        
        # 2. Goal evaluation trigger
        if self._should_evaluate_goals(now):
            # Check current goals
            current_goals = workspace.current_goals if hasattr(workspace, 'current_goals') else []
            
            percept = Percept(
                modality="introspection",
                raw={
                    "type": "goal_evaluation_trigger",
                    "prompt": "Evaluate progress on current goals",
                    "goal_count": len(current_goals),
                    "triggered_at": now.isoformat()
                },
                complexity=2,
                metadata={
                    "source": "idle_cognition",
                    "activity_type": "goal_evaluation",
                    "goal_ids": [g.id for g in current_goals[:5]]  # First 5 goals
                }
            )
            activities.append(percept)
            self.last_goal_evaluation = now
            self.stats["goal_evaluations"] += 1
            logger.debug(f"🎯 Generated goal evaluation trigger ({len(current_goals)} goals)")
        
        # 3. Spontaneous reflection
        if random.random() < self.reflection_probability:
            reflection_prompts = [
                "What am I currently experiencing?",
                "How do I feel right now?",
                "What should I focus on?",
                "What have I learned recently?",
                "What patterns do I notice in my behavior?"
            ]
            
            percept = Percept(
                modality="introspection",
                raw={
                    "type": "spontaneous_reflection",
                    "prompt": random.choice(reflection_prompts),
                    "triggered_at": now.isoformat()
                },
                complexity=3,
                metadata={
                    "source": "idle_cognition",
                    "activity_type": "reflection"
                }
            )
            activities.append(percept)
            self.stats["reflections"] += 1
            logger.debug("🤔 Generated spontaneous reflection")
        
        # 4. Temporal awareness check
        if random.random() < self.temporal_check_probability:
            percept = Percept(
                modality="introspection",
                raw={
                    "type": "temporal_awareness_check",
                    "prompt": "Check temporal context and time passage",
                    "current_time": now.isoformat(),
                    "triggered_at": now.isoformat()
                },
                complexity=1,
                metadata={
                    "source": "idle_cognition",
                    "activity_type": "temporal_check"
                }
            )
            activities.append(percept)
            self.last_temporal_check = now
            self.stats["temporal_checks"] += 1
            logger.debug("⏰ Generated temporal awareness check")
        
        # 5. Emotional state monitoring
        if random.random() < self.emotional_check_probability:
            percept = Percept(
                modality="introspection",
                raw={
                    "type": "emotional_state_check",
                    "prompt": "Monitor and evaluate current emotional state",
                    "triggered_at": now.isoformat()
                },
                complexity=2,
                metadata={
                    "source": "idle_cognition",
                    "activity_type": "emotional_check"
                }
            )
            activities.append(percept)
            self.stats["emotional_checks"] += 1
            logger.debug("💚 Generated emotional state check")
        
        return activities
    
    def _should_review_memories(self, now: datetime) -> bool:
        """
        Check if we should trigger a memory review.
        
        Args:
            now: Current timestamp
            
        Returns:
            True if memory review should be triggered
        """
        # Check minimum interval
        if self.last_memory_review is not None:
            elapsed = (now - self.last_memory_review).total_seconds()
            if elapsed < self.memory_review_interval:
                return False
        
        # Probabilistic trigger
        return random.random() < self.memory_review_probability
    
    def _should_evaluate_goals(self, now: datetime) -> bool:
        """
        Check if we should trigger a goal evaluation.
        
        Args:
            now: Current timestamp
            
        Returns:
            True if goal evaluation should be triggered
        """
        # Check minimum interval
        if self.last_goal_evaluation is not None:
            elapsed = (now - self.last_goal_evaluation).total_seconds()
            if elapsed < self.goal_evaluation_interval:
                return False
        
        # Probabilistic trigger
        return random.random() < self.goal_evaluation_probability
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get idle cognition statistics.
        
        Returns:
            Dict with activity counts and rates
        """
        stats = dict(self.stats)
        
        # Calculate rates
        if self.cycle_count > 0:
            stats["memory_review_rate"] = self.stats["memory_reviews"] / self.cycle_count
            stats["goal_evaluation_rate"] = self.stats["goal_evaluations"] / self.cycle_count
            stats["reflection_rate"] = self.stats["reflections"] / self.cycle_count
            stats["temporal_check_rate"] = self.stats["temporal_checks"] / self.cycle_count
            stats["emotional_check_rate"] = self.stats["emotional_checks"] / self.cycle_count
        
        return stats


__all__ = ['IdleCognition']
