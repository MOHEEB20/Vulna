"""Simple file watcher for monitoring request files."""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
import uuid


class SimpleFileWatcher:
    """Simple file watcher for monitoring request files."""
    
    def __init__(self, filepath, queue, poll_interval=0.5):
        self.filepath = Path(filepath)
        self.queue = queue
        self.poll_interval = poll_interval
        self._running = False
        self._task = None
        self.last_size = 0
        self.processed_lines = set()
    
    async def start(self):
        """Start the file watcher."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._watch_loop())
        print(f"[FileWatcher] Started for {self.filepath}")
    
    async def stop(self):
        """Stop the file watcher."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print(f"[FileWatcher] Stopped for {self.filepath}")
    
    async def _watch_loop(self):
        """Main watching loop."""
        try:
            while self._running:
                await self._check_file()
                await asyncio.sleep(self.poll_interval)
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[FileWatcher] Error: {e}")
    
    async def _check_file(self):
        """Check file for new content."""
        try:
            if not self.filepath.exists():
                return
            
            current_size = self.filepath.stat().st_size
            
            if current_size > self.last_size:
                # Read new content
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    f.seek(self.last_size)
                    new_content = f.read()
                
                # Process new lines
                for line in new_content.strip().split('\n'):
                    if line and line not in self.processed_lines:
                        await self._process_line(line)
                        self.processed_lines.add(line)
                
                self.last_size = current_size
        
        except Exception as e:
            print(f"[FileWatcher] Check file error: {e}")
    
    async def _process_line(self, line):
        """Process a single line from the file."""
        try:
            # Parse JSON line
            request_data = json.loads(line)
            
            # Create simple queue item dict instead of complex objects
            queue_item = {
                'id': str(uuid.uuid4())[:8],
                'method': request_data['method'],
                'url': request_data['url'],
                'headers': request_data.get('headers', {}),
                'body': request_data.get('body'),
                'timestamp': request_data['timestamp']
            }
            
            # Add to queue (simplified)
            if hasattr(self.queue, 'queue'):
                try:
                    self.queue.queue.put_nowait(queue_item)
                    print(f"[FileWatcher] Queued: {queue_item['method']} {queue_item['url'][:50]}...")
                except:
                    print(f"[FileWatcher] Queue full, dropped request")
            
        except Exception as e:
            print(f"[FileWatcher] Process line error: {e}")
