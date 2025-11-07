from pathlib import Path
import asyncio
import logging
import os
from typing import Dict, Any, Optional, List, Tuple, Union
import numpy as np
from .discord_client import EnhancedDiscordClient
from .speech_processor import WhisperProcessor
from .emotional_context import EmotionalContextHandler

# Initialize components
discord_client = EnhancedDiscordClient()
whisper_processor = WhisperProcessor()
emotional_context = EmotionalContextHandler()

async def discord_join_voice_channel(channel_id: str) -> bool:
    """
    Join a Discord voice channel and start listening
    
    Args:
        channel_id: ID of the voice channel to join
        
    Returns:
        bool: True if successfully joined
    """
    try:
        # Join voice channel
        success = await discord_client.join_voice_channel(channel_id)
        if not success:
            return False
            
        # Start listening in background
        asyncio.create_task(_voice_listener(channel_id))
        return True
        
    except Exception as e:
        logger.error(f"Error joining voice channel: {e}")
        return False

async def discord_leave_voice_channel() -> None:
    """Leave the current voice channel"""
    try:
        await discord_client.leave_voice_channel()
    except Exception as e:
        logger.error(f"Error leaving voice channel: {e}")

async def coqui_tts_speak(text: str, voice_id: str = "lyra_voice") -> None:
    """
    Speak text using Coqui XTTS with Lyra's chosen voice
    
    Args:
        text: Text to be spoken
        voice_id: ID of the voice model to use (defaults to Lyra's voice)
    """
    try:
        # Initialize TTS with emotion-aware settings
        from TTS.api import TTS
        
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                  progress_bar=False,
                  gpu=True)
                  
        # Load Lyra's voice embedding
        voice_path = Path(__file__).parent / "voices" / f"{voice_id}.npz"
        if not voice_path.exists():
            raise ValueError(f"Voice file {voice_id}.npz not found")
            
        # Generate speech with emotional prosody
        wav = await asyncio.to_thread(
            tts.tts,
            text=text,
            speaker_wav=str(voice_path),
            language="en"
        )
        
        # Stream to Discord voice channel
        await discord_client.stream_audio(wav)
        
    except Exception as e:
        logger.error(f"Error in TTS: {e}")
        raise

async def _voice_listener(channel_id: str) -> None:
    """Background task to listen to voice channel and process speech"""
    try:
        while True:
            if not discord_client.voice_client:
                break
                
            # Get audio data from Discord
            audio_data = await discord_client.voice_client.receive_audio()
            
            # Process with Whisper
            async for transcribed_text in whisper_processor.process_audio_stream(audio_data):
                if transcribed_text:
                    # Forward to task planner
                    await process_voice_input(transcribed_text, channel_id)
                    
    except Exception as e:
        logger.error(f"Error in voice listener: {e}")
        
async def process_voice_input(text: str, channel_id: str) -> None:
    """Process transcribed voice input through the task planner"""
    try:
        # Add emotional context
        context = emotional_context.get_current_context()
        
        # TODO: Forward to task planner with emotional context
        # This will be implemented when the task planner is ready
        pass
        
    except Exception as e:
        logger.error(f"Error processing voice input: {e}")