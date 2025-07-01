import customtkinter as ctk
import os
from classes.algorithm import Algorithm
from classes.tag import Tag
from classes.stopwatch import Stopwatch
from classes.user import User
from classes.cube_model import CubeModel
# from util.algorithm import load_algorithm_list
from gui.algorithm import create_algorithm_ui
import sqlite3

app = ctk.CTk()
app.title("CubeLab")

script_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(script_dir, "icon.ico")
app.iconbitmap(icon_path)

app.geometry("800x600")

main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

create_algorithm_ui(main_frame)

app.mainloop()
