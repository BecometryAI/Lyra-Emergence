"""
Emotional Modulation: Making emotions functionally efficacious.

This module implements functional emotional modulation where PAD (Pleasure-Arousal-Dominance)
values directly modulate processing parameters BEFORE LLM invocation. This ensures emotions
are causal forces that shape computation, not merely descriptive labels.

From a functionalist perspective: if emotions don't cause measurable changes to processing
before the LLM is invoked, they're not functionally real emotions.

Key Principles:
1. Arousal modulates processing speed and thoroughness (fight/flight vs deliberation)
2. Valence creates approach/avoidance biases in action selection
3. Dominance modulates decision confidence thresholds (assertiveness)
4. All modulation happens BEFORE cognitive processing, not as context to LLM
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ProcessingParams:
    """
    Processing parameters modulated by emotional state.
    
    These parameters directly affect cognitive processing before any LLM invocation,
    making emotions functionally efficacious rather than merely descriptive.
    
    Attributes:
        attention_iterations: Number of competitive attention cycles (arousal-modulated)
        ignition_threshold: Threshold for global workspace broadcast (arousal-modulated)
        memory_retrieval_limit: Max memories to retrieve (arousal-modulated)
        processing_timeout: Time budget for processing (arousal-modulated)
        decision_threshold: Confidence needed to act (dominance-modulated)
        action_bias_strength: Strength of valence-based action biasing (valence-modulated)
    """
    attention_iterations: int = 7
    ignition_threshold: float = 0.5
    memory_retrieval_limit: int = 3
    processing_timeout: float = 1.5
    decision_threshold: float = 0.7
    action_bias_strength: float = 0.0
    
    # Metadata for tracking
    arousal_level: float = 0.0
    valence_level: float = 0.0
    dominance_level: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/metrics."""
        return {
            'attention_iterations': self.attention_iterations,
            'ignition_threshold': self.ignition_threshold,
            'memory_retrieval_limit': self.memory_retrieval_limit,
            'processing_timeout': self.processing_timeout,
            'decision_threshold': self.decision_threshold,
            'action_bias_strength': self.action_bias_strength,
            'arousal_level': self.arousal_level,
            'valence_level': self.valence_level,
            'dominance_level': self.dominance_level,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ModulationMetrics:
    """
    Metrics for tracking emotional modulation effects.
    
    These metrics verify that emotions are actually modulating processing,
    providing evidence that emotions are functionally real.
    """
    total_modulations: int = 0
    
    # Arousal effects
    high_arousal_fast_processing: int = 0
    low_arousal_slow_processing: int = 0
    arousal_attention_correlations: List[tuple] = field(default_factory=list)
    
    # Valence effects
    positive_valence_approach_bias: int = 0
    negative_valence_avoidance_bias: int = 0
    valence_action_correlations: List[tuple] = field(default_factory=list)
    
    # Dominance effects
    high_dominance_assertive: int = 0
    low_dominance_cautious: int = 0
    dominance_threshold_correlations: List[tuple] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            'total_modulations': self.total_modulations,
            'arousal_effects': {
                'high_arousal_fast': self.high_arousal_fast_processing,
                'low_arousal_slow': self.low_arousal_slow_processing,
                'correlations_count': len(self.arousal_attention_correlations)
            },
            'valence_effects': {
                'positive_approach': self.positive_valence_approach_bias,
                'negative_avoidance': self.negative_valence_avoidance_bias,
                'correlations_count': len(self.valence_action_correlations)
            },
            'dominance_effects': {
                'high_assertive': self.high_dominance_assertive,
                'low_cautious': self.low_dominance_cautious,
                'correlations_count': len(self.dominance_threshold_correlations)
            }
        }


