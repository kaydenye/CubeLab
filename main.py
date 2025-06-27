import customtkinter as ctk
import os
from classes.algorithm import Algorithm
from classes.tag import Tag
from classes.stopwatch import Stopwatch

app = ctk.CTk()
app.title("CubeLab")

script_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(script_dir, "icon.ico")
app.iconbitmap(icon_path)

app.geometry("1920x1080")
app.state("zoomed")

algo = Algorithm("sune", "R U R' U R U2 R'", ["oll"])
print(algo)

print(algo.get_name())
print(algo.get_notation())
print(algo.get_tags())

# algo.set_name("new_sune")
algo.set_notation("R U R' U' R' F R F'")
algo.add_tag("beginner")
algo.remove_tag("oll")

tag = Tag("tag2")
print(tag)

algo.add_tag(tag)

algo.save_to_db()

print(algo)

loaded = Algorithm.load_from_db("sune")
print(loaded)

# app.mainloop()
