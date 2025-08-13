#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/stopwatch_widget.py

import customtkinter as ctk
import time
from classes.stopwatch import Stopwatch
from classes.timer_util import TimerUtil
from .components import FONT

class StopwatchWidget(ctk.CTkFrame):
    """Stopwatch widget component"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#2A2D32", corner_radius=15, **kwargs)
        
        self.stopwatch = Stopwatch()
        self.timer_util = TimerUtil()
        self.selected_algorithm = None
        self._update_job = None
        
        # Set up stopwatch callbacks
        self.stopwatch.on_state_change = self._on_state_change
        
        # StringVars for display
        self.target_var = ctk.StringVar(value="No algorithm selected")
        self.time_var = ctk.StringVar(value="0.000")
        self.state_var = ctk.StringVar(value="Ready")
        
        self.setup_ui()
        self.setup_key_bindings()
        self.start_update_loop()
    
    def setup_ui(self):
        """Setup the stopwatch UI"""
        # Title
        title = ctk.CTkLabel(self, text="Stopwatch", font=(FONT, 24, "bold"))
        title.pack(pady=(15, 5))
        
        # Algorithm target
        self.target_label = ctk.CTkLabel(self, textvariable=self.target_var, font=(FONT, 16), text_color="gray")
        self.target_label.pack(pady=5)
        
        # Timer display
        self.time_label = ctk.CTkLabel(self, textvariable=self.time_var, font=(FONT, 48, "bold"), text_color="white")
        self.time_label.pack(pady=10)
        
        # State display
        self.state_label = ctk.CTkLabel(self, textvariable=self.state_var, font=(FONT, 14), text_color="gray")
        self.state_label.pack(pady=(0, 15))
        
        # Instructions
        instructions = ctk.CTkLabel(self, text="Hold SPACE for 0.5s to start • Press SPACE to stop", font=(FONT, 12), text_color="gray")
        instructions.pack(pady=(0, 15))
    
    def setup_key_bindings(self):
        """Setup keyboard event bindings"""
        toplevel = self.winfo_toplevel()
        toplevel.bind("<KeyPress-space>", self.on_space_press)
        toplevel.bind("<KeyRelease-space>", self.on_space_release)
        toplevel.focus_set()
    
    def remove_key_bindings(self):
        """Remove keyboard event bindings"""
        toplevel = self.winfo_toplevel()
        toplevel.unbind("<KeyPress-space>")
        toplevel.unbind("<KeyRelease-space>")
    
    def on_space_press(self, event):
        """Handle space key press"""
        if not self.selected_algorithm:
            return
        
        if self.stopwatch.running:
            # Stop the timer
            elapsed = self.stopwatch.stop()
            if elapsed > 0:
                success = self.timer_util.save_time(self.selected_algorithm, elapsed)
                if success:
                    # You can emit a signal here for feedback
                    pass
        else:
            # Start hold
            self.stopwatch.start_hold()
            self._check_hold_duration()
    
    def on_space_release(self, event):
        """Handle space key release"""
        if not self.selected_algorithm:
            return
        
        self.stopwatch.release_hold()
    
    def _check_hold_duration(self):
        """Check hold duration periodically"""
        if self.stopwatch.holding:
            self.stopwatch.check_hold_duration()
            self.after(50, self._check_hold_duration)
    
    def _on_state_change(self, state: str):
        """Handle stopwatch state changes"""
        if state == "holding":
            self.state_var.set("Hold...")
            self.time_label.configure(text_color="red")
        elif state == "ready":
            if self.stopwatch.ready:
                self.state_var.set("Ready - Release to start!")
                self.time_label.configure(text_color="green")
            else:
                self.state_var.set("Ready")
                self.time_label.configure(text_color="white")
        elif state == "running":
            self.state_var.set("Running...")
            self.time_label.configure(text_color="white")
        elif state == "stopped":
            self.state_var.set("Stopped")
            # Don't change color when stopping - keep it white
    
    def start_update_loop(self):
        """Start the display update loop"""
        self._update_display()
    
    def _update_display(self):
        """Update the time display"""
        current_time = self.stopwatch.get_time()
        self.time_var.set(f"{current_time:.3f}")
        
        # Schedule next update
        self._update_job = self.after(10, self._update_display)
    
    def set_algorithm(self, algorithm_name: str):
        """Set the selected algorithm"""
        self.selected_algorithm = algorithm_name
        self.target_var.set(f"Timing: {algorithm_name}")
        self.reset()
    
    def reset(self):
        """Reset the stopwatch"""
        if self._update_job:
            self.after_cancel(self._update_job)
        
        self.stopwatch.reset()
        self.time_var.set("0.000")
        self.state_var.set("Ready")
        self.time_label.configure(text_color="white")
        
        # Restart update loop
        self.start_update_loop()
    
    def destroy(self):
        """Clean up when widget is destroyed"""
        if self._update_job:
            self.after_cancel(self._update_job)
        self.remove_key_bindings()
        super().destroy()
