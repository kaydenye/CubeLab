#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/algorithm_details.py

import customtkinter as ctk
from classes.algorithm import Algorithm
from .components import TagChip, FONT

class AlgorithmDetails(ctk.CTkFrame):    
    def __init__(self, parent, **kwargs):
        """
        Function: Initialise the algorithm details component
        Input: parent (CTk widget), **kwargs
        Outputs: None
        """
        super().__init__(parent, fg_color="#222326", corner_radius=0, **kwargs)
        
        self.algorithm_service = Algorithm()
        
        self.name_var = ctk.StringVar(value="")
        self.notation_var = ctk.StringVar(value="")
        self.feedback_var = ctk.StringVar(value="")
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        Function: Setup UI for algorithm details display
        Input: None
        Outputs: None
        """
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
    
    # name: str or None, algorithm name to display (str for lookup, None for reset)
    # Returns: None
    def show_algorithm(self, name):
        """
        Function: Display algorithm details by name
        Input: name (str)
        Outputs: None (updates display with algorithm details)
        """
        if name is None:
            # No algorithm selected - show default state
            self.name_var.set("No Algorithm Selected")
            self.notation_var.set("")
            self.feedback_var.set("Select an algorithm to view details")
            self._clear_tags_display()
            return
            
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

    def _clear_tags_display(self):
        """Clear the tags display"""
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
    
    # tags: list, list of tag strings (list for multiple tags)
    # Returns: None
    def _update_tags_display(self, tags):
        """Update the tags display (max 10 tags)"""
        # Clear existing tags
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        
        if not tags:
            no_tags_label = ctk.CTkLabel(self.tags_frame, text="—", text_color="gray")
            no_tags_label.pack(anchor="center")
            return
        
        # Create container for tags
        tag_container = ctk.CTkFrame(self.tags_frame, fg_color="transparent")
        tag_container.pack(anchor="center")
        
        # Show all tags with wrapping to new lines (max 10)
        current_row = ctk.CTkFrame(tag_container, fg_color="transparent")
        current_row.pack(anchor="center", pady=2)
        
        current_width = 0
        max_width = 400  # Approximate max width before wrapping
        
        # Limit to 10 tags maximum
        display_tags = tags[:10]
        
        for tag in display_tags:
            tag_chip = TagChip(current_row, tag)
            tag_chip.update_idletasks()
            tag_width = tag_chip.winfo_reqwidth() + 8  # Include padding
            
            # If adding this tag would exceed max width, start new row
            if current_width + tag_width > max_width and current_width > 0:
                current_row = ctk.CTkFrame(tag_container, fg_color="transparent")
                current_row.pack(anchor="center", pady=2)
                current_width = 0
            
            tag_chip.pack(side="left", padx=(0, 8), pady=2)
            current_width += tag_width
    
    def clear(self):
        """Clear the details display"""
        self.name_var.set("")
        self.notation_var.set("")
        self.feedback_var.set("")
        
        # Clear tags
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
    
    # message: str, feedback message to display (str for UI)
    # Returns: None
    def set_feedback(self, message):
        """Set feedback message"""
        self.feedback_var.set(message)
