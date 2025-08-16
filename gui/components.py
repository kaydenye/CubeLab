#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/components.py

import customtkinter as ctk

FONT = "Rethink Sans"

class SearchBar(ctk.CTkFrame):
    
    # parent: CTk widget, parent container for search bar (CTk widget for UI)
    # on_search_change: function or None, callback for search changes (function for event)
    # **kwargs: dict, extra options for CTkFrame
    # Returns: None
    def __init__(self, parent, on_search_change=None, **kwargs):
        """
        Function: Initialise the search bar component
        Input: parent (CTk widget), on_search_change (callback function), **kwargs
        Outputs: None
        """
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
        
        # Bind escape key to unfocus the search bar
        self.search_entry.bind("<Escape>", self._on_escape)
        
        # Bind click events to the parent frame to unfocus when clicking outside
        self._setup_focus_handling()

    def _setup_focus_handling(self):
        """Setup focus handling for clicking outside the search bar"""
        # event: event object, click event (object for event binding)
        # Returns: None
        def lose_focus(event):
            # Check if the click was outside the search bar
            if event.widget != self.search_entry and not str(event.widget).startswith(str(self.search_entry)):
                # Move focus to the main window
                top_level = self.winfo_toplevel()
                top_level.focus_set()

        top_level = self.winfo_toplevel()
        top_level.bind("<Button-1>", lose_focus, add="+")

    # event: event object, key event (object for event binding)
    # Returns: None
    def _on_escape(self, event):
        """Handle escape key to unfocus"""
        top_level = self.winfo_toplevel()
        top_level.focus_set() # Move focus away from the search entry

    # event: event object or None, key event (object for event binding)
    # Returns: None
    def _on_change(self, event=None):
        """
        Function: Handle for when the user updates the search bar input
        Input: event (optional object)
        Outputs: None (calls search change)
        """
        if self.on_search_change:
            self.on_search_change(self.get_query())
    
    def get_query(self):
        """
        Function: Get the current search query text
        Input: None
        Outputs: str (lowercase search query to match with algorithm list)
        """
        return self.search_entry.get().lower()

    def clear(self):
        """
        Function: Clear the search entry field
        Input: None
        Outputs: None
        """
        self.search_entry.delete(0, "end")

class FilterButton(ctk.CTkButton):
    
    # parent: CTk widget, parent container for button (CTk widget for UI)
    # on_filter_click: function or None, callback for filter click (function for event)
    # **kwargs: dict, extra options for CTkButton
    # Returns: None
    def __init__(self, parent, on_filter_click=None, **kwargs):
        """
        Function: Initialise the filter button component
        Input: parent (CTk widget), on_filter_click (callback function), **kwargs
        Outputs: None
        """
        super().__init__(parent, text="Filter", width=90, **kwargs)
        
        if on_filter_click:
            self.configure(command=on_filter_click)

class TagChip(ctk.CTkLabel):
    
    # parent: CTk widget, parent container for tag (CTk widget for UI)
    # tag_text: str, text to display in tag (str for label)
    # **kwargs: dict, extra options for CTkLabel
    # Returns: None
    def __init__(self, parent, tag_text, **kwargs):
        """
        Function: Initialise a tag chip display component
        Input: parent (CTk widget), tag_text (str), **kwargs
        Outputs: None
        """
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
    
    # parent: CTk widget, parent container for list item (CTk widget for UI)
    # name: str, algorithm name (str for label)
    # on_click: function or None, callback for click (function for event)
    # show_remove: bool, show remove button (bool for UI)
    # on_remove: function or None, callback for remove (function for event)
    # show_count: bool, show count label (bool for UI)
    # count: int, number of times (int for display)
    # **kwargs: dict, extra options for CTkFrame
    # Returns: None
    def __init__(self, parent, name, on_click=None, 
                 show_remove=True, on_remove=None,
                 show_count=False, count=0, **kwargs):
        """
        Function: Initialise an algorithm list item component
        Input: parent (CTk widget), name (str), on_click (callback), show_remove (bool), on_remove (callback), show_count (bool), count (int), **kwargs
        Outputs: None
        """
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
            remove_button = ctk.CTkButton(
                self,
                text="Remove",
                fg_color="red",
                hover_color="#aa0000",
                width=80,
                command=lambda: on_remove(name),
            )
            remove_button.pack(side="right")

class HeaderFrame(ctk.CTkFrame):
    
    # parent: CTk widget, parent container for header (CTk widget for UI)
    # title: str, header title (str for label)
    # show_back: bool, show back button (bool for UI)
    # on_back: function or None, callback for back (function for event)
    # show_dashboard: bool, show dashboard button (bool for UI)
    # on_dashboard: function or None, callback for dashboard (function for event)
    # on_exit: function or None, callback for exit (function for event)
    # **kwargs: dict, extra options for CTkFrame
    # Returns: None
    def __init__(self, parent, title="", show_back=False, 
                 on_back=None, show_dashboard=False,
                 on_dashboard=None, on_exit=None, **kwargs):
        """
        Function: Initialise the header frame component
        Input: parent (CTk widget), title (str), show_back (bool), on_back (callback), show_dashboard (bool), on_dashboard (callback), on_exit (callback), **kwargs
        Outputs: None
        """
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
