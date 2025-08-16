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
    
    # parent (CTk widget): Parent widget
    # **kwargs: Additional widget options
    # No return
    def __init__(self, parent, **kwargs):
        """
        Function: Initialise the stopwatch widget
        Input: parent (CTk widget), **kwargs
        Outputs: None
        """
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
        
        self.setup_ui()
        self.setup_key_bindings()
        self.start_update_loop()
    
    # No arguments
    # No return
    def setup_ui(self):
        """
        Function: Setup the stopwatch UI
        Input: None
        Outputs: None
        """
        # Title
        title = ctk.CTkLabel(self, text="Stopwatch", font=(FONT, 24, "bold"))
        title.pack(pady=(15, 5))
        
        # Algorithm target
        self.target_label = ctk.CTkLabel(self, textvariable=self.target_var, font=(FONT, 16), text_color="gray")
        self.target_label.pack(pady=5)
        
        # Timer display
        self.time_label = ctk.CTkLabel(self, textvariable=self.time_var, font=(FONT, 48, "bold"), text_color="white")
        self.time_label.pack(pady=10)
        
        # Instructions
        instructions = ctk.CTkLabel(self, text="Hold spacebar for 0.5s to start, press spacebar to stop", font=(FONT, 12), text_color="gray")
        instructions.pack(pady=(0, 15))
    
    def setup_key_bindings(self):
        """
        Function: Setup keyboard event bindings
        Input: None
        Outputs: None
        """
        toplevel = self.winfo_toplevel()
        toplevel.bind("<KeyPress-space>", self.on_space_press)
        toplevel.bind("<KeyRelease-space>", self.on_space_release)
        toplevel.focus_set()

    def remove_key_bindings(self):
        """
        Function: Remove keyboard event bindings
        Input: None
        Outputs: None
        """
        toplevel = self.winfo_toplevel()
        toplevel.unbind("<KeyPress-space>")
        toplevel.unbind("<KeyRelease-space>")

    def on_space_press(self, event: None):
        """
        Function: Handle space key press
        Input: event (keyboard event)
        Outputs: None
        """
        # Make sure that stopwatch cant be started when in the searchbar
        focused_widget = self.winfo_toplevel().focus_get()
        if focused_widget and hasattr(focused_widget, 'get'):
            return
            
        if not self.selected_algorithm:
            return
        
        if self.stopwatch.running:
            # Stop the timer
            elapsed = self.stopwatch.stop()
            if elapsed > 0:
                success = self.timer_util.save_time(self.selected_algorithm, elapsed)
                if success:
                    pass
        else:
            # Start hold
            self.stopwatch.start_hold()
            self._check_hold_duration()
    
    # event: Keyboard event object, required for event handling
    # No return
    def on_space_release(self, event: None):
        """
        Function: Handle space key release
        Input: event (keyboard event)
        Outputs: None
        """
        # Make sure that stopwatch cant be started when in the searchbar
        focused_widget = self.winfo_toplevel().focus_get()
        if focused_widget and hasattr(focused_widget, 'get'):
            return
            
        if not self.selected_algorithm:
            return
        
        self.stopwatch.release_hold()

    def _check_hold_duration(self):
        """
        Function: Check hold duration every 50 milliseconds
        Input: None
        Outputs: None
        """
        if self.stopwatch.holding:
            self.stopwatch.check_hold_duration()
            self.after(50, self._check_hold_duration)
    
    def _on_state_change(self, state):
        """
        Function: Handle stopwatch state changes
        Input: state (str)
        Outputs: None
        """
        if state == "holding":
            self.time_label.configure(text_color="red")
        elif state == "ready":
            if self.stopwatch.ready:
                self.time_label.configure(text_color="green")
            else:
                self.time_label.configure(text_color="white")
        elif state == "running":
            self.time_label.configure(text_color="white")

    def start_update_loop(self):
        """
        Function: Start the display update loop
        Input: None
        Outputs: None
        """
        self._update_display()

    def _update_display(self):
        """
        Function: Update the time display
        Input: None
        Outputs: None
        """
        current_time = self.stopwatch.get_time()
        self.time_var.set(f"{current_time:.3f}")
        
        # Schedule next update after 10 milliseconds
        self._update_job = self.after(10, self._update_display)
    
    # algorithm_name (str or None): Name of selected algorithm, string for display, None for no selection
    # No return
    def set_algorithm(self, algorithm_name):
        """
        Function: Set the selected algorithm
        Input: algorithm_name (str or None)
        Outputs: None
        """
        self.selected_algorithm = algorithm_name
        if algorithm_name is None:
            self.target_var.set("No algorithm selected")
        else:
            self.target_var.set(f"Timing: {algorithm_name}")
        self.reset()
    
    def reset(self):
        """
        Function: Reset the stopwatch
        Input: None
        Outputs: None
        """
        if self._update_job:
            self.after_cancel(self._update_job)
        
        self.stopwatch.reset()
        self.time_var.set("0.000")
        self.time_label.configure(text_color="white")
        
        # Restart update loop
        self.start_update_loop()
    
    def destroy(self):
        """Clean up when widget is destroyed"""
        if self._update_job:
            self.after_cancel(self._update_job)
        self.remove_key_bindings()
        super().destroy()
