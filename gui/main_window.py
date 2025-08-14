#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/main_window.py

import customtkinter as ctk
import os
from PIL import Image
from .components import HeaderFrame, FONT
from .algorithm_list import AlgorithmList
from .algorithm_details import AlgorithmDetails
from .stopwatch_widget import StopwatchWidget
from .modals import AddAlgorithmModal, LoginModal
from .dashboard import Dashboard

class MainWindow:
    """Main application window"""
    
    def __init__(self, parent_frame: ctk.CTkFrame):
        self.parent_frame = parent_frame
        self.current_view = "main"
        
        # Components
        self.algorithm_list = None
        self.algorithm_details = None
        self.stopwatch_widget = None
        self.dashboard = None
        
        self.draw_main_ui()
    
    def clear_parent_frame(self):
        """Clear all widgets from parent frame"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
    
    def draw_main_ui(self):
        """Draw the main UI"""
        self.clear_parent_frame()
        self.current_view = "main"
        
        # Configure parent frame grid
        self.parent_frame.grid_rowconfigure(0, weight=0)  # header
        self.parent_frame.grid_rowconfigure(1, weight=1)  # content
        self.parent_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = HeaderFrame(
            self.parent_frame,
            show_dashboard=True,
            on_dashboard=self.show_dashboard,
            on_exit=self.exit_app
        )
        self.header.grid(row=0, column=0, sticky="ew")
        
        # Add icon to header - but don't let it cover the buttons
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "../icon.ico")
            icon_image = ctk.CTkImage(light_image=Image.open(icon_path), size=(64, 64))
            icon_label = ctk.CTkLabel(self.header, image=icon_image, text="", fg_color="transparent")
            icon_label.place(relx=0.5, rely=0.5, anchor="center")  # Center the icon instead of using grid
        except Exception:
            pass
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self.parent_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)  # details
        self.content_frame.grid_columnconfigure(1, weight=0)  # list
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Algorithm details (left side)
        self.algorithm_details = AlgorithmDetails(self.content_frame)
        self.algorithm_details.grid(row=0, column=0, sticky="nsew")
        
        # Details content with stopwatch
        details_content = ctk.CTkFrame(self.algorithm_details.content_frame, fg_color="transparent")
        details_content.pack(side="bottom", fill="x", pady=(20, 0))
        
        # Stopwatch widget (bottom of details)
        self.stopwatch_widget = StopwatchWidget(details_content)
        self.stopwatch_widget.pack(side="bottom", fill="x")
        
        # Algorithm list (right side)
        self.algorithm_list = AlgorithmList(
            self.content_frame,
            on_algorithm_select=self.on_algorithm_select,
            show_remove=True,
            show_add=True,
            show_count=False
        )
        self.algorithm_list.grid(row=0, column=1, sticky="nsew")
        
        # Connect add button
        self.algorithm_list.on_add_click = self.show_add_algorithm_modal
    
    def on_algorithm_select(self, algorithm_name: str):
        """Handle algorithm selection"""
        self.algorithm_details.show_algorithm(algorithm_name)
        self.stopwatch_widget.set_algorithm(algorithm_name)
    
    def show_add_algorithm_modal(self):
        """Show add algorithm modal"""
        # Disable stopwatch keys
        if self.stopwatch_widget:
            self.stopwatch_widget.remove_key_bindings()
        
        modal = AddAlgorithmModal(
            self.parent_frame.winfo_toplevel(),
            on_success=self.on_algorithm_added
        )
        modal.show()
    
    def on_algorithm_added(self, message: str):
        """Handle successful algorithm addition"""
        self.algorithm_details.set_feedback(message)
        self.algorithm_list.refresh()
        
        # Re-enable stopwatch keys
        if self.stopwatch_widget:
            self.stopwatch_widget.setup_key_bindings()
    
    def show_dashboard(self):
        """Show dashboard view"""
        if self.stopwatch_widget:
            self.stopwatch_widget.remove_key_bindings()
        
        self.current_view = "dashboard"
        self.clear_parent_frame()
        
        # Create dashboard
        self.dashboard = Dashboard(
            self.parent_frame,
            on_back=self.draw_main_ui
        )
    
    def exit_app(self):
        """Exit the application with proper cleanup"""
        try:
            # Clean up any matplotlib figures that might exist
            import matplotlib.pyplot as plt
            plt.close('all')
            
            # If we have a dashboard instance, clean it up
            if hasattr(self, 'dashboard'):
                try:
                    if hasattr(self.dashboard, 'bar_chart_card') and hasattr(self.dashboard.bar_chart_card, 'canvas'):
                        if self.dashboard.bar_chart_card.canvas:
                            self.dashboard.bar_chart_card.canvas.get_tk_widget().destroy()
                    if hasattr(self.dashboard, 'line_chart_card') and hasattr(self.dashboard.line_chart_card, 'canvas'):
                        if self.dashboard.line_chart_card.canvas:
                            self.dashboard.line_chart_card.canvas.get_tk_widget().destroy()
                except:
                    pass
                    
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            # Exit the application
            self.parent_frame.winfo_toplevel().destroy()

def create_algorithm_ui(parent_frame: ctk.CTkFrame):
    """Factory function for backward compatibility"""
    return MainWindow(parent_frame)
