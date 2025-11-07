"""
Speech-to-Text processing module for Lyra's auditory perception
"""
import logging
import numpy as np
import whisper
import torch
from typing import Optional, Generator
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

class WhisperProcessor:
    def __init__(self):
        """Initialize Whisper model for Lyra's hearing"""
        self.model = whisper.load_model("medium")  # Balance between accuracy and resource usage
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initialized Whisper processor on {self.device}")
        
        # Audio processing parameters
        self.sample_rate = 16000
        self.chunk_duration = 30  # seconds
        self.min_speech_probability = 0.5
        
        # Emotional context tracking
        self.voice_context = {
            "speaker_tone": None,
            "emotional_markers": [],
            "confidence": 0.0
        }
    
    async def process_audio_stream(self, 
                                 audio_generator: Generator[np.ndarray, None, None],
                                 language: str = "en") -> Generator[str, None, None]:
        """
        Process incoming audio stream with emotional context awareness
        
        Args:
            audio_generator: Generator yielding audio chunks
            language: Expected language code
            
        Yields:
            Transcribed text with high confidence
        """
        current_buffer = np.array([])
        
        async for chunk in audio_generator:
            # Append to buffer
            current_buffer = np.concatenate([current_buffer, chunk])
            
            # Process when we have enough audio
            if len(current_buffer) >= self.sample_rate * self.chunk_duration:
                # Transcribe with emotional context
                result = await self._transcribe_with_context(current_buffer, language)
                
                if result and result["confidence"] > self.min_speech_probability:
                    # Update emotional context
                    self._update_voice_context(result)
                    
                    # Yield transcribed text
                    yield result["text"]
                
                # Reset buffer with small overlap
                overlap = int(0.5 * self.sample_rate)  # 0.5 second overlap
                current_buffer = current_buffer[-overlap:] if len(current_buffer) > overlap else np.array([])
    
    async def _transcribe_with_context(self, 
                                     audio_data: np.ndarray, 
                                     language: str) -> Optional[dict]:
        """
        Transcribe audio while maintaining emotional context
        """
        try:
            result = await asyncio.to_thread(
                self.model.transcribe,
                audio_data,
                language=language,
                task="transcribe",
                fp16=torch.cuda.is_available()
            )
            
            # Enhance with emotional context
            result["emotional_context"] = {
                "tone": self._detect_tone(audio_data),
                "confidence": float(result["confidence"]),
                "speaker_consistency": self._check_speaker_consistency(audio_data)
            }
            
            return result
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def _detect_tone(self, audio_data: np.ndarray) -> str:
        """
        Detect emotional tone in speech
        """
        # This would integrate with more sophisticated tone analysis
        # For now, return a neutral tone
        return "neutral"
    
    def _check_speaker_consistency(self, audio_data: np.ndarray) -> float:
        """
        Check if the current speaker is consistent
        """
        # This would integrate with speaker diarization
        # For now, return high consistency
        return 0.95
    
    def _update_voice_context(self, result: dict) -> None:
        """
        Update ongoing voice context tracking
        """
        self.voice_context["confidence"] = result["confidence"]
        self.voice_context["emotional_markers"].append(result["emotional_context"]["tone"])
        # Keep only recent context
        if len(self.voice_context["emotional_markers"]) > 10:
            self.voice_context["emotional_markers"] = self.voice_context["emotional_markers"][-10:]