#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/algorithm_details.py

import customtkinter as ctk
from typing import Optional
from classes.algorithm import Algorithm
from .components import TagChip, FONT

class AlgorithmDetails(ctk.CTkFrame):
    """Algorithm details display component"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#222326", corner_radius=0, **kwargs)
        
        self.algorithm_service = Algorithm()
        
        self.name_var = ctk.StringVar(value="")
        self.notation_var = ctk.StringVar(value="")
        self.feedback_var = ctk.StringVar(value="")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top section with algorithm info
        self.info_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.info_frame.pack(fill="x", pady=(0, 20))
        
        # Algorithm name
        self.name_label = ctk.CTkLabel(self.info_frame, textvariable=self.name_var, font=(FONT, 48, "bold"))
        self.name_label.pack(pady=5)
        
        # Notation
        self.notation_label = ctk.CTkLabel(self.info_frame, textvariable=self.notation_var, font=(FONT, 24))
        self.notation_label.pack()
        
        # Tags frame
        self.tags_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.tags_frame.pack(pady=5)
        
        # Feedback label
        self.feedback_label = ctk.CTkLabel(self.info_frame, textvariable=self.feedback_var)
        self.feedback_label.pack(pady=10)
    
    def show_algorithm(self, name: str):
        """Display algorithm details"""
        details = self.algorithm_service.get_algorithm_details(name)
        if not details:
            self.feedback_var.set(f"Could not load '{name}'.")
            return
        
        notation, tags = details
        
        # Update display
        self.name_var.set(name)
        self.notation_var.set(notation)
        self.feedback_var.set("")
        
        # Update tags
        self._update_tags_display(tags)
    
    def _update_tags_display(self, tags: list):
        """Update the tags display"""
        # Clear existing tags
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        
        if tags:
            tag_container = ctk.CTkFrame(self.tags_frame, fg_color="transparent")
            tag_container.pack(anchor="center")
            
            for tag in tags:
                tag_chip = TagChip(tag_container, tag)
                tag_chip.pack(side="left", padx=(0, 8), pady=2)
        else:
            no_tags_label = ctk.CTkLabel(self.tags_frame, text="—", text_color="gray")
            no_tags_label.pack(anchor="center")
    
    def clear(self):
        """Clear the details display"""
        self.name_var.set("")
        self.notation_var.set("")
        self.feedback_var.set("")
        
        # Clear tags
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
    
    def set_feedback(self, message: str):
        """Set feedback message"""
        self.feedback_var.set(message)
