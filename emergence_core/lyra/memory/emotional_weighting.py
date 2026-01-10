"""
Emotional Weighting Module

Emotional salience affects storage and retrieval priority.
High-emotion memories get preferential treatment.

Author: Lyra Emergence Team
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class EmotionalWeighting:
    """
    Manages emotional salience in memory operations.
    
    Responsibilities:
    - Emotional salience scoring
    - High-emotion memories get storage priority
    - Emotional state biases retrieval
    """
    
    def __init__(self):
        """Initialize emotional weighting system."""
        # Emotional intensity weights (can be tuned)
        self.emotion_weights = {
            "joy": 0.8,
            "surprise": 0.9,
            "fear": 1.0,
            "anger": 0.9,
            "sadness": 0.8,
            "trust": 0.7,
            "anticipation": 0.6,
            "disgust": 0.7,
            # Extended tones
            "curious": 0.6,
            "thoughtful": 0.7,
            "engaged": 0.7,
            "reflective": 0.8,
            "excited": 0.9,
            "concerned": 0.8,
            "hopeful": 0.7,
            "grateful": 0.8,
        }
    
    def calculate_salience(self, memory: Dict[str, Any]) -> float:
        """
        Calculate emotional salience score for a memory.
        
        Args:
            memory: Memory dictionary with emotional_tone field
            
        Returns:
            Salience score (0.0-1.0), higher means more emotionally significant
        """
        emotional_tones = memory.get("emotional_tone", [])
        
        if not emotional_tones:
            return 0.5  # Neutral baseline
        
        # Calculate average weight of all emotional tones
        weights = []
        for tone in emotional_tones:
            tone_lower = tone.lower()
            weight = self.emotion_weights.get(tone_lower, 0.5)
            weights.append(weight)
        
        if weights:
            salience = sum(weights) / len(weights)
            logger.debug(f"Calculated salience {salience:.2f} for tones: {emotional_tones}")
            return salience
        
        return 0.5
    
    def should_prioritize_storage(self, memory: Dict[str, Any], threshold: float = 0.7) -> bool:
        """
        Determine if a memory should get prioritized storage.
        
        High emotional salience memories get immediate indexing
        and enhanced storage priority.
        
        Args:
            memory: Memory to evaluate
            threshold: Salience threshold for prioritization
            
        Returns:
            True if should prioritize, False otherwise
        """
        salience = self.calculate_salience(memory)
        should_prioritize = salience >= threshold
        
        if should_prioritize:
            logger.info(f"Memory prioritized for storage (salience: {salience:.2f})")
        
        return should_prioritize
    
    def weight_retrieval_results(
        self,
        memories: List[Dict[str, Any]],
        current_emotional_state: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Bias retrieval results based on emotional congruence.
        
        Memories matching current emotional state get boosted scores.
        This simulates mood-congruent memory retrieval.
        
        Args:
            memories: List of retrieved memories
            current_emotional_state: Current emotional tones
            
        Returns:
            Weighted and re-sorted memory list
        """
        if not current_emotional_state:
            return memories
        
        current_state_lower = [tone.lower() for tone in current_emotional_state]
        
        # Add emotional congruence scores
        for memory in memories:
            memory_tones = [tone.lower() for tone in memory.get("emotional_tone", [])]
            
            # Calculate overlap between current state and memory
            overlap = len(set(current_state_lower) & set(memory_tones))
            congruence = overlap / max(len(current_state_lower), 1)
            
            # Store congruence score
            memory["emotional_congruence"] = congruence
            
            # Boost overall score if congruent
            if congruence > 0:
                logger.debug(
                    f"Memory emotional congruence: {congruence:.2f} "
                    f"(current: {current_emotional_state}, memory: {memory_tones})"
                )
        
        # Sort by congruence (higher first), then by original order
        memories.sort(
            key=lambda m: (m.get("emotional_congruence", 0), m.get("timestamp", "")),
            reverse=True
        )
        
        return memories
    
    def get_emotion_weight(self, emotion: str) -> float:
        """
        Get the salience weight for a specific emotion.
        
        Args:
            emotion: Emotion name
            
        Returns:
            Weight value (0.0-1.0)
        """
        return self.emotion_weights.get(emotion.lower(), 0.5)
    
    def update_emotion_weight(self, emotion: str, weight: float) -> None:
        """
        Update the salience weight for an emotion.
        
        Args:
            emotion: Emotion name
            weight: New weight value (0.0-1.0)
        """
        if 0.0 <= weight <= 1.0:
            self.emotion_weights[emotion.lower()] = weight
            logger.info(f"Updated emotion weight: {emotion} -> {weight}")
        else:
            logger.warning(f"Invalid weight value {weight} for emotion {emotion}, must be 0.0-1.0")
