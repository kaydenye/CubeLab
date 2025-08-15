#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/modals.py

import customtkinter as ctk
from classes.algorithm import Algorithm
from .components import FONT

class AddAlgorithmModal:
    """Modal for adding new algorithms"""
    
    def __init__(self, parent, on_success=None):
        self.parent = parent
        self.on_success = on_success
        self.dialog = None
    
    def show(self):
        """Show the modal"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Add Algorithm")
        self.dialog.geometry("675x450")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame with border
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
            placeholder_text="Notation"
        )
        self.notation_entry.pack(anchor="w", pady=(0, 15))
        
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
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(side="bottom", anchor="se", padx=20, pady=20)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=self.cancel, width=100)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = ctk.CTkButton(btn_frame, text="Save", command=self.save, width=100)
        save_btn.pack(side="right", padx=(0, 10))
    
    def save(self):
        """Save the algorithm"""
        name = self.name_entry.get().strip()
        notation = self.notation_entry.get().strip()
        tags_raw = self.tags_entry.get().strip()
        
        if not name or not notation:
            self.message_var.set("Name and notation are required.")
            return
        
        # Check if algorithm already exists
        from classes.algorithm import Algorithm
        service = Algorithm()
        if service.algorithm_exists(name):
            self.message_var.set("Name already exists.")
            return
        
        # Parse tags
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        
        # Create and save algorithm
        try:
            algorithm = Algorithm(name, notation, tags)
            algorithm.save_to_db()
            
            if self.on_success:
                self.on_success(f"Added '{name}'.")
            
            self.dialog.destroy()
        except Exception as e:
            self.message_var.set(f"Error: {e}")
    
    def cancel(self):
        """Cancel and close modal"""
        self.dialog.destroy()

class LoginModal:
    """Modal for user login/registration"""
    
    def __init__(self, parent, on_success=None):
        self.parent = parent
        self.on_success = on_success
        self.dialog = None
    
    def show(self):
        """Show the login modal"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Login / Register")
        self.dialog.geometry("400x300")
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
        
        # Title
        title_label = ctk.CTkLabel(
            modal_frame,
            text="Login / Register",
            font=(FONT, 24, "bold")
        )
        title_label.pack(pady=20)
        
        # Form fields
        self.username_entry = ctk.CTkEntry(
            modal_frame,
            placeholder_text="Username",
            width=280
        )
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(
            modal_frame,
            placeholder_text="Password",
            width=280,
            show="*"
        )
        self.password_entry.pack(pady=10)
        
        # Message label
        self.message_var = ctk.StringVar(value="")
        message_label = ctk.CTkLabel(modal_frame, textvariable=self.message_var, text_color="red")
        message_label.pack(pady=10)
        
        # Buttons
        login_btn = ctk.CTkButton(modal_frame, text="Login", command=self.login, width=100)
        login_btn.pack(pady=10)
        
        register_btn = ctk.CTkButton(modal_frame, text="Register", command=self.register, width=100)
        register_btn.pack(pady=10)
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.message_var.set("Username and password are required.")
            return
        
        # Simple authentication (you can enhance this)
        if username == "admin" and password == "admin":
            self.message_var.set("Login successful!")
            if self.on_success:
                self.on_success("Login successful!")
            self.dialog.destroy()
        else:
            self.message_var.set("Invalid credentials.")
    
    def register(self):
        """Handle registration"""
        self.message_var.set("Registration not implemented.")
