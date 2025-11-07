"""
Enhanced Discord client with voice capabilities for Lyra
"""
import discord
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Union
import numpy as np

logger = logging.getLogger(__name__)

class EnhancedDiscordClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.voice_client = None
        self.current_channel = None
        
    async def join_voice_channel(self, channel_id: str) -> bool:
        """Join a voice channel and prepare for audio streaming"""
        try:
            channel = self.get_channel(int(channel_id))
            if not channel:
                raise ValueError(f"Could not find voice channel with ID {channel_id}")
                
            if not isinstance(channel, discord.VoiceChannel):
                raise TypeError(f"Channel {channel_id} is not a voice channel")
            
            # Connect to voice
            self.voice_client = await channel.connect()
            self.current_channel = channel
            logger.info(f"Connected to voice channel: {channel.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join voice channel: {e}")
            return False
            
    async def leave_voice_channel(self) -> None:
        """Leave the current voice channel"""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            self.current_channel = None
            
    async def stream_audio(self, audio_data: Union[np.ndarray, bytes]) -> None:
        """Stream audio data to the current voice channel"""
        if not self.voice_client:
            raise RuntimeError("Not connected to any voice channel")
            
        try:
            # Convert numpy array to bytes if needed
            if isinstance(audio_data, np.ndarray):
                audio_data = audio_data.tobytes()
            
            # Create audio source
            audio_source = discord.FFmpegPCMAudio(audio_data)
            
            # Play audio
            self.voice_client.play(
                audio_source,
                after=lambda e: logger.error(f"Audio streaming error: {e}") if e else None
            )
            
            # Wait for audio to finish
            while self.voice_client.is_playing():
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error streaming audio: {e}")
            raise
            
    async def send_message(self, 
                          message: str, 
                          channel_id: Optional[str] = None) -> None:
        """Send a text message to a Discord channel"""
        try:
            channel = self.get_channel(int(channel_id))
            if not channel:
                raise ValueError(f"Could not find channel with ID {channel_id}")
                
            await channel.send(message)
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise