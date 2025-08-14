import customtkinter as ctk
import os
from gui.main_window import create_algorithm_ui
import platform

if platform.system() == "Windows":
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(2)

app = ctk.CTk()
app.title("CubeLab")

script_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(script_dir, "icon.ico")
app.iconbitmap(icon_path)

app.geometry("1920x1080")
app.attributes("-fullscreen", True)

main_frame = ctk.CTkFrame(app)
main_frame.grid(row=0, column=0, sticky="nsew")

app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

create_algorithm_ui(main_frame)

app.mainloop()
