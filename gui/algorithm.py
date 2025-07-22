import customtkinter as ctk
import sqlite3
import os
from PIL import Image
from classes.algorithm import Algorithm

FONT = "Rethink Sans"

def create_algorithm_ui(parent_frame: ctk.CTkFrame):
    # Header
    header = ctk.CTkFrame(parent_frame, height=80)
    header.grid(row=0, column=0, sticky="ew")
    header.grid_propagate(False)
    parent_frame.grid_rowconfigure(0, minsize=80)  # Optional: enforce header row height

    # Set up a single column and row, both centered
    header.grid_columnconfigure(0, weight=1)
    header.grid_rowconfigure(0, weight=1)

    # Load and center icon
    icon_path = os.path.join(os.path.dirname(__file__), "../icon.ico")
    icon_image = ctk.CTkImage(light_image=Image.open(icon_path), size=(64, 64))
    icon_label = ctk.CTkLabel(header, image=icon_image, text="")
    icon_label.grid(row=0, column=0, sticky="nsew")

    # Exit button (optional, still at top right)
    exit_button = ctk.CTkButton(header, text="Exit", width=80, command=parent_frame.winfo_toplevel().destroy)
    exit_button.place(relx=1.0, rely=0.5, anchor="e", x=-20)  # 🡐 stays right & vertically centered

    # Main content
    # Content frame (below header)
    content_frame = ctk.CTkFrame(parent_frame)
    content_frame.grid(row=1, column=0, sticky="nsew")
    parent_frame.grid_rowconfigure(1, weight=1)  # Let content expand
    parent_frame.grid_columnconfigure(0, weight=1)

    content_frame.grid_columnconfigure(0, weight=1)  # Left (details) expands
    content_frame.grid_columnconfigure(1, weight=0)  # Right (list) fixed
    content_frame.grid_rowconfigure(0, weight=1)

    # Details Frame (Left, 75%)
    details_frame = ctk.CTkFrame(content_frame)
    details_frame.grid(row=0, column=0, sticky="nsew")  # Expand

    # List Frame (Right, 25%)
    list_frame = ctk.CTkFrame(content_frame, width=360)
    list_frame.grid(row=0, column=1, sticky="nsew")
    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)
    list_frame.grid_propagate(False)

    # Scrollable list
    scrollable_list = ctk.CTkScrollableFrame(list_frame)
    scrollable_list.grid(row=0, column=0, sticky="nsew")

    # Add Button at Bottom
    add_button = ctk.CTkButton(list_frame, text="+", width=40, command=lambda: open_add_popup())
    add_button.grid(row=1, column=0, sticky="ew", padx=10, pady=(10, 5))

    # Details (name/notation/tags)
    details_title = ctk.CTkLabel(details_frame, text="Select an algorithm →", font=("Arial", 20))
    details_title.pack(pady=(20, 10))

    name_var = ctk.StringVar(value="")
    notation_var = ctk.StringVar(value="")
    tags_var = ctk.StringVar(value="")

    name_label = ctk.CTkLabel(details_frame, textvariable=name_var, font=("Arial", 16))
    name_label.pack(pady=5)

    notation_label = ctk.CTkLabel(details_frame, textvariable=notation_var, font=("Consolas", 14))
    notation_label.pack(pady=5)

    tags_label = ctk.CTkLabel(details_frame, textvariable=tags_var, wraplength=400)
    tags_label.pack(pady=5)

    feedback_var = ctk.StringVar(value="")
    feedback_label = ctk.CTkLabel(details_frame, textvariable=feedback_var)
    feedback_label.pack(pady=10)

    # (Keep the rest of your load_algorithm_list(), show_details(), remove_algorithm(), etc.)

    # load_algorithm_list()

    def load_algorithm_list():
        for w in scrollable_list.winfo_children():
            w.destroy()

        with sqlite3.connect(Algorithm.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM algorithms ORDER BY name")
            names = [r[0] for r in cur.fetchall()]

        for name in names:
            row = ctk.CTkFrame(scrollable_list)
            row.pack(fill="x", pady=2, padx=5)

            lbl = ctk.CTkLabel(row, text=name, cursor="hand2")
            lbl.pack(side="left", padx=(5, 10))
            lbl.bind("<Button-1>", lambda e, n=name: show_details(n))

            del_btn = ctk.CTkButton(
                row,
                text="Remove",
                fg_color="red",
                hover_color="#aa0000",
                width=80,
                command=lambda n=name: remove_algorithm(n),
            )
            del_btn.pack(side="right")

    def show_details(name: str):
        with sqlite3.connect(Algorithm.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT notation FROM algorithms WHERE name = ?", (name,))
            notation_row = cur.fetchone()
            if not notation_row:
                feedback_var.set(f"Could not load '{name}'.")
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

        details_title.configure(text="Algorithm Details")
        name_var.set(f"Name: {name}")
        notation_var.set(f"Notation: {notation}")
        tags_var.set(f"Tags: {', '.join(tags) if tags else '—'}")
        feedback_var.set("")

    def remove_algorithm(name: str):
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
            feedback_var.set(f"Deleted '{name}'.")
            load_algorithm_list()
            if name_var.get().startswith("Name:") and name in name_var.get():
                name_var.set("")
                notation_var.set("")
                tags_var.set("")
                details_title.configure(text="Select an algorithm →")
        except Exception as e:
            feedback_var.set(f"Error deleting: {e}")

    def open_add_popup():
        popup = ctk.CTkToplevel()
        popup.title("Add Algorithm")
        popup.geometry("400x350")
        popup.grab_set()

        ttk = {"padx": 10, "pady": 5}

        lbl_name = ctk.CTkLabel(popup, text="Algorithm Name:")
        lbl_name.pack(**ttk)
        ent_name = ctk.CTkEntry(popup)
        ent_name.pack(**ttk)

        lbl_not = ctk.CTkLabel(popup, text="Notation:")
        lbl_not.pack(**ttk)
        ent_not = ctk.CTkEntry(popup)
        ent_not.pack(**ttk)

        lbl_tags = ctk.CTkLabel(popup, text="Tags (comma-separated):")
        lbl_tags.pack(**ttk)
        ent_tags = ctk.CTkEntry(popup)
        ent_tags.pack(**ttk)

        msg_var = ctk.StringVar(value="")
        lbl_msg = ctk.CTkLabel(popup, textvariable=msg_var)
        lbl_msg.pack(pady=(5, 10))

        def save_and_close():
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
                popup.destroy()
                load_algorithm_list()
                feedback_var.set(f"Added '{name}'.")
            except Exception as e:
                msg_var.set(f"Error: {e}")

        btn_save = ctk.CTkButton(popup, text="Save", command=save_and_close)
        btn_save.pack(pady=10)

    load_algorithm_list()
