import customtkinter as ctk
import sqlite3
import os
from PIL import Image
from classes.algorithm import Algorithm
import time
from datetime import datetime

FONT = "Rethink Sans"

class AlgorithmUI:
    def __init__(self, parent_frame: ctk.CTkFrame):
        self.parent_frame = parent_frame

        # Filters and sorting state
        self.filter_tags = set()
        self.sort_order = "asc"  # "asc" or "desc"
        # Dashboard filters and sorting state
        self.dashboard_filter_tags = set()
        self.dashboard_sort_order = "asc"  # "asc" or "desc"

        # UI state vars
        self.name_var = ctk.StringVar(value="")
        self.notation_var = ctk.StringVar(value="")
        self.tags_var = ctk.StringVar(value="")
        self.feedback_var = ctk.StringVar(value="")

        # Stopwatch state
        self.selected_algorithm = None
        self._timer_running = False
        self._elapsed_ms = 0
        self._last_perf = None
        self._after_job = None
        self.stopwatch_target_var = ctk.StringVar(value="No algorithm selected")
        self.stopwatch_time_var = ctk.StringVar(value="0.000")
        self.stopwatch_state_var = ctk.StringVar(value="Ready")
        
        # Stopwatch timing variables (from poop.py)
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.hold_start = None
        self.ready = False

        self.draw_main_ui()

    def clear_parent_frame(self):
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

    def draw_main_ui(self):
        self.clear_parent_frame()

        # Header
        self.header = ctk.CTkFrame(self.parent_frame, height=80)
        self.header._fg_color = "#353A40"
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_rowconfigure(0, weight=1)

        icon_path = os.path.join(os.path.dirname(__file__), "../icon.ico")
        icon_image = ctk.CTkImage(light_image=Image.open(icon_path), size=(64, 64))
        icon_label = ctk.CTkLabel(self.header, image=icon_image, text="")
        icon_label.grid(row=0, column=0, sticky="nsew")

        exit_button = ctk.CTkButton(self.header, text="Exit", width=80, command=self.parent_frame.winfo_toplevel().destroy)
        exit_button.place(relx=1.0, rely=0.5, anchor="e", x=-20)

        # Add Dashboard button on the right side of the header
        try:
            dashboard_button = ctk.CTkButton(self.header, text="Dashboard", width=120, command=self.show_dashboard)
            # Place it left of the Exit button
            dashboard_button.place(relx=1.0, rely=0.5, anchor="e", x=-140)  # adjust if button widths change
        except Exception:
            pass

        # Content frame
        self.content_frame = ctk.CTkFrame(self.parent_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.parent_frame.grid_rowconfigure(1, weight=1)
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=0)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Details frame
        self.details_frame = ctk.CTkFrame(self.content_frame, fg_color="#222326", corner_radius=0)
        self.details_frame.grid(row=0, column=0, sticky="nsew")

        # List frame
        self.list_frame = ctk.CTkFrame(self.content_frame, width=360)
        self.list_frame.grid(row=0, column=1, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)  # search
        self.list_frame.grid_columnconfigure(1, weight=0)  # filter btn
        self.list_frame.grid_rowconfigure(0, weight=0)     # search/filter row
        self.list_frame.grid_rowconfigure(1, weight=1)     # scrollable list
        self.list_frame.grid_rowconfigure(2, weight=0)     # add button
        self.list_frame.grid_propagate(False)

        # Search bar
        self.search_entry = ctk.CTkEntry(
            self.list_frame,
            placeholder_text="Search...",
            height=35
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(10, 6), pady=(10, 5))
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        # Filter button next to search
        self.filter_btn = ctk.CTkButton(
            self.list_frame,
            text="Filter",
            width=90,
            command=self.open_filter_dialog
        )
        self.filter_btn.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=(10, 5))

        # Scrollable list
        self.scrollable_list = ctk.CTkScrollableFrame(self.list_frame, fg_color="#33363D", corner_radius=0)
        self.scrollable_list.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Add button
        self.add_button = ctk.CTkButton(self.list_frame, text="+", width=40, command=self.show_add_algorithm_modal)
        self.add_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))

        # Labels in details frame
        self.name_label = ctk.CTkLabel(self.details_frame, textvariable=self.name_var, font=(FONT, 48, "bold"))
        self.name_label.pack(pady=5)

        self.notation_label = ctk.CTkLabel(self.details_frame, textvariable=self.notation_var, font=(FONT, 24))
        self.notation_label.pack()

        # Frame for individual tag indicators
        self.tags_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.tags_frame.pack(pady=5)

        # Stopwatch section
        stopwatch_container = ctk.CTkFrame(self.details_frame, fg_color="#2A2D32", corner_radius=15)
        stopwatch_container.pack(pady=(20, 10), padx=20, fill="x")

        # Stopwatch title
        stopwatch_title = ctk.CTkLabel(stopwatch_container, text="Stopwatch", font=(FONT, 24, "bold"))
        stopwatch_title.pack(pady=(15, 5))

        # Algorithm target
        self.stopwatch_target_label = ctk.CTkLabel(stopwatch_container, textvariable=self.stopwatch_target_var, font=(FONT, 16), text_color="gray")
        self.stopwatch_target_label.pack(pady=5)

        # Timer display
        self.stopwatch_time_label = ctk.CTkLabel(stopwatch_container, textvariable=self.stopwatch_time_var, font=(FONT, 48, "bold"), text_color="white")
        self.stopwatch_time_label.pack(pady=10)

        # State display
        self.stopwatch_state_label = ctk.CTkLabel(stopwatch_container, textvariable=self.stopwatch_state_var, font=(FONT, 14), text_color="gray")
        self.stopwatch_state_label.pack(pady=(0, 15))

        # Instructions
        instructions = ctk.CTkLabel(stopwatch_container, text="Hold SPACE for 0.5s to start • Press SPACE to stop", font=(FONT, 12), text_color="gray")
        instructions.pack(pady=(0, 15))

        self.feedback_label = ctk.CTkLabel(self.details_frame, textvariable=self.feedback_var)
        self.feedback_label.pack(pady=10)

        # Enable keyboard controls
        self.enable_stopwatch_keys(True)

        # Start the display update loop
        self.update_stopwatch_display()

        # Load initial data
        self.load_algorithm_list()

    def on_search_change(self, event=None):
        query = self.search_entry.get().lower()
        self.load_algorithm_list(query)

    def load_algorithm_list(self, search_query: str = ""):
        # Clear list
        for w in self.scrollable_list.winfo_children():
            w.destroy()

        order_sql = "ASC" if self.sort_order == "asc" else "DESC"

        with sqlite3.connect(Algorithm.db_path) as conn:
            cur = conn.cursor()

            tags = list(self.filter_tags)
            has_tags = len(tags) > 0
            has_search = bool(search_query)

            if has_tags:
                # Filter algorithms that have ANY of the selected tags
                placeholders = ",".join(["?"] * len(tags))
                where_parts = [f"t.name IN ({placeholders})"]
                params = tags[:]

                if has_search:
                    where_parts.append("(LOWER(a.name) LIKE ? OR LOWER(a.notation) LIKE ?)")
                    params.extend([f"%{search_query}%", f"%{search_query}%"])

                where_clause = " AND ".join(where_parts)
                sql = f"""
                    SELECT DISTINCT a.name
                    FROM algorithms a
                    JOIN algorithm_tags at ON at.algorithm_id = a.id
                    JOIN tags t ON t.id = at.tag_id
                    WHERE {where_clause}
                    ORDER BY a.name COLLATE NOCASE {order_sql}
                """
                cur.execute(sql, params)
                names = [r[0] for r in cur.fetchall()]
            else:
                if has_search:
                    cur.execute(
                        f"""
                        SELECT a.name
                        FROM algorithms a
                        WHERE LOWER(a.name) LIKE ? OR LOWER(a.notation) LIKE ?
                        ORDER BY a.name COLLATE NOCASE {order_sql}
                        """,
                        (f"%{search_query}%", f"%{search_query}%")
                    )
                    names = [r[0] for r in cur.fetchall()]
                else:
                    cur.execute(f"SELECT name FROM algorithms ORDER BY name COLLATE NOCASE {order_sql}")
                    names = [r[0] for r in cur.fetchall()]

        # Build rows
        for name in names:
            row = ctk.CTkFrame(self.scrollable_list)
            row.pack(fill="x", pady=2, padx=5)

            lbl = ctk.CTkLabel(row, text=name, cursor="hand2")
            lbl.pack(side="left", padx=(5, 10))

            row.bind("<Button-1>", lambda e, n=name: self.show_details(n))
            lbl.bind("<Button-1>", lambda e, n=name: self.show_details(n))
            row.configure(cursor="hand2")

            del_btn = ctk.CTkButton(
                row,
                text="Remove",
                fg_color="red",
                hover_color="#aa0000",
                width=80,
                command=lambda n=name: self.remove_algorithm(n),
            )
            del_btn.pack(side="right")

        # Auto-select the first algorithm if nothing selected
        if not search_query and names:
            self.show_details(names[0])

    def open_filter_dialog(self):
        """Open dialog to choose tag filters and sort order (A–Z / Z–A)."""
        dlg = ctk.CTkToplevel(self.parent_frame.winfo_toplevel())
        dlg.title("Filter & Sort")
        dlg.geometry("380x440")
        dlg.transient(self.parent_frame.winfo_toplevel())
        dlg.grab_set()

        root = ctk.CTkFrame(dlg)
        root.pack(fill="both", expand=True, padx=16, pady=16)

        # Tags section
        ctk.CTkLabel(root, text="Filter by tags", font=(FONT, 16, "bold")).pack(anchor="w", pady=(0, 8))
        tags_frame = ctk.CTkScrollableFrame(root, height=220, fg_color="transparent")
        tags_frame.pack(fill="x", pady=(0, 12))

        tag_vars = {}
        tags = self.get_all_tags()
        if tags:
            for t in tags:
                var = ctk.BooleanVar(value=(t in self.filter_tags))
                cb = ctk.CTkCheckBox(tags_frame, text=t, variable=var)
                cb.pack(anchor="w", pady=2)
                tag_vars[t] = var
        else:
            ctk.CTkLabel(tags_frame, text="No tags found.", text_color="gray").pack(anchor="w", pady=4)

        # Sort section
        ctk.CTkLabel(root, text="Sort", font=(FONT, 16, "bold")).pack(anchor="w", pady=(8, 6))
        sort_values = ["A-Z", "Z-A"]
        current_sort = "A-Z" if self.sort_order == "asc" else "Z-A"
        sort_menu = ctk.CTkOptionMenu(root, values=sort_values)
        sort_menu.set(current_sort)
        sort_menu.pack(anchor="w")

        # Buttons
        btns = ctk.CTkFrame(root, fg_color="transparent")
        btns.pack(fill="x", pady=(18, 0))

        def apply_and_close():
            self.filter_tags = {name for name, v in tag_vars.items() if v.get()}
            sel = sort_menu.get()
            self.sort_order = "asc" if sel == "A-Z" else "desc"
            q = self.search_entry.get().lower() if hasattr(self, "search_entry") else ""
            self.load_algorithm_list(q)
            dlg.destroy()

        def clear_and_close():
            self.filter_tags = set()
            self.sort_order = "asc"
            q = self.search_entry.get().lower() if hasattr(self, "search_entry") else ""
            self.load_algorithm_list(q)
            dlg.destroy()

        ctk.CTkButton(btns, text="Clear", command=clear_and_close, width=100).pack(side="left")
        ctk.CTkButton(btns, text="Apply", command=apply_and_close, width=100).pack(side="right")

    def get_all_tags(self):
        """Return list of all tag names."""
        try:
            with sqlite3.connect(Algorithm.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM tags ORDER BY name COLLATE NOCASE ASC")
                return [r[0] for r in cur.fetchall()]
        except Exception:
            return []

    def show_details(self, name: str):
        with sqlite3.connect(Algorithm.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT notation FROM algorithms WHERE name = ?", (name,))
            notation_row = cur.fetchone()
            if not notation_row:
                self.feedback_var.set(f"Could not load '{name}'.")
                return
            notation = notation_row[0]

            cur.execute(
                """
                SELECT tags.name FROM tags
                JOIN algorithm_tags ON tags.id = algorithm_tags.tag_id
                JOIN algorithms ON algorithms.id = algorithm_tags.algorithm_id
                WHERE algorithms.name = ?
                """,
                (name,),
            )
            tags = [t[0] for t in cur.fetchall()]

        self.name_var.set(f"{name}")
        self.notation_var.set(f"{notation}")
        self.tags_var.set("")
        self.feedback_var.set("")

        # Refresh tag widgets
        for widget in self.tags_frame.winfo_children():
            widget.destroy()

        if tags:
            tag_container = ctk.CTkFrame(self.tags_frame, fg_color="transparent")
            tag_container.pack(anchor="center")
            for tag in tags:
                tag_chip = ctk.CTkLabel(
                    tag_container,
                    text=tag,
                    corner_radius=8,
                    fg_color="#4A5568",
                    text_color="white",
                    padx=12,
                    pady=6
                )
                tag_chip.pack(side="left", padx=(0, 8), pady=2)
        else:
            ctk.CTkLabel(self.tags_frame, text="—", text_color="gray").pack(anchor="center")

        self.selected_algorithm = name
        self.stopwatch_target_var.set(f"Timing: {name}")
        self.reset_timer()  # Reset timer when switching algorithms

    def remove_algorithm(self, name: str):
        try:
            with sqlite3.connect(Algorithm.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT id FROM algorithms WHERE name = ?", (name,))
                res = cur.fetchone()
                if res:
                    alg_id = res[0]
                    # Remove tag relations first for FK integrity
                    cur.execute("DELETE FROM algorithm_tags WHERE algorithm_id = ?", (alg_id,))
                    cur.execute("DELETE FROM algorithms WHERE id = ?", (alg_id,))
                    conn.commit()
            self.feedback_var.set(f"Deleted '{name}'.")
            self.load_algorithm_list(self.search_entry.get().lower() if hasattr(self, 'search_entry') else "")
            # Clear detail view if it was the selected item
            if self.name_var.get() == name:
                self.name_var.set("")
                self.notation_var.set("")
                for w in self.tags_frame.winfo_children():
                    w.destroy()
                self.selected_algorithm = None
                self.stopwatch_target_var.set("No algorithm selected")
                self.reset_timer()
        except Exception as e:
            self.feedback_var.set(f"Error deleting: {e}")

    def show_add_algorithm_modal(self):
        self.clear_parent_frame()
        # Disable spacebar timer in modal
        self.enable_stopwatch_keys(False)

        self.parent_frame.configure(fg_color="transparent")

        modal_frame = ctk.CTkFrame(
            self.parent_frame,
            width=675,
            height=450,
            corner_radius=15,
            fg_color="#5A6E73",
            border_width=3,
            border_color="#5A6E73"
        )
        modal_frame.pack_propagate(False)
        modal_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Left panel - #33363D
        left_panel = ctk.CTkFrame(
            modal_frame,
            fg_color="#33363D",
            corner_radius=12,
            width=337,
        )
        left_panel.pack_propagate(False)
        left_panel.pack(side="left", fill="both", expand=True, padx=(3, 0), pady=3)

        # Right panel - 10% darker (#2D3033)
        right_panel = ctk.CTkFrame(
            modal_frame,
            fg_color="#2D3033",
            corner_radius=12,
            width=338,
        )
        right_panel.pack_propagate(False)
        right_panel.pack(side="left", fill="both", expand=True, padx=(0, 3), pady=3)

        # Content frame for left alignment
        content_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        content_frame.pack(anchor="w", padx=20, pady=20, fill="both", expand=True)

        # Title label in left panel
        lbl_title = ctk.CTkLabel(
            content_frame,
            text="Add Algorithm",
            font=("Rethink Sans", 24, "bold")
        )
        lbl_title.pack(anchor="w", pady=(0, 30))

        # Algorithm Name with placeholder
        ent_name = ctk.CTkEntry(
            content_frame,
            width=280,
            placeholder_text="Algorithm Name"
        )
        ent_name.pack(anchor="w", pady=(0, 15))

        # Notation with placeholder
        ent_not = ctk.CTkEntry(
            content_frame,
            width=280,
            placeholder_text="Notation"
        )
        ent_not.pack(anchor="w", pady=(0, 15))

        # Tags with placeholder
        ent_tags = ctk.CTkEntry(
            content_frame,
            width=280,
            placeholder_text="Tags (comma-separated)"
        )
        ent_tags.pack(anchor="w", pady=(0, 15))

        # Message label in left panel
        msg_var = ctk.StringVar(value="")
        lbl_msg = ctk.CTkLabel(content_frame, textvariable=msg_var, text_color="red")
        lbl_msg.pack(anchor="w", pady=(10, 5))

        def save_and_return():
            name = ent_name.get().strip()
            notation = ent_not.get().strip()
            tags_raw = ent_tags.get().strip()

            if not name or not notation:
                msg_var.set("Name and notation are required.")
                return

            with sqlite3.connect(Algorithm.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM algorithms WHERE name=?", (name,))
                if cur.fetchone():
                    msg_var.set("Name already exists.")
                    return

            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            alg = Algorithm(name, notation, tags)

            try:
                alg.save_to_db()
                self.draw_main_ui()
                self.feedback_var.set(f"Added '{name}'.")
            except Exception as e:
                msg_var.set(f"Error: {e}")

        # Buttons frame in right panel
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(side="bottom", anchor="se", padx=20, pady=20)

        btn_cancel = ctk.CTkButton(btn_frame, text="Cancel", command=self.draw_main_ui, width=100)
        btn_cancel.pack(side="right", padx=(10, 0))

        btn_save = ctk.CTkButton(btn_frame, text="Save", command=save_and_return, width=100)
        btn_save.pack(side="right", padx=(0, 10))
        
    def show_login_modal(self):
        # Clear the parent frame for the login modal
        self.clear_parent_frame()
        # Disable spacebar timer in modal
        self.enable_stopwatch_keys(False)

        # Create the login modal frame
        modal_frame = ctk.CTkFrame(
            self.parent_frame,
            width=400,
            height=300,
            corner_radius=15,
            fg_color="#5A6E73",
            border_width=3,
            border_color="#5A6E73"
        )
        modal_frame.pack_propagate(False)
        modal_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title label
        lbl_title = ctk.CTkLabel(
            modal_frame,
            text="Login / Register",
            font=("Rethink Sans", 24, "bold")
        )
        lbl_title.pack(pady=20)

        # Username entry
        ent_username = ctk.CTkEntry(
            modal_frame,
            placeholder_text="Username",
            width=280
        )
        ent_username.pack(pady=10)

        # Password entry
        ent_password = ctk.CTkEntry(
            modal_frame,
            placeholder_text="Password",
            width=280,
            show="*"
        )
        ent_password.pack(pady=10)

        # Message label
        msg_var = ctk.StringVar(value="")
        lbl_msg = ctk.CTkLabel(modal_frame, textvariable=msg_var, text_color="red")
        lbl_msg.pack(pady=10)

        def on_login():
            username = ent_username.get().strip()
            password = ent_password.get().strip()

            if not username or not password:
                msg_var.set("Username and password are required.")
                return

            # Here you would typically check the credentials with the database
            if username == "admin" and password == "admin":
                msg_var.set("Login successful!")
                # Proceed to the next part of your application
            else:
                msg_var.set("Invalid credentials.")

        # Login button
        btn_login = ctk.CTkButton(modal_frame, text="Login", command=on_login, width=100)
        btn_login.pack(pady=10)

        # Switch to register (for now, just a placeholder)
        btn_register = ctk.CTkButton(modal_frame, text="Register", command=lambda: msg_var.set("Registration not implemented."), width=100)
        btn_register.pack(pady=10)

    def show_dashboard(self):
        """Dashboard with same layout as main: details left, algorithm list right."""
        self.clear_parent_frame()
        # Disable spacebar timer on dashboard
        self.enable_stopwatch_keys(False)

        # Header (same style)
        self.header = ctk.CTkFrame(self.parent_frame, height=80)
        self.header._fg_color = "#383E46"
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_rowconfigure(0, weight=1)

        icon_path = os.path.join(os.path.dirname(__file__), "../icon.ico")
        icon_image = ctk.CTkImage(light_image=Image.open(icon_path), size=(64, 64))
        icon_label = ctk.CTkLabel(self.header, image=icon_image, text="")
        icon_label.grid(row=0, column=0, sticky="nsew")

        back_button = ctk.CTkButton(self.header, text="← Algorithms", width=140, command=self.draw_main_ui)
        back_button.place(relx=0.0, rely=0.5, anchor="w", x=20)

        exit_button = ctk.CTkButton(self.header, text="Exit", width=80, command=self.parent_frame.winfo_toplevel().destroy)
        exit_button.place(relx=1.0, rely=0.5, anchor="e", x=-20)

        # Content (same grid/frames)
        self.content_frame = ctk.CTkFrame(self.parent_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.parent_frame.grid_rowconfigure(1, weight=1)
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=0)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Details (left) – shows times list for selected algorithm
        self.dashboard_details_frame = ctk.CTkFrame(self.content_frame, fg_color="#222326", corner_radius=0)
        self.dashboard_details_frame.grid(row=0, column=0, sticky="nsew")

        # Right list – same styling as main page
        self.dashboard_list_frame = ctk.CTkFrame(self.content_frame, width=360, fg_color="#33363D")
        self.dashboard_list_frame.grid(row=0, column=1, sticky="nsew")
        self.dashboard_list_frame.grid_rowconfigure(0, weight=0)
        self.dashboard_list_frame.grid_rowconfigure(1, weight=1)
        self.dashboard_list_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_list_frame.grid_columnconfigure(1, weight=0)  # filter button column
        self.dashboard_list_frame.grid_propagate(False)

        # Search (same placeholder/height)
        self.dashboard_search_entry = ctk.CTkEntry(
            self.dashboard_list_frame,
            placeholder_text="Search...",
            height=35
        )
        self.dashboard_search_entry.grid(row=0, column=0, sticky="ew", padx=(10, 6), pady=(10, 5))
        self.dashboard_search_entry.bind("<KeyRelease>", self.on_dashboard_search_change)

        # Filter button (to the right of search)
        self.dashboard_filter_btn = ctk.CTkButton(
            self.dashboard_list_frame,
            text="Filter",
            width=90,
            command=self.open_dashboard_filter_dialog
        )
        self.dashboard_filter_btn.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=(10, 5))

        # Scrollable algorithm list
        self.dashboard_scrollable_list = ctk.CTkScrollableFrame(self.dashboard_list_frame, fg_color="#33363D", corner_radius=0)
        self.dashboard_scrollable_list.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Initial load and empty state
        self.load_dashboard_algorithm_list()
        self.show_dashboard_empty_state()

    def on_dashboard_search_change(self, event=None):
        query = self.dashboard_search_entry.get().lower()
        self.load_dashboard_algorithm_list(query)

    def load_dashboard_algorithm_list(self, search_query=""):
        # Clear
        for w in self.dashboard_scrollable_list.winfo_children():
            w.destroy()

        order_sql = "ASC" if self.dashboard_sort_order == "asc" else "DESC"

        with sqlite3.connect(Algorithm.db_path) as conn:
            cur = conn.cursor()
            tags = list(self.dashboard_filter_tags)
            has_tags = len(tags) > 0
            has_search = bool(search_query)

            if has_tags:
                placeholders = ",".join(["?"] * len(tags))
                where_parts = [f"t.name IN ({placeholders})"]
                params = tags[:]
                if has_search:
                    where_parts.append("(LOWER(a.name) LIKE ? OR LOWER(a.notation) LIKE ?)")
                    params.extend([f"%{search_query}%", f"%{search_query}%"])
                where_clause = " AND ".join(where_parts)
                sql = f"""
                    SELECT DISTINCT a.name
                    FROM algorithms a
                    JOIN algorithm_tags at ON at.algorithm_id = a.id
                    JOIN tags t ON t.id = at.tag_id
                    WHERE {where_clause}
                    ORDER BY a.name COLLATE NOCASE {order_sql}
                """
                cur.execute(sql, params)
                names = [r[0] for r in cur.fetchall()]
            else:
                if has_search:
                    cur.execute(
                        f"""
                        SELECT a.name
                        FROM algorithms a
                        WHERE LOWER(a.name) LIKE ? OR LOWER(a.notation) LIKE ?
                        ORDER BY a.name COLLATE NOCASE {order_sql}
                        """,
                        (f"%{search_query}%", f"%{search_query}%")
                    )
                    names = [r[0] for r in cur.fetchall()]
                else:
                    cur.execute(f"SELECT name FROM algorithms ORDER BY name COLLATE NOCASE {order_sql}")
                    names = [r[0] for r in cur.fetchall()]

        # Build rows
        for name in names:
            row = ctk.CTkFrame(self.dashboard_scrollable_list)
            row.pack(fill="x", pady=2, padx=5)

            lbl = ctk.CTkLabel(row, text=name, cursor="hand2")
            lbl.pack(side="left", padx=(5, 10), pady=10)

            row.bind("<Button-1>", lambda e, n=name: self.show_algorithm_times(n))
            lbl.bind("<Button-1>", lambda e, n=name: self.show_algorithm_times(n))
            row.configure(cursor="hand2")

            # Right count label (instead of Remove)
            try:
                with sqlite3.connect(Algorithm.db_path) as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT COUNT(*) FROM times t
                        JOIN algorithms a ON t.algorithm_id = a.id
                        WHERE a.name = ?
                    """, (name,))
                    count = cur.fetchone()[0]
                ctk.CTkLabel(row, text=f"({count} times)", text_color="gray").pack(side="right", padx=(0, 10))
            except Exception:
                pass

    def show_dashboard_empty_state(self):
        # Clear details
        for w in self.dashboard_details_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.dashboard_details_frame, text="Dashboard", font=(FONT, 36, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(
            self.dashboard_details_frame,
            text="Select an algorithm from the list to view all saved times.",
            font=(FONT, 16),
            text_color="gray"
        ).pack(pady=10)

    def show_algorithm_times(self, algorithm_name: str):
        # Clear details
        for w in self.dashboard_details_frame.winfo_children():
            w.destroy()

        # Title
        ctk.CTkLabel(
            self.dashboard_details_frame,
            text=f"Times — {algorithm_name}",
            font=(FONT, 32, "bold")
        ).pack(pady=(20, 10))

        # Scrollable times area (fills like main)
        times_list = ctk.CTkScrollableFrame(self.dashboard_details_frame, fg_color="transparent")
        times_list.pack(fill="both", expand=True, padx=20, pady=20)

        # Load times
        try:
            with sqlite3.connect(Algorithm.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT t.time_seconds, t.timestamp
                    FROM times t
                    JOIN algorithms a ON t.algorithm_id = a.id
                    WHERE a.name = ?
                    ORDER BY t.timestamp DESC
                """, (algorithm_name,))
                times_data = cur.fetchall()
        except Exception as e:
            ctk.CTkLabel(times_list, text=f"Error loading times: {e}", text_color="red").pack(pady=20)
            return

        if not times_data:
            ctk.CTkLabel(times_list, text="No times recorded yet.", text_color="gray").pack(pady=20)
            return

        # Stats (simple summary)
        times_only = [t[0] for t in times_data]
        best = min(times_only)
        worst = max(times_only)
        avg = sum(times_only) / len(times_only)

        stats = ctk.CTkFrame(times_list, fg_color="#333D", corner_radius=10)
        stats.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(stats, text="Summary", font=(FONT, 20, "bold")).pack(pady=(12, 6))
        row = ctk.CTkFrame(stats, fg_color="transparent")
        row.pack(padx=16, pady=(0, 12), fill="x")
        ctk.CTkLabel(row, text=f"Best: {best:.3f}s", font=(FONT, 14)).pack(side="left")
        ctk.CTkLabel(row, text=f"Avg: {avg:.3f}s", font=(FONT, 14)).pack(side="left", padx=20)
        ctk.CTkLabel(row, text=f"Worst: {worst:.3f}s", font=(FONT, 14)).pack(side="left", padx=20)
        ctk.CTkLabel(row, text=f"Total: {len(times_only)}", font=(FONT, 14)).pack(side="left", padx=20)

        # Times list
        total = len(times_data)
        for i, (time_seconds, timestamp) in enumerate(times_data):
            item = ctk.CTkFrame(times_list, fg_color="#2A2D32", corner_radius=8)
            item.pack(fill="x", pady=2)

            row = ctk.CTkFrame(item, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=10)

            ctk.CTkLabel(row, text=f"#{total - i}", font=(FONT, 14, "bold"), text_color="gray").pack(side="left")
            ctk.CTkLabel(row, text=f"{time_seconds:.3f}s", font=(FONT, 16, "bold")).pack(side="left", padx=(20, 0))

            # timestamp formatting
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00') if isinstance(timestamp, str) and timestamp.endswith('Z') else str(timestamp))
                ts = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                ts = str(timestamp)
            ctk.CTkLabel(row, text=ts, font=(FONT, 12), text_color="gray").pack(side="right")

    def open_dashboard_filter_dialog(self):
        """Open dialog to choose tag filters and sort order."""
        dlg = ctk.CTkToplevel(self.parent_frame.winfo_toplevel())
        dlg.title("Filter & Sort")
        dlg.geometry("380x440")
        dlg.transient(self.parent_frame.winfo_toplevel())
        dlg.grab_set()

        root = ctk.CTkFrame(dlg)
        root.pack(fill="both", expand=True, padx=16, pady=16)

        # Tags section
        ctk.CTkLabel(root, text="Filter by tags", font=(FONT, 16, "bold")).pack(anchor="w", pady=(0, 8))
        tags_frame = ctk.CTkScrollableFrame(root, height=220, fg_color="transparent")
        tags_frame.pack(fill="x", pady=(0, 12))

        tag_vars = {}
        tags = self.get_all_tags()
        if tags:
            for t in tags:
                var = ctk.BooleanVar(value=(t in self.dashboard_filter_tags))
                cb = ctk.CTkCheckBox(tags_frame, text=t, variable=var)
                cb.pack(anchor="w", pady=2)
                tag_vars[t] = var
        else:
            ctk.CTkLabel(tags_frame, text="No tags found.", text_color="gray").pack(anchor="w", pady=4)

        # Sort section
        ctk.CTkLabel(root, text="Sort", font=(FONT, 16, "bold")).pack(anchor="w", pady=(8, 6))
        sort_values = ["A-Z", "Z-A"]
        current_sort = "A-Z" if self.dashboard_sort_order == "asc" else "Z-A"
        sort_menu = ctk.CTkOptionMenu(root, values=sort_values)
        sort_menu.set(current_sort)
        sort_menu.pack(anchor="w")

        # Buttons
        btns = ctk.CTkFrame(root, fg_color="transparent")
        btns.pack(fill="x", pady=(18, 0))
        def apply_and_close():
            self.dashboard_filter_tags = {name for name, v in tag_vars.items() if v.get()}
            sel = sort_menu.get()
            self.dashboard_sort_order = "asc" if sel == "A-Z" else "desc"
            # reload list with current search text
            q = self.dashboard_search_entry.get().lower() if hasattr(self, "dashboard_search_entry") else ""
            self.load_dashboard_algorithm_list(q)
            dlg.destroy()

        def clear_and_close():
            self.dashboard_filter_tags = set()
            self.dashboard_sort_order = "asc"
            q = self.dashboard_search_entry.get().lower() if hasattr(self, "dashboard_search_entry") else ""
            self.load_dashboard_algorithm_list(q)
            dlg.destroy()

        ctk.CTkButton(btns, text="Clear", command=clear_and_close, width=100).pack(side="left")
        ctk.CTkButton(btns, text="Apply", command=apply_and_close, width=100).pack(side="right")

    def get_all_tags(self):
        """Return list of all tag names."""
        try:
            with sqlite3.connect(Algorithm.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM tags ORDER BY name COLLATE NOCASE ASC")
                return [r[0] for r in cur.fetchall()]
        except Exception:
            return []

    def enable_stopwatch_keys(self, enabled: bool):
        """Enable or disable stopwatch keyboard controls."""
        if enabled:
            # Bind to the toplevel window to capture all key events
            toplevel = self.parent_frame.winfo_toplevel()
            toplevel.bind("<KeyPress-space>", self.on_space_press)
            toplevel.bind("<KeyRelease-space>", self.on_space_release)
            toplevel.focus_set()
        else:
            # Unbind events
            toplevel = self.parent_frame.winfo_toplevel()
            toplevel.unbind("<KeyPress-space>")
            toplevel.unbind("<KeyRelease-space>")

    def on_space_press(self, event):
        """Handle spacebar press for stopwatch control (from poop.py)"""
        if self.hold_start is None:
            self.hold_start = time.time()
            if not self.running:
                self.stopwatch_time_label.configure(text_color="red")
                self.stopwatch_state_var.set("Hold to start...")
            self.parent_frame.after(10, self.check_hold_duration)

    def on_space_release(self, event):
        """Handle spacebar release for stopwatch control (from poop.py)"""
        if self.hold_start is None:
            return

        hold_duration = time.time() - self.hold_start

        if self.ready:
            if not self.running and self.elapsed == 0:
                self.start_stopwatch()
            elif not self.running and self.elapsed > 0:
                self.reset_stopwatch()
                self.start_stopwatch()
        elif self.running and hold_duration < 0.5:
            self.stop_stopwatch()

        self.hold_start = None
        self.ready = False

    def check_hold_duration(self):
        """Check how long spacebar has been held (from poop.py)"""
        if self.hold_start is None:
            return

        held_time = time.time() - self.hold_start

        if held_time >= 0.5:
            self.ready = True
            if not self.running:
                self.stopwatch_time_label.configure(text_color="green")
                self.stopwatch_state_var.set("Ready to start!")
        else:
            if not self.running:
                self.stopwatch_time_label.configure(text_color="red")
                self.stopwatch_state_var.set("Hold to start...")
            self.parent_frame.after(10, self.check_hold_duration)

    def start_stopwatch(self):
        """Start the stopwatch timer (from poop.py)"""
        if not self.selected_algorithm:
            self.feedback_var.set("Please select an algorithm first!")
            return
            
        self.running = True
        self.start_time = time.time()
        self.elapsed = 0
        self.stopwatch_time_label.configure(text_color="white")
        self.stopwatch_state_var.set("Running...")

    def stop_stopwatch(self):
        """Stop the stopwatch and save the time (from poop.py)"""
        if not self.running:
            return
            
        self.running = False
        self.elapsed = time.time() - self.start_time
        self.stopwatch_state_var.set(f"Stopped: {self.elapsed:.3f}s")
        
        # Save the time to database
        self.save_time_to_db(self.elapsed)

    def save_time_to_db(self, time_seconds: float):
        """Save the stopwatch time to the database"""
        if not self.selected_algorithm:
            return
            
        try:
            with sqlite3.connect(Algorithm.db_path) as conn:
                cur = conn.cursor()
                # Get algorithm ID
                cur.execute("SELECT id FROM algorithms WHERE name = ?", (self.selected_algorithm,))
                result = cur.fetchone()
                if result:
                    algorithm_id = result[0]
                    # Insert the time
                    cur.execute(
                        "INSERT INTO times (algorithm_id, time_seconds) VALUES (?, ?)",
                        (algorithm_id, time_seconds)
                    )
                    conn.commit()
                    self.feedback_var.set(f"Time saved: {time_seconds:.3f}s")
                else:
                    self.feedback_var.set("Algorithm not found!")
        except Exception as e:
            self.feedback_var.set(f"Error saving time: {e}")

    def update_stopwatch_display(self):
        """Update the stopwatch display (from poop.py)"""
        if self.running:
            current = time.time() - self.start_time
            self.stopwatch_time_var.set(f"{current:.3f}")
        else:
            self.stopwatch_time_var.set(f"{self.elapsed:.3f}")
        
        # Schedule next update
        self.parent_frame.after(10, self.update_stopwatch_display)

    def reset_timer(self):
        """Reset the stopwatch timer."""
        self.running = False
        self.elapsed = 0
        self.start_time = 0
        self.hold_start = None
        self.ready = False
        self.stopwatch_time_var.set("0.000")
        self.stopwatch_state_var.set("Ready")
        self.stopwatch_time_label.configure(text_color="white")
        if self._after_job:
            self.parent_frame.after_cancel(self._after_job)
            self._after_job = None

def create_algorithm_ui(parent_frame: ctk.CTkFrame):
    """Factory function to create AlgorithmUI instance for backward compatibility"""
    return AlgorithmUI(parent_frame)