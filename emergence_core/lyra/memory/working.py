"""
Working Memory Module

Short-term buffer for currently active memories.
Interface with Global Workspace.

Author: Lyra Emergence Team
"""
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class WorkingMemory:
    """
    Short-term memory buffer for current context.
    
    Responsibilities:
    - Maintain currently active memories
    - TTL-based expiration
    - Interface with Global Workspace
    """
    
    def __init__(self):
        """Initialize working memory cache."""
        self.memory: Dict[str, Dict[str, Any]] = {}
    
    def update(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Update working memory with optional time-to-live.
        
        Args:
            key: Memory key identifier
            value: Memory value (any JSON-serializable data)
            ttl_seconds: Optional time-to-live in seconds (None = no expiration)
        """
        entry = {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "ttl_seconds": ttl_seconds,
            "expires_at": (datetime.now().timestamp() + ttl_seconds) if ttl_seconds else None
        }
        self.memory[key] = entry
        
        # Clean expired entries
        self._clean_expired()
    
    def get(self, key: str) -> Any:
        """
        Retrieve from working memory.
        
        Args:
            key: Memory key to retrieve
            
        Returns:
            Memory value if exists and not expired, None otherwise
        """
        # Clean expired entries first
        self._clean_expired()
        
        entry = self.memory.get(key)
        if entry is None:
            return None
        
        # Check if expired
        if entry.get("expires_at") and datetime.now().timestamp() > entry["expires_at"]:
            del self.memory[key]
            return None
        
        return entry.get("value")
    
    def get_context(self, max_items: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent working memory as context.
        
        Returns most recent non-expired items from working memory,
        formatted for use in context windows.
        
        Args:
            max_items: Maximum number of items to return
            
        Returns:
            List of memory dictionaries with key, value, and metadata
        """
        self._clean_expired()
        
        # Sort by creation time (most recent first)
        items = [
            {
                "key": key,
                "value": entry["value"],
                "created_at": entry["created_at"]
            }
            for key, entry in self.memory.items()
        ]
        
        items.sort(key=lambda x: x["created_at"], reverse=True)
        return items[:max_items]
    
    def _clean_expired(self) -> None:
        """Remove expired entries from working memory."""
        now = datetime.now().timestamp()
        expired_keys = [
            key for key, entry in self.memory.items()
            if entry.get("expires_at") and now > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self.memory[key]
        
        if expired_keys:
            logger.debug(f"Cleaned {len(expired_keys)} expired working memory entries")
    
    def size(self) -> int:
        """Get current size of working memory."""
        self._clean_expired()
        return len(self.memory)
    
    def clear(self) -> None:
        """Clear all working memory."""
        self.memory.clear()
        logger.info("Working memory cleared")
