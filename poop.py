import customtkinter as ctk
import CTkGradient as ctkg
import tkinter as tk
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class StopwatchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Stopwatch")
        self.geometry("300x200")

        # Create a GradientFrame as the background
        self.gradient_frame = ctkg.GradientFrame(
            master=self,
            colors=("#ec0075", "#ffd366"),
            direction="vertical",
            corner_radius=10,
            height=200,   # Match window height
            width=300     # Match window width
        )
        self.gradient_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Create text directly on the gradient canvas (centered)
        self.text_id = self.gradient_frame.gradient.create_text(
            150, 100,  # Center position (300/2, 200/2)
            text="0.000",
            font=("Arial", 40),
            fill="white",
            anchor="center"
        )

        # State variables
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.hold_start = None
        self.ready = False

        self.bind("<KeyPress-space>", self.on_space_press)
        self.bind("<KeyRelease-space>", self.on_space_release)
        self.focus_set()

        self.update_display()

    def on_space_press(self, event):
        if self.hold_start is None:
            self.hold_start = time.time()
            if not self.running:
                self.gradient_frame.gradient.itemconfig(self.text_id, fill="red")  # Only show red if not running
            self.after(10, self.check_hold_duration)

    def on_space_release(self, event):
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
        if self.hold_start is None:
            return

        held_time = time.time() - self.hold_start

        if held_time >= 0.5:
            self.ready = True
            if not self.running:
                self.gradient_frame.gradient.itemconfig(self.text_id, fill="green")
        else:
            if not self.running:
                self.gradient_frame.gradient.itemconfig(self.text_id, fill="red")
            self.after(10, self.check_hold_duration)

    def start_stopwatch(self):
        self.running = True
        self.start_time = time.time()
        self.elapsed = 0
        self.gradient_frame.gradient.itemconfig(self.text_id, fill="white")

    def stop_stopwatch(self):
        self.running = False
        self.elapsed = time.time() - self.start_time

    def reset_stopwatch(self):
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.gradient_frame.gradient.itemconfig(self.text_id, text="0.000")

    def update_display(self):
        if self.running:
            current = time.time() - self.start_time
            self.gradient_frame.gradient.itemconfig(self.text_id, text=f"{current:.3f}")
        else:
            self.gradient_frame.gradient.itemconfig(self.text_id, text=f"{self.elapsed:.3f}")
        self.after(10, self.update_display)

if __name__ == "__main__":
    app = StopwatchApp()
    app.mainloop()