#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/components.py

import customtkinter as ctk
from typing import Callable, Optional

FONT = "Rethink Sans"

class SearchBar(ctk.CTkFrame):
    
    def __init__(self, parent, on_search_change: Callable = None, **kwargs):
        kwargs.setdefault('fg_color', 'transparent')
        kwargs.setdefault('border_width', 0)
        super().__init__(parent, **kwargs)
        
        self.on_search_change = on_search_change
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Search...",
            height=35
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        if self.on_search_change:
            self.search_entry.bind("<KeyRelease>", self._on_change)
    
    def _on_change(self, event=None):
        if self.on_search_change:
            self.on_search_change(self.get_query())
    
    def get_query(self) -> str:
        return self.search_entry.get().lower()
    
    def clear(self):
        self.search_entry.delete(0, "end")

class FilterButton(ctk.CTkButton):
    
    def __init__(self, parent, on_filter_click: Callable = None, **kwargs):
        super().__init__(parent, text="Filter", width=90, **kwargs)
        
        if on_filter_click:
            self.configure(command=on_filter_click)

class TagChip(ctk.CTkLabel):
    
    def __init__(self, parent, tag_text: str, **kwargs):
        super().__init__(
            parent,
            text=tag_text,
            corner_radius=8,
            fg_color="#4A5568",
            text_color="white",
            padx=12,
            pady=6,
            **kwargs
        )

class AlgorithmListItem(ctk.CTkFrame):
    
    def __init__(self, parent, name: str, on_click: Callable = None, 
                 show_remove: bool = True, on_remove: Callable = None,
                 show_count: bool = False, count: int = 0, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.name_label = ctk.CTkLabel(self, text=name, cursor="hand2")
        self.name_label.pack(side="left", padx=(5, 10), pady=10)
        
        if on_click:
            self.bind("<Button-1>", lambda e: on_click(name))
            self.name_label.bind("<Button-1>", lambda e: on_click(name))
            self.configure(cursor="hand2")
        
        if show_count:
            count_label = ctk.CTkLabel(self, text=f"({count} times)", text_color="gray")
            count_label.pack(side="right", padx=(0, 10))
        
        if show_remove and on_remove:
            remove_btn = ctk.CTkButton(
                self,
                text="Remove",
                fg_color="red",
                hover_color="#aa0000",
                width=80,
                command=lambda: on_remove(name),
            )
            remove_btn.pack(side="right")

class HeaderFrame(ctk.CTkFrame):
    
    def __init__(self, parent, title: str = "", show_back: bool = False, 
                 on_back: Callable = None, show_dashboard: bool = False,
                 on_dashboard: Callable = None, on_exit: Callable = None, **kwargs):
        super().__init__(parent, height=80, **kwargs)
        
        self._fg_color = "#353A40"
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        if title:
            title_label = ctk.CTkLabel(self, text=title, font=(FONT, 24, "bold"))
            title_label.grid(row=0, column=0, sticky="nsew")
        
        if show_dashboard and on_dashboard:
            dashboard_button = ctk.CTkButton(self, text="Dashboard", width=120, command=on_dashboard)
            dashboard_button.place(relx=0.0, rely=0.5, anchor="w", x=20)
        
        if show_back and on_back:
            back_button = ctk.CTkButton(self, text="← Back", width=140, command=on_back)
            # Position back button based on whether dashboard button is shown
            back_x = 160 if (show_dashboard and on_dashboard) else 20
            back_button.place(relx=0.0, rely=0.5, anchor="w", x=back_x)
        
        if on_exit:
            exit_button = ctk.CTkButton(self, text="Exit", width=80, command=on_exit)
            exit_button.place(relx=1.0, rely=0.5, anchor="e", x=-20)
