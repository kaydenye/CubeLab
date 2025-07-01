#   Name: Kayden Ye
#   Date: 30/06/2025
#   File: classes/algorithm.py

class Stopwatch:
    def __init__(self, 
                 time: float, 
                 is_running: bool):
        self.time = time
        self.is_running = is_running

    def __str__(self):
        return f"Time: {self.time}, Is Running?: {self.is_running}"

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

    def reset():
        pass

    def get_time(self):
        return self.time