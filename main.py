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
import platform

if platform.system() == "Windows":
    from ctypes import windll, byref, sizeof, c_int
    windll.shcore.SetProcessDpiAwareness(2)

app = ctk.CTk()
app.title("CubeLab")

script_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(script_dir, "icon.ico")
app.iconbitmap(icon_path)

app.geometry("1920x1080")

app.attributes("-fullscreen", True)

main_frame = ctk.CTkFrame(app)
main_frame.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack

# Let it expand with the window
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

create_algorithm_ui(main_frame)

app.mainloop()