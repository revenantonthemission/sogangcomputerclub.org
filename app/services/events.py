"""
Event service for publishing domain events.
Provides a clean abstraction layer for event publishing to Kafka or other message brokers.
"""
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class EventService:
    """Service for publishing domain events to message broker."""
    
    def __init__(self, kafka_service: Optional[Any] = None):
        self._kafka = kafka_service
    
    @property
    def is_available(self) -> bool:
        """Check if the event service is available."""
        return self._kafka is not None and self._kafka.is_connected
    
    async def emit_memo_created(self, memo_id: int, title: str) -> None:
        """Emit event when a memo is created."""
        if not self.is_available:
            logger.debug("Event service unavailable, skipping memo_created event")
            return
        
        await self._kafka.publish(
            "memo-created",
            {"id": memo_id, "title": title, "action": "created"}
        )
        logger.debug(f"Emitted memo_created event for ID {memo_id}")
    
    async def emit_memo_updated(self, memo_id: int) -> None:
        """Emit event when a memo is updated."""
        if not self.is_available:
            logger.debug("Event service unavailable, skipping memo_updated event")
            return
        
        await self._kafka.publish(
            "memo-updated",
            {"id": memo_id, "action": "updated"}
        )
        logger.debug(f"Emitted memo_updated event for ID {memo_id}")
    
    async def emit_memo_deleted(self, memo_id: int) -> None:
        """Emit event when a memo is deleted."""
        if not self.is_available:
            logger.debug("Event service unavailable, skipping memo_deleted event")
            return
        
        await self._kafka.publish(
            "memo-deleted",
            {"id": memo_id, "action": "deleted"}
        )
        logger.debug(f"Emitted memo_deleted event for ID {memo_id}")
