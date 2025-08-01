import customtkinter as ctk
import CTkGradient as ctkg
import sqlite3
import os
from PIL import Image
from classes.algorithm import Algorithm

FONT = "Rethink Sans"

class AlgorithmUI:
    def __init__(self, parent_frame: ctk.CTkFrame):
        self.parent_frame = parent_frame
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
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_propagate(False)

        self.scrollable_list = ctk.CTkScrollableFrame(self.list_frame, fg_color="#33363D", corner_radius=0)
        self.scrollable_list.grid(row=0, column=0, sticky="nsew")

        self.add_button = ctk.CTkButton(self.list_frame, text="+", width=40, command=self.show_add_algorithm_modal)
        self.add_button.grid(row=1, column=0, sticky="ew", padx=10, pady=(10, 5))

        # Variables for UI state
        self.name_var = ctk.StringVar(value="")
        self.notation_var = ctk.StringVar(value="")
        self.tags_var = ctk.StringVar(value="")
        self.feedback_var = ctk.StringVar(value="")

        # Labels in details frame
        self.name_label = ctk.CTkLabel(self.details_frame, textvariable=self.name_var, font=(FONT, 48, "bold"))
        self.name_label.pack(pady=5)

        self.notation_label = ctk.CTkLabel(self.details_frame, textvariable=self.notation_var, font=(FONT, 24))
        self.notation_label.pack()

        self.tags_label = ctk.CTkLabel(self.details_frame, textvariable=self.tags_var, wraplength=400)
        self.tags_label.pack(pady=5)

        self.feedback_label = ctk.CTkLabel(self.details_frame, textvariable=self.feedback_var)
        self.feedback_label.pack(pady=10)

        # Load initial data
        self.load_algorithm_list()

    def load_algorithm_list(self):
        for w in self.scrollable_list.winfo_children():
            w.destroy()

        with sqlite3.connect(Algorithm.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM algorithms ORDER BY name")
            names = [r[0] for r in cur.fetchall()]

        for name in names:
            row = ctk.CTkFrame(self.scrollable_list)
            row.pack(fill="x", pady=2, padx=5)

            lbl = ctk.CTkLabel(row, text=name, cursor="hand2")
            lbl.pack(side="left", padx=(5, 10))
            lbl.bind("<Button-1>", lambda e, n=name: self.show_details(n))

            del_btn = ctk.CTkButton(
                row,
                text="Remove",
                fg_color="red",
                hover_color="#aa0000",
                width=80,
                command=lambda n=name: self.remove_algorithm(n),
            )
            del_btn.pack(side="right")

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
        self.tags_var.set(f"{', '.join(tags) if tags else '—'}")
        self.feedback_var.set("")

    def remove_algorithm(self, name: str):
        try:
            with sqlite3.connect(Algorithm.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT id FROM algorithms WHERE name = ?", (name,))
                res = cur.fetchone()
                if res:
                    alg_id = res[0]
                    cur.execute("DELETE FROM algorithm_tags WHERE algorithm_id = ?", (alg_id,))
                    cur.execute("DELETE FROM algorithms WHERE id = ?", (alg_id,))
                    conn.commit()
            self.feedback_var.set(f"Deleted '{name}'.")
            self.load_algorithm_list()
            if self.name_var.get().startswith("Name:") and name in self.name_var.get():
                self.name_var.set("")
                self.notation_var.set("")
                self.tags_var.set("")
        except Exception as e:
            self.feedback_var.set(f"Error deleting: {e}")

    def show_add_algorithm_modal(self):
        self.clear_parent_frame()

        self.parent_frame.configure(fg_color="transparent")

        modal_frame = ctk.CTkFrame(
            self.parent_frame,
            width=675,
            height=450,
            corner_radius=15,
            fg_color="#33363D",
            border_width=3,
            border_color="#5A6E73"
        )
        modal_frame.pack_propagate(False)
        modal_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title label
        lbl_title = ctk.CTkLabel(
            modal_frame,
            text="Add Algorithm",
            font=("Rethink Sans", 24, "bold")
        )
        lbl_title.pack(pady=(20, 10))

        # Algorithm Name
        lbl_name = ctk.CTkLabel(modal_frame, text="Algorithm Name:")
        lbl_name.pack(padx=10, pady=(10, 5))
        ent_name = ctk.CTkEntry(modal_frame, width=400)
        ent_name.pack(padx=10, pady=5)

        # Notation
        lbl_not = ctk.CTkLabel(modal_frame, text="Notation:")
        lbl_not.pack(padx=10, pady=(10, 5))
        ent_not = ctk.CTkEntry(modal_frame, width=400)
        ent_not.pack(padx=10, pady=5)

        # Tags
        lbl_tags = ctk.CTkLabel(modal_frame, text="Tags (comma-separated):")
        lbl_tags.pack(padx=10, pady=(10, 5))
        ent_tags = ctk.CTkEntry(modal_frame, width=400)
        ent_tags.pack(padx=10, pady=5)

        # Message label
        msg_var = ctk.StringVar(value="")
        lbl_msg = ctk.CTkLabel(modal_frame, textvariable=msg_var, text_color="red")
        lbl_msg.pack(pady=(10, 5))

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

        # Buttons frame
        btn_frame = ctk.CTkFrame(modal_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        btn_save = ctk.CTkButton(btn_frame, text="Save", command=save_and_return, width=100)
        btn_save.pack(side="left", padx=(0, 10))
        
        btn_cancel = ctk.CTkButton(btn_frame, text="Cancel", command=self.draw_main_ui, width=100)
        btn_cancel.pack(side="right", padx=(10, 0))

def create_algorithm_ui(parent_frame: ctk.CTkFrame):
    """Factory function to create AlgorithmUI instance for backward compatibility"""
    return AlgorithmUI(parent_frame)