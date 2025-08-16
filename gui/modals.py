#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/modals.py

import customtkinter as ctk
from classes.algorithm import Algorithm
from .components import FONT

class AddAlgorithmModal:
    """Modal for adding new algorithms"""
    
    # parent: CTk widget, parent window for modal (CTk widget for UI)
    # on_success: function or None, callback after successful add (function for event)
    # Returns: None
    def __init__(self, parent, on_success=None):
        """
        Function: Initialise the Add Algorithm modal
        Input: parent (CTk widget), on_success (callback function)
        Outputs: None
        """
        self.parent = parent
        self.on_success = on_success
        self.dialog = None
    
    # No args. Shows the modal dialog for adding an algorithm.
    # Returns: None
    def show(self):
        """
        Function: Show the Add Algorithm modal dialog
        Input: None
        Outputs: None
        """
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Add Algorithm")
        self.dialog.geometry("675x450")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        modal_frame = ctk.CTkFrame(
            self.dialog,
            corner_radius=15,
            fg_color="#5A6E73",
            border_width=3,
            border_color="#5A6E73"
        )
        modal_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel
        left_panel = ctk.CTkFrame(
            modal_frame,
            fg_color="#33363D",
            corner_radius=0,
            width=337,
        )
        left_panel.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        left_panel.pack_propagate(False)
        
        # Right panel
        right_panel = ctk.CTkFrame(
            modal_frame,
            fg_color="#2D3033",
            corner_radius=0,
            width=338,
        )
        right_panel.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)
        right_panel.pack_propagate(False)
        
        # Content frame for left alignment
        content_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        content_frame.pack(anchor="w", padx=20, pady=20, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text="Add Algorithm",
            font=(FONT, 24, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 30))
        
        # Form fields
        self.name_entry = ctk.CTkEntry(
            content_frame,
            width=280,
            placeholder_text="Algorithm Name"
        )
        self.name_entry.pack(anchor="w", pady=(0, 15))
        
        self.notation_entry = ctk.CTkEntry(
            content_frame,
            width=280,
            placeholder_text="Notation (e.g., R U R' U')"
        )
        self.notation_entry.pack(anchor="w", pady=(0, 15))
        
        # Bind validation to notation entry
        self.notation_entry.bind("<KeyRelease>", self._validate_notation)
        
        self.tags_entry = ctk.CTkEntry(
            content_frame,
            width=280,
            placeholder_text="Tags (comma-separated)"
        )
        self.tags_entry.pack(anchor="w", pady=(0, 15))
        
        # Message label
        self.message_var = ctk.StringVar(value="")
        message_label = ctk.CTkLabel(content_frame, textvariable=self.message_var, text_color="red")
        message_label.pack(anchor="w", pady=(10, 5))
        
        # Buttons frame in right panel
        button_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        button_frame.pack(side="bottom", anchor="se", padx=20, pady=20)
        
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, width=100, fg_color="#bc2626", hover_color="#a01e1e")
        cancel_button.pack(side="right", padx=(10, 0))

        save_button = ctk.CTkButton(button_frame, text="Save", command=self.save, width=100, fg_color="#26BC53", hover_color="#1e9c43")
        save_button.pack(side="right", padx=(0, 10))
    
    # event: event object or None, event from key press (object for event binding)
    # Returns: bool or None (True if valid, False if not)
    def _validate_notation(self, event=None):
        """
        Function: Validate notation input and check if valid
        Input: event (optional event object)
        Outputs: Boolean (True if valid, False otherwise) or None
        """
        notation = self.notation_entry.get().strip()
        
        if event is not None:
            if not notation:
                self.message_var.set("")
                return
        
        if not notation:
            return False
        
        valid_moves = {
            'U', 'D', 'L', 'R', 'F', 'B', # base moves
            'U2', 'D2', 'L2', 'R2', 'F2', 'B2', # 2 moves
            "U'", "D'", "L'", "R'", "F'", "B'", # prime moves
            "U2'", "D2'", "L2'", "R2'", "F2'", "B2'" # 2 prime moves
        }
        
        # Split by spaces and check each move (convert to uppercase for validation)
        moves = notation.split()
        invalid_moves = []
        
        for move in moves:
            if move.upper() not in valid_moves:
                invalid_moves.append(move)
        
        if event is not None:
            if invalid_moves:
                self.message_var.set(f"Invalid moves: {', '.join(invalid_moves)}")
            else:
                self.message_var.set("")
            return
        
        return len(invalid_moves) == 0

    def save(self):
        """
        Function: Save the new algorithm to the database
        Input: None (uses form entry values)
        Outputs: None (success or displays error message)
        """
        name = self.name_entry.get().strip()
        notation = self.notation_entry.get().strip()
        tags_raw = self.tags_entry.get().strip()
        
        if not name or not notation:
            self.message_var.set("Name and notation are required.")
            return
        
        if not self._validate_notation():
            self.message_var.set("Invalid notation. Must use U, D, L, R, F, B with modifiers 2 and/or ' (separated by spaces)")
            return
        
        # Check if algorithm already exists
        from classes.algorithm import Algorithm
        service = Algorithm()
        if service.algorithm_exists(name):
            self.message_var.set("Name already exists.")
            return
        
        # Parse tags
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        
        # Convert notation to uppercase for consistency
        notation_uppercase = ' '.join(move.upper() for move in notation.split())
        
        # Create and save algorithm
        try:
            algorithm = Algorithm(name, notation_uppercase, tags)
            algorithm.save_to_db()
            
            if self.on_success:
                self.on_success(f"Added '{name}'.")
            
            self.dialog.destroy()
        except Exception as e:
            self.message_var.set(f"Error: {e}")

    def cancel(self):
        """
        Function: Cancel and close the modal dialog
        Input: None
        Outputs: None
        """
        self.dialog.destroy()