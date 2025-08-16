#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: classes/stopwatch.py

import time

class Stopwatch:    
    def __init__(self):
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.hold_start = None
        self.ready = False
        self.holding = False
        
        self.on_state_change = None
        self.on_time_update = None
    
    def __str__(self):
        return f"Time: {self.get_time():.3f}s, Is Running: {self.running}"
    
    def start_hold(self):
        """
        Function: Begin the hold to start process for the stopwatch
        Input: none
        Outputs: none
        """
        if not self.running and not self.holding:
            self.holding = True
            self.hold_start = time.time()
            self.ready = False
            if self.on_state_change:
                self.on_state_change("holding")
    
    # hold_threshold: float, seconds required to ready up (float for timing)
    # Returns: bool (True if ready, False otherwise)
    def check_hold_duration(self, hold_threshold: float = 0.5) -> bool:
        """
        Function: Check whether the user has held the spacebar past the threshold to become ready
        Input: hold_threshold (seconds required for the stopwatch to ready up when the user holds the spacebar)
        Outputs: True if ready, otherwise False
        """
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
        """
        Function: Handle release after the user holds spacebar
        Input: none
        Outputs: none (starts timer if ready otherwise resets hold state)
        """
        if self.ready and not self.running:
            # Start the timer
            self.start()
        else:
            # Reset hold state (user released spacebar)
            self.reset_hold()
    
    def reset_hold(self):
        """
        Function: Reset the hold state
        Input: none
        Outputs: none
        """
        self.holding = False
        self.hold_start = None
        self.ready = False
        if not self.running and self.on_state_change:
            self.on_state_change("ready")
    
    def start(self):
        """
        Function: Start the stopwatch
        Input: none
        Outputs: none
        """
        self.running = True
        self.start_time = time.time()
        self.elapsed = 0
        self.ready = False
        self.hold_start = None
        self.holding = False
        if self.on_state_change:
            self.on_state_change("running")
    
    def stop(self):
        """
        Function: Stop the stopwatch and calculate the final time
        Input: none
        Outputs: Elapsed time in seconds to three decimal places, return 0 if the stopwatch was not running
        """
        if self.running:
            self.running = False
            # Get the current time and subtract by the time the stopwatch started to get elapsed time
            self.elapsed = time.time() - self.start_time
            if self.on_state_change:
                self.on_state_change("stopped")
            return round(self.elapsed, 3)
        return 0
    
    def reset(self):
        """
        Function: Reset the stopwatch to initial state
        Input: none
        Outputs: none
        """
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.reset_hold()
        if self.on_state_change:
            self.on_state_change("ready")
    
    # No args. Gets the current elapsed time.
    # Returns: float (elapsed time in seconds)
    def get_time(self) -> float:
        """
        Function: Get the current elapsed time
        Input: none
        Outputs: Elapsed time in seconds to three decimal points. If running, time since start, otherwise last time that was recorded
        """
        if self.running:
            return round(time.time() - self.start_time, 3)
        return round(self.elapsed, 3)

    # No args. Gets the current stopwatch state label.
    # Returns: str ("running", "ready", "holding", or "stopped")
    def get_state(self) -> str:
        """
        Function: Get the current stopwatch state label
        Input: none
        Outputs: Either "running", "ready", "holding", "stopped"
        """
        if self.running:
            return "running"
        elif self.ready:
            return "ready"
        elif self.holding:
            return "holding"
        else:
            return "stopped" if self.elapsed > 0 else "ready"