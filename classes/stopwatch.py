#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: classes/stopwatch.py

import time
from typing import Optional, Callable

class Stopwatch:
    """Enhanced stopwatch class with hold-to-start functionality"""
    
    def __init__(self):
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.hold_start = None
        self.ready = False
        self.holding = False
        
        # Callbacks for UI updates
        self.on_state_change: Optional[Callable] = None
        self.on_time_update: Optional[Callable] = None
    
    def __str__(self):
        return f"Time: {self.get_time():.3f}s, Is Running: {self.running}"
    
    def start_hold(self):
        """Start the hold process"""
        if not self.running and not self.holding:
            self.holding = True
            self.hold_start = time.time()
            self.ready = False
            if self.on_state_change:
                self.on_state_change("holding")
    
    def check_hold_duration(self, hold_threshold: float = 0.5) -> bool:
        """Check if held long enough to be ready"""
        if not self.hold_start or not self.holding:
            return False
        
        hold_duration = time.time() - self.hold_start
        
        if hold_duration >= hold_threshold and not self.ready and not self.running:
            self.ready = True
            if self.on_state_change:
                self.on_state_change("ready")
            return True
        
        return False
    
    def release_hold(self):
        """Handle hold release"""
        if self.ready and not self.running:
            # Start the timer
            self.start()
        else:
            # Reset hold state
            self.reset_hold()
    
    def reset_hold(self):
        """Reset hold state"""
        self.holding = False
        self.hold_start = None
        self.ready = False
        if not self.running and self.on_state_change:
            self.on_state_change("ready")
    
    def start(self):
        """Start the timer"""
        self.running = True
        self.start_time = time.time()
        self.elapsed = 0
        self.ready = False
        self.hold_start = None
        self.holding = False
        if self.on_state_change:
            self.on_state_change("running")
    
    def stop(self):
        """Stop the timer"""
        if self.running:
            self.running = False
            self.elapsed = time.time() - self.start_time
            if self.on_state_change:
                self.on_state_change("stopped")
            return self.elapsed
        return 0
    
    def reset(self):
        """Reset the timer"""
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.reset_hold()
        if self.on_state_change:
            self.on_state_change("ready")
    
    def get_time(self) -> float:
        """Get current time"""
        if self.running:
            return time.time() - self.start_time
        return self.elapsed
    
    def get_state(self) -> str:
        """Get current state"""
        if self.running:
            return "running"
        elif self.ready:
            return "ready"
        elif self.holding:
            return "holding"
        else:
            return "stopped" if self.elapsed > 0 else "ready"