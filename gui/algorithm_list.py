#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/algorithm_list.py

import customtkinter as ctk
from typing import Callable, Optional, Set
from classes.algorithm_util import AlgorithmUtil
from classes.timer_util import TimerUtil, TimerUtil
from .components import SearchBar, FilterButton, AlgorithmListItem, FONT

class AlgorithmList(ctk.CTkFrame):    
    def __init__(self, parent, on_algorithm_select: Callable = None, 
                 show_remove: bool = True, show_add: bool = True,
                 show_count: bool = False, **kwargs):
        super().__init__(parent, width=360, **kwargs)

        self.algorithm_util = AlgorithmUtil()
        self.timer_util = TimerUtil()
        self.on_algorithm_select = on_algorithm_select
        self.show_remove = show_remove
        self.show_add = show_add
        self.show_count = show_count
        
        # State
        self.filter_tags: Set[str] = set()
        self.sort_order = "asc"
        
        self.setup_ui()
        self.load_algorithms()
    
    def setup_ui(self):
        """Setup the UI components"""
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # search row
        self.grid_rowconfigure(1, weight=1)  # list
        self.grid_rowconfigure(2, weight=0)  # add button
        
        # Search and filter row
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=0)
        
        # Search bar
        self.search_bar = SearchBar(search_frame, on_search_change=self.on_search_change, fg_color="transparent")
        self.search_bar.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        
        # Filter button
        self.filter_button = FilterButton(search_frame, on_filter_click=self.open_filter_dialog)
        self.filter_button.grid(row=0, column=1, sticky="e")
        
        # Scrollable list
        self.scrollable_list = ctk.CTkScrollableFrame(self, fg_color="#33363D", corner_radius=0)
        self.scrollable_list.grid(row=1, column=0, sticky="nsew")
        
        # Add button
        if self.show_add:
            self.add_button = ctk.CTkButton(self, text="+", width=40, command=self._on_add_click)
            self.add_button.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
    
    def on_search_change(self, query: str):
        """Handle search query change"""
        self.load_algorithms(query)
    
    def load_algorithms(self, search_query: str = ""):
        """Load and display algorithms"""
        # Clear current list
        for widget in self.scrollable_list.winfo_children():
            widget.destroy()
        
        # Get algorithms
        algorithms = self.algorithm_util.get_algorithms_with_filters(
            search_query, self.filter_tags, self.sort_order
        )
        
        # Create list items
        for name in algorithms:
            count = 0
            if self.show_count:
                count = self.timer_util.get_time_count(name)
            
            item = AlgorithmListItem(
                self.scrollable_list,
                name=name,
                on_click=self._on_algorithm_click,
                show_remove=self.show_remove,
                on_remove=self._on_algorithm_remove,
                show_count=self.show_count,
                count=count
            )
            item.pack(fill="x", pady=2, padx=5)
        
        # Auto-select first if no search and we have items
        if not search_query and algorithms and self.on_algorithm_select:
            self.on_algorithm_select(algorithms[0])
    
    def _on_algorithm_click(self, name: str):
        """Handle algorithm selection"""
        if self.on_algorithm_select:
            self.on_algorithm_select(name)
    
    def _on_algorithm_remove(self, name: str):
        """Handle algorithm removal"""
        if self.algorithm_util.remove_algorithm(name):
            self.refresh()
            # Emit removal signal if needed
    
    def _on_add_click(self):
        """Internal add button click handler"""
        if hasattr(self, 'on_add_click') and callable(self.on_add_click):
            self.on_add_click()
    
    def on_add_click(self):
        """Handle add button click - to be overridden"""
        pass
    
    def open_filter_dialog(self):
        """Open filter dialog"""
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("Filter & Sort")
        dlg.geometry("675x450")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()
        
        # Main frame with border
        modal_frame = ctk.CTkFrame(
            dlg,
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
        
        # Content frame for left panel
        content_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        content_frame.pack(anchor="w", padx=20, pady=20, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text="Filter & Sort",
            font=(FONT, 24, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 30))
        
        # Tags section
        ctk.CTkLabel(content_frame, text="Filter by tags", font=(FONT, 16, "bold")).pack(anchor="w", pady=(0, 8))
        tags_frame = ctk.CTkScrollableFrame(content_frame, height=220, fg_color="transparent")
        tags_frame.pack(fill="x", pady=(0, 12))
        
        tag_vars = {}
        tags = self.algorithm_util.get_all_tags()
        if tags:
            for tag in tags:
                var = ctk.BooleanVar(value=(tag in self.filter_tags))
                cb = ctk.CTkCheckBox(tags_frame, text=tag, variable=var)
                cb.pack(anchor="w", pady=2)
                tag_vars[tag] = var
        else:
            ctk.CTkLabel(tags_frame, text="No tags found.", text_color="gray").pack(anchor="w", pady=4)
        
        # Sort section in right panel
        sort_content_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        sort_content_frame.pack(anchor="w", padx=20, pady=20, fill="both", expand=True)
        
        ctk.CTkLabel(sort_content_frame, text="Sort", font=(FONT, 16, "bold")).pack(anchor="w", pady=(0, 6))
        sort_values = ["A-Z", "Z-A"]
        current_sort = "A-Z" if self.sort_order == "asc" else "Z-A"
        sort_menu = ctk.CTkOptionMenu(sort_content_frame, values=sort_values, width=280)
        sort_menu.set(current_sort)
        sort_menu.pack(anchor="w")
        
        # Buttons frame in right panel
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(side="bottom", anchor="se", padx=20, pady=20)
        
        def apply_and_close():
            self.filter_tags = {name for name, var in tag_vars.items() if var.get()}
            sel = sort_menu.get()
            self.sort_order = "asc" if sel == "A-Z" else "desc"
            self.refresh()
            dlg.destroy()
        
        def clear_and_close():
            self.filter_tags = set()
            self.sort_order = "asc"
            self.refresh()
            dlg.destroy()
        
        clear_btn = ctk.CTkButton(btn_frame, text="Clear", command=clear_and_close, width=100)
        clear_btn.pack(side="right", padx=(10, 0))
        
        apply_btn = ctk.CTkButton(btn_frame, text="Apply", command=apply_and_close, width=100)
        apply_btn.pack(side="right", padx=(0, 10))
    
    def refresh(self):
        """Refresh the algorithm list"""
        query = self.search_bar.get_query() if hasattr(self.search_bar, 'get_query') else ""
        self.load_algorithms(query)
