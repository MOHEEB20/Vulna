"""File watcher utilities for monitoring request files."""

import asyncio
import json
import os
from pathlib import Path
from typing import AsyncGenerator, Optional
from backend.models.findings import HttpRequest, HttpMethod, QueueItem
from datetime import datetime
import uuid


async def tail_file(filepath: str, poll_interval: float = 0.5) -> AsyncGenerator[QueueItem, None]:
    """
    Tail a JSONL file and yield new QueueItems as they appear.
    STARTUP OPTIMIZATION: Only processes NEW requests added after startup
    
    Args:
        filepath: Path to the JSONL file to monitor
        poll_interval: How often to check for new content (seconds)
    
    Yields:
        QueueItem objects for new requests
    """
    filepath = Path(filepath)
    processed_lines = set()
    
    # STARTUP FIX: Start from END of file to avoid re-processing existing requests
    if filepath.exists():
        last_size = filepath.stat().st_size
        print(f"[i] Starting file monitoring from position: {last_size} (skipping existing content)")
    else:
        last_size = 0
        print(f"[i] File {filepath} does not exist, monitoring for creation")
    
    while True:
        try:
            if filepath.exists():
                current_size = filepath.stat().st_size
                
                if current_size > last_size:
                    # Read new content
                    with open(filepath, 'r', encoding='utf-8') as f:
                        f.seek(last_size)
                        new_content = f.read()
                        
                    # Process new lines
                    for line in new_content.strip().split('\n'):
                        if line and line not in processed_lines:
                            try:
                                # Parse JSON line
                                request_data = json.loads(line)
                                
                                # Create HttpRequest object
                                request = HttpRequest(
                                    method=HttpMethod(request_data['method']),
                                    url=request_data['url'],
                                    headers=request_data.get('headers', {}),
                                    body=request_data.get('body'),
                                    timestamp=datetime.fromisoformat(request_data['timestamp'])
                                )
                                
                                # Create QueueItem
                                queue_item = QueueItem(
                                    id=str(uuid.uuid4())[:8],
                                    request=request,
                                    priority=_calculate_priority(request)
                                )
                                
                                processed_lines.add(line)
                                yield queue_item
                                
                            except (json.JSONDecodeError, KeyError, ValueError) as e:
                                print(f"Failed to parse request line: {e}")
                                continue
                    
                    last_size = current_size
            
            await asyncio.sleep(poll_interval)
            
        except Exception as e:
            print(f"File watcher error: {e}")
            await asyncio.sleep(poll_interval)


def _calculate_priority(request: HttpRequest) -> int:
    """
    Calculate processing priority for a request.
    Higher numbers = higher priority
    
    Args:
        request: The HTTP request to analyze
        
    Returns:
        Priority score (0-10)
    """
    priority = 0
    
    # POST/PUT/DELETE are higher priority than GET
    if request.method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.DELETE]:
        priority += 3
    elif request.method == HttpMethod.GET:
        priority += 1
    
    # Forms and APIs are higher priority
    url_lower = request.url.lower()
    if any(keyword in url_lower for keyword in ['api', 'login', 'admin', 'upload', 'form']):
        priority += 2
    
    # Requests with bodies are higher priority
    if request.body and len(request.body) > 10:
        priority += 2
    
    # Authentication headers indicate higher priority
    auth_headers = ['authorization', 'cookie', 'x-auth-token']
    if any(header.lower() in request.headers for header in auth_headers):
        priority += 1
    
    return min(priority, 10)  # Cap at 10


class FileWatcher:
    """
    File watcher for monitoring request files and feeding the queue.
    """
    
    def __init__(self, filepath: str, queue, poll_interval: float = 0.5):
        self.filepath = filepath
        self.queue = queue
        self.poll_interval = poll_interval
        self._running = False
        self._task = None
    
    async def start(self):
        """Start the file watcher."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._watch_loop())
        print(f"File watcher started for {self.filepath}")
    
    async def stop(self):
        """Stop the file watcher."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print(f"File watcher stopped for {self.filepath}")
    
    async def _watch_loop(self):
        """Main watching loop."""
        try:
            async for queue_item in tail_file(self.filepath, self.poll_interval):
                if not self._running:
                    break
                
                # Add to queue
                success = await self.queue.put(queue_item)
                if success:
                    print(f"Queued: {queue_item.request.method} {queue_item.request.url[:50]}...")
                else:
                    print(f"Queue full, dropped: {queue_item.request.method} {queue_item.request.url[:50]}...")
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"File watcher error: {e}")
