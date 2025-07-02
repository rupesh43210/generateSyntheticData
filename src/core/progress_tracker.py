"""
Real-time progress tracking system with WebSocket support
"""

import time
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(Enum):
    GENERATION = "generation"
    VALIDATION = "validation"
    EXPORT = "export"
    ANALYSIS = "analysis"

@dataclass
class ProgressUpdate:
    task_id: str
    task_type: TaskType
    status: TaskStatus
    progress_percent: float
    current_step: str
    current_count: int
    total_count: int
    elapsed_time: float
    estimated_remaining: Optional[float] = None
    rate_per_second: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ProgressTracker:
    """Advanced progress tracking with real-time updates"""
    
    def __init__(self):
        self.tasks: Dict[str, ProgressUpdate] = {}
        self.callbacks: List[Callable[[ProgressUpdate], None]] = []
        self.lock = threading.Lock()
    
    def create_task(self, 
                   task_type: TaskType, 
                   total_count: int, 
                   description: str = "") -> str:
        """Create a new task and return its ID"""
        task_id = str(uuid.uuid4())
        
        with self.lock:
            self.tasks[task_id] = ProgressUpdate(
                task_id=task_id,
                task_type=task_type,
                status=TaskStatus.PENDING,
                progress_percent=0.0,
                current_step=description or "Initializing",
                current_count=0,
                total_count=total_count,
                elapsed_time=0.0,
                metadata={"created_at": time.time()}
            )
        
        self._notify_callbacks(self.tasks[task_id])
        return task_id
    
    def start_task(self, task_id: str, description: str = "Starting"):
        """Mark task as started"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.RUNNING
                task.current_step = description
                task.metadata = task.metadata or {}
                task.metadata["started_at"] = time.time()
        
        self._notify_callbacks(self.tasks[task_id])
    
    def update_progress(self, 
                       task_id: str, 
                       current_count: int, 
                       step_description: str = None,
                       metadata: Dict[str, Any] = None):
        """Update task progress"""
        with self.lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.current_count = current_count
            task.progress_percent = (current_count / task.total_count) * 100
            
            if step_description:
                task.current_step = step_description
            
            # Calculate timing metrics
            current_time = time.time()
            start_time = task.metadata.get("started_at", current_time)
            task.elapsed_time = current_time - start_time
            
            if task.elapsed_time > 0 and current_count > 0:
                task.rate_per_second = current_count / task.elapsed_time
                
                remaining_items = task.total_count - current_count
                if task.rate_per_second > 0:
                    task.estimated_remaining = remaining_items / task.rate_per_second
            
            # Update metadata
            if metadata:
                task.metadata = task.metadata or {}
                task.metadata.update(metadata)
        
        self._notify_callbacks(self.tasks[task_id])
    
    def complete_task(self, task_id: str, final_metadata: Dict[str, Any] = None):
        """Mark task as completed"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.progress_percent = 100.0
                task.current_step = "Completed"
                task.current_count = task.total_count
                
                current_time = time.time()
                task.metadata = task.metadata or {}
                task.metadata["completed_at"] = current_time
                
                if final_metadata:
                    task.metadata.update(final_metadata)
        
        self._notify_callbacks(self.tasks[task_id])
    
    def fail_task(self, task_id: str, error_message: str, metadata: Dict[str, Any] = None):
        """Mark task as failed"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.FAILED
                task.current_step = "Failed"
                task.error_message = error_message
                
                current_time = time.time()
                task.metadata = task.metadata or {}
                task.metadata["failed_at"] = current_time
                
                if metadata:
                    task.metadata.update(metadata)
        
        self._notify_callbacks(self.tasks[task_id])
    
    def cancel_task(self, task_id: str):
        """Cancel a running task"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.CANCELLED
                task.current_step = "Cancelled"
                
                current_time = time.time()
                task.metadata = task.metadata or {}
                task.metadata["cancelled_at"] = current_time
        
        self._notify_callbacks(self.tasks[task_id])
    
    def get_task(self, task_id: str) -> Optional[ProgressUpdate]:
        """Get task by ID"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, ProgressUpdate]:
        """Get all tasks"""
        with self.lock:
            return self.tasks.copy()
    
    def get_active_tasks(self) -> Dict[str, ProgressUpdate]:
        """Get all active (running) tasks"""
        with self.lock:
            return {
                task_id: task for task_id, task in self.tasks.items()
                if task.status == TaskStatus.RUNNING
            }
    
    def cleanup_completed_tasks(self, max_age_seconds: int = 3600):
        """Remove old completed tasks"""
        current_time = time.time()
        to_remove = []
        
        with self.lock:
            for task_id, task in self.tasks.items():
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    completed_time = task.metadata.get("completed_at") or task.metadata.get("failed_at") or task.metadata.get("cancelled_at")
                    if completed_time and (current_time - completed_time) > max_age_seconds:
                        to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.tasks[task_id]
    
    def add_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Add a callback for progress updates"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Remove a callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, progress: ProgressUpdate):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(progress)
            except Exception as e:
                # Log callback errors but don't let them break progress tracking
                print(f"Progress callback error: {e}")

class WebSocketProgressNotifier:
    """WebSocket notifier for progress updates"""
    
    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
        self.active_clients: Dict[str, set] = {}  # task_id -> set of client session IDs
    
    def subscribe_client(self, session_id: str, task_id: str):
        """Subscribe a client to task updates"""
        if task_id not in self.active_clients:
            self.active_clients[task_id] = set()
        self.active_clients[task_id].add(session_id)
    
    def unsubscribe_client(self, session_id: str, task_id: str = None):
        """Unsubscribe a client from task updates"""
        if task_id:
            if task_id in self.active_clients:
                self.active_clients[task_id].discard(session_id)
                if not self.active_clients[task_id]:
                    del self.active_clients[task_id]
        else:
            # Remove from all tasks
            for task_clients in self.active_clients.values():
                task_clients.discard(session_id)
            # Clean up empty task client sets
            self.active_clients = {
                task_id: clients for task_id, clients in self.active_clients.items()
                if clients
            }
    
    def notify_progress(self, progress: ProgressUpdate):
        """Send progress update to subscribed clients"""
        task_id = progress.task_id
        
        if task_id in self.active_clients:
            # Convert progress to dict for JSON serialization
            progress_dict = asdict(progress)
            progress_dict['task_type'] = progress.task_type.value
            progress_dict['status'] = progress.status.value
            
            # Send to all subscribed clients
            for client_session in self.active_clients[task_id]:
                self.socketio.emit('progress_update', progress_dict, room=client_session)
        
        # Also broadcast to general progress room
        progress_dict = asdict(progress)
        progress_dict['task_type'] = progress.task_type.value
        progress_dict['status'] = progress.status.value
        self.socketio.emit('progress_update', progress_dict, room='progress_updates')

# Global progress tracker instance
progress_tracker = ProgressTracker()