#   Name: Kayden Ye
#   Date: 2/07/2025
#   File: gui/algorithm.py

import customtkinter as ctk
import sqlite3
from classes.algorithm import Algorithm

def create_algorithm_ui(parent_frame):
    form_frame = ctk.CTkFrame(parent_frame)
    form_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    list_frame = ctk.CTkFrame(parent_frame)
    list_frame.pack(side="right", fill="both", expand=True)

    title_label = ctk.CTkLabel(form_frame, text="Add New Algorithm", font=("Arial", 20))
    title_label.pack(pady=10)

    name_label = ctk.CTkLabel(form_frame, text="Algorithm Name:")
    name_label.pack()
    name_entry = ctk.CTkEntry(form_frame)
    name_entry.pack(pady=5)

    notation_label = ctk.CTkLabel(form_frame, text="Notation:")
    notation_label.pack()
    notation_entry = ctk.CTkEntry(form_frame)
    notation_entry.pack(pady=5)

    tags_label = ctk.CTkLabel(form_frame, text="Tags (comma-separated):")
    tags_label.pack()
    tags_entry = ctk.CTkEntry(form_frame)
    tags_entry.pack(pady=5)

    feedback_label = ctk.CTkLabel(form_frame, text="")
    feedback_label.pack(pady=10)

    list_title = ctk.CTkLabel(list_frame, text="Saved Algorithms", font=("Arial", 18))
    list_title.pack(pady=10)

    scrollable_list = ctk.CTkScrollableFrame(list_frame, width=300, height=400)
    scrollable_list.pack(fill="both", expand=True, padx=10, pady=10)

    def load_algorithm_list():
        for widget in scrollable_list.winfo_children():
            widget.destroy()

        conn = sqlite3.connect(Algorithm.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM algorithms ORDER BY name")
        names = [row[0] for row in cursor.fetchall()]
        conn.close()

        for name in names:
            entry_frame = ctk.CTkFrame(scrollable_list)
            entry_frame.pack(fill="x", pady=2, padx=5)

            name_label = ctk.CTkLabel(entry_frame, text=name)
            name_label.pack(side="left", padx=(5, 10))

            remove_btn = ctk.CTkButton(
                entry_frame,
                text="Remove",
                fg_color="red",
                hover_color="#aa0000",
                width=80,
                command=lambda n=name: remove_algorithm(n)
            )
            remove_btn.pack(side="right", padx=5)

    def remove_algorithm(name):
        try:
            conn = sqlite3.connect(Algorithm.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM algorithms WHERE name = ?", (name,))
            result = cursor.fetchone()
            if result:
                algorithm_id = result[0]
                cursor.execute("DELETE FROM algorithm_tags WHERE algorithm_id = ?", (algorithm_id,))
                cursor.execute("DELETE FROM algorithms WHERE id = ?", (algorithm_id,))
                conn.commit()
            conn.close()

            feedback_label.configure(text=f"Deleted algorithm '{name}'", text_color="green")
            load_algorithm_list()
        except Exception as e:
            feedback_label.configure(text=f"Error deleting: {str(e)}", text_color="red")

    def submit_algorithm():
        name = name_entry.get().strip()
        notation = notation_entry.get().strip()
        tags_raw = tags_entry.get().strip()

        if not name or not notation:
            feedback_label.configure(text="Name and notation are required.", text_color="red")
            return

        conn = sqlite3.connect(Algorithm.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM algorithms WHERE name = ?", (name,))
        exists = cursor.fetchone()
        conn.close()

        if exists:
            feedback_label.configure(text=f"Algorithm '{name}' already exists.", text_color="orange")
            return

        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        algo = Algorithm(name, notation, tags)

        try:
            algo.save_to_db()
            feedback_label.configure(text=f"Algorithm '{name}' saved!", text_color="green")
            name_entry.delete(0, 'end')
            notation_entry.delete(0, 'end')
            tags_entry.delete(0, 'end')
            load_algorithm_list()
        except Exception as e:
            feedback_label.configure(text=f"Error: {str(e)}", text_color="red")

    submit_button = ctk.CTkButton(form_frame, text="Save Algorithm", command=submit_algorithm)
    submit_button.pack(pady=20)

    load_algorithm_list()
