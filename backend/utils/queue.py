"""Queue management utilities for Vulna."""

import asyncio
from typing import Dict, Any
from backend.models.findings import QueueItem


class VulnaQueue:
    """Async queue manager with statistics."""
    
    def __init__(self, maxsize: int = 1000):
        self.queue = asyncio.Queue(maxsize=maxsize)
        self.total_items = 0
        self.dropped_items = 0
        
    async def put(self, item: QueueItem) -> bool:
        """Put item in queue, return True if successful."""
        try:
            self.queue.put_nowait(item)
            self.total_items += 1
            return True
        except asyncio.QueueFull:
            self.dropped_items += 1
            return False
    
    async def get(self) -> QueueItem:
        """Get item from queue."""
        return await self.queue.get()
    
    def task_done(self):
        self.queue.task_done()
    
    def qsize(self) -> int:
        return self.queue.qsize()
    
    def empty(self) -> bool:
        return self.queue.empty()
    
    def full(self) -> bool:
        return self.queue.full()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "current_size": self.qsize(),
            "total_items": self.total_items,
            "dropped_items": self.dropped_items,
            "max_size": self.queue.maxsize,
            "is_full": self.full(),
            "is_empty": self.empty()
        }