class EmotionalModulation:
    """
    Implements functional emotional modulation of cognitive processing.
    
    Makes emotions causally efficacious by directly modulating processing parameters
    BEFORE any LLM invocation. This ensures emotions are real forces that shape
    computation, not merely descriptive context passed to the LLM.
    
    Arousal Effects (Processing Speed/Thoroughness):
    - High arousal (0.7-1.0): Faster, less thorough (fight/flight)
      * Fewer attention iterations (snap decisions)
      * Lower ignition threshold (react to more stimuli)
      * Shorter memory retrieval (less deliberation)
      * Faster timeout (quick response)
    
    - Low arousal (0.0-0.3): Slower, more deliberate
      * More attention iterations (careful analysis)
      * Higher ignition threshold (selective)
      * More memory retrieval (thorough consideration)
      * Longer timeout (take time to think)
    
    Valence Effects (Approach/Avoidance):
    - Positive valence (0.3-1.0): Approach bias
      * Boost priority of engage, explore, create, connect actions
      * Reduce priority of withdraw, defend, avoid, reject actions
    
    - Negative valence (-1.0 to -0.3): Avoidance bias
      * Reduce priority of approach actions
      * Boost priority of defensive/avoidance actions
    
    Dominance Effects (Confidence/Assertiveness):
    - High dominance (0.7-1.0): Lower confidence threshold
      * More assertive (act with less certainty)
      * Lower decision threshold
    
    - Low dominance (0.0-0.3): Higher confidence threshold
      * More cautious (need more certainty to act)
      * Higher decision threshold
    
    Attributes:
        enabled: Whether modulation is active (for ablation testing)
        metrics: Tracking metrics for verifying functional effects
        baseline_params: Default processing parameters
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize emotional modulation system.
        
        Args:
            enabled: Whether modulation is active (False for ablation testing)
        """
        self.enabled = enabled
        self.metrics = ModulationMetrics()
        
        # Baseline processing parameters (neutral emotional state)
        self.baseline_params = ProcessingParams(
            attention_iterations=7,
            ignition_threshold=0.5,
            memory_retrieval_limit=3,
            processing_timeout=1.5,
            decision_threshold=0.7,
            action_bias_strength=0.0
        )
        
        logger.info(f"EmotionalModulation initialized (enabled={enabled})")
    
    def modulate_processing(
        self,
        arousal: float,
        valence: float,
        dominance: float
    ) -> ProcessingParams:
        """
        Modulate processing parameters based on emotional state.
        
        This is the core method that makes emotions functionally efficacious.
        It directly affects cognitive parameters BEFORE any LLM processing.
        
        Args:
            arousal: Emotional arousal level (-1.0 to 1.0, typically 0.0 to 1.0)
            valence: Emotional valence (-1.0 to 1.0)
            dominance: Sense of control/dominance (0.0 to 1.0)
        
        Returns:
            ProcessingParams with emotionally-modulated values
        """
        if not self.enabled:
            # Return baseline parameters (for ablation testing)
            return self.baseline_params
        
        # Ensure arousal is in [0, 1] range (some systems use [-1, 1])
        arousal_normalized = max(0.0, min(1.0, arousal))
        
        # Apply arousal modulation to processing speed/thoroughness
        params = self._modulate_arousal(arousal_normalized)
        
        # Apply dominance modulation to decision threshold
        params = self._modulate_dominance(dominance, params)
        
        # Store emotional levels for metrics
        params.arousal_level = arousal_normalized
        params.valence_level = valence
        params.dominance_level = dominance
        params.timestamp = datetime.now()
        
        # Update metrics
        self._update_metrics(arousal_normalized, valence, dominance, params)
        
        logger.debug(
            f"Emotional modulation: A={arousal_normalized:.2f} V={valence:.2f} D={dominance:.2f} "
            f"→ iters={params.attention_iterations}, thresh={params.ignition_threshold:.2f}, "
            f"decision={params.decision_threshold:.2f}"
        )
        
        return params
    
    def _modulate_arousal(self, arousal: float) -> ProcessingParams:
        """
        Modulate processing parameters based on arousal.
        
        High arousal = faster, less thorough (fight/flight)
        Low arousal = slower, more deliberate
        
        Args:
            arousal: Arousal level (0.0-1.0)
        
        Returns:
            ProcessingParams with arousal modulation
        """
        # Attention iterations: 5-10 range (inverse with arousal)
        # High arousal → fewer iterations (snap decisions)
        # Low arousal → more iterations (careful analysis)
        attention_iterations = int(10 - (arousal * 5))
        attention_iterations = max(5, min(10, attention_iterations))
        
        # Ignition threshold: 0.4-0.6 range (inverse with arousal)
        # High arousal → lower threshold (react to more stimuli)
        # Low arousal → higher threshold (more selective)
        ignition_threshold = 0.6 - (arousal * 0.2)
        ignition_threshold = max(0.4, min(0.6, ignition_threshold))
        
        # Memory retrieval limit: 2-5 range (inverse with arousal)
        # High arousal → fewer memories (less deliberation)
        # Low arousal → more memories (thorough consideration)
        memory_retrieval_limit = int(5 - (arousal * 3))
        memory_retrieval_limit = max(2, min(5, memory_retrieval_limit))
        
        # Processing timeout: 1.0-2.0 seconds (inverse with arousal)
        # High arousal → shorter timeout (quick response)
        # Low arousal → longer timeout (take time to think)
        processing_timeout = 2.0 - (arousal * 1.0)
        processing_timeout = max(1.0, min(2.0, processing_timeout))
        
        return ProcessingParams(
            attention_iterations=attention_iterations,
            ignition_threshold=ignition_threshold,
            memory_retrieval_limit=memory_retrieval_limit,
            processing_timeout=processing_timeout,
            decision_threshold=self.baseline_params.decision_threshold,
            action_bias_strength=0.0
        )
    
    def _modulate_dominance(
        self,
        dominance: float,
        params: ProcessingParams
    ) -> ProcessingParams:
        """
        Modulate decision threshold based on dominance.
        
        High dominance = lower confidence threshold (more assertive)
        Low dominance = higher confidence threshold (more cautious)
        
        Args:
            dominance: Dominance level (0.0-1.0)
            params: ProcessingParams to modify
        
        Returns:
            Modified ProcessingParams
        """
        # Decision threshold: 0.5-0.7 range (inverse with dominance)
        # High dominance → lower threshold (act with less certainty)
        # Low dominance → higher threshold (need more certainty)
        base_threshold = 0.7
        decision_threshold = base_threshold - (dominance * 0.2)
        decision_threshold = max(0.5, min(0.7, decision_threshold))
        
        params.decision_threshold = decision_threshold
        return params
    
    def bias_action_selection(
        self,
        actions: List[Any],
        valence: float,
        action_type_attr: str = 'type'
    ) -> List[Any]:
        """
        Apply valence-based approach/avoidance bias to action selection.
        
        This modulates action priorities BEFORE any LLM scoring, making
        valence a causal force in action selection.
        
        Args:
            actions: List of action objects or dicts
            valence: Emotional valence (-1.0 to 1.0)
            action_type_attr: Attribute/key name for action type
        
        Returns:
            List of actions with modulated priorities
        """
        if not self.enabled or abs(valence) < 0.2:
            # No significant valence, return unchanged
            return actions
        
        # Bias strength scales with valence magnitude
        bias_strength = abs(valence) * 0.3  # Max 0.3 adjustment
        
        # Approach actions (boosted by positive valence)
        approach_types = ['speak', 'tool_call', 'commit_memory', 'engage', 'explore', 'create', 'connect']
        
        # Avoidance actions (boosted by negative valence)
        avoidance_types = ['wait', 'introspect', 'withdraw', 'defend', 'avoid', 'reject']
        
        for action in actions:
            # Get action type (handle both dict and object)
            if isinstance(action, dict):
                action_type = action.get(action_type_attr, '')
                priority = action.get('priority', 0.5)
            else:
                action_type = getattr(action, action_type_attr, '')
                priority = getattr(action, 'priority', 0.5)
            
            # Convert to string for comparison
            action_type_str = str(action_type).lower()
            
            # Apply bias based on valence
            if valence > 0:
                # Positive valence: boost approach, reduce avoidance
                if any(approach in action_type_str for approach in approach_types):
                    new_priority = min(1.0, priority + (valence * bias_strength))
                    if isinstance(action, dict):
                        action['priority'] = new_priority
                    else:
                        action.priority = new_priority
                elif any(avoid in action_type_str for avoid in avoidance_types):
                    new_priority = max(0.0, priority - (valence * bias_strength))
                    if isinstance(action, dict):
                        action['priority'] = new_priority
                    else:
                        action.priority = new_priority
            else:
                # Negative valence: reduce approach, boost avoidance
                if any(approach in action_type_str for approach in approach_types):
                    new_priority = max(0.0, priority + (valence * bias_strength))  # valence is negative
                    if isinstance(action, dict):
                        action['priority'] = new_priority
                    else:
                        action.priority = new_priority
                elif any(avoid in action_type_str for avoid in avoidance_types):
                    new_priority = min(1.0, priority - (valence * bias_strength))  # valence is negative
                    if isinstance(action, dict):
                        action['priority'] = new_priority
                    else:
                        action.priority = new_priority
        
        return actions
    
    def _update_metrics(
        self,
        arousal: float,
        valence: float,
        dominance: float,
        params: ProcessingParams
    ) -> None:
        """
        Update metrics tracking emotional modulation effects.
        
        These metrics verify that emotions are functionally modulating processing.
        """
        self.metrics.total_modulations += 1
        
        # Track arousal effects
        if arousal > 0.7:
            self.metrics.high_arousal_fast_processing += 1
        elif arousal < 0.3:
            self.metrics.low_arousal_slow_processing += 1
        
        # Record arousal-attention correlation
        self.metrics.arousal_attention_correlations.append(
            (arousal, params.attention_iterations, params.ignition_threshold)
        )
        
        # Track valence effects
        if valence > 0.3:
            self.metrics.positive_valence_approach_bias += 1
        elif valence < -0.3:
            self.metrics.negative_valence_avoidance_bias += 1
        
        # Record valence-action correlation
        self.metrics.valence_action_correlations.append(
            (valence, params.action_bias_strength)
        )
        
        # Track dominance effects
        if dominance > 0.7:
            self.metrics.high_dominance_assertive += 1
        elif dominance < 0.3:
            self.metrics.low_dominance_cautious += 1
        
        # Record dominance-threshold correlation
        self.metrics.dominance_threshold_correlations.append(
            (dominance, params.decision_threshold)
        )
        
        # Keep correlation lists bounded (last 100)
        if len(self.metrics.arousal_attention_correlations) > 100:
            self.metrics.arousal_attention_correlations.pop(0)
        if len(self.metrics.valence_action_correlations) > 100:
            self.metrics.valence_action_correlations.pop(0)
        if len(self.metrics.dominance_threshold_correlations) > 100:
            self.metrics.dominance_threshold_correlations.pop(0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current modulation metrics.
        
        Returns:
            Dictionary of metrics showing emotional modulation effects
        """
        return self.metrics.to_dict()
    
    def reset_metrics(self) -> None:
        """Reset metrics (useful for testing)."""
        self.metrics = ModulationMetrics()
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable emotional modulation.
        
        Used for ablation testing to verify emotions have measurable effects.
        
        Args:
            enabled: Whether to enable modulation
        """
        self.enabled = enabled
        logger.info(f"Emotional modulation {'enabled' if enabled else 'disabled'}")
