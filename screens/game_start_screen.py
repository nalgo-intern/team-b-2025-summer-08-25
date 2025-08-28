import tkinter as tk
from tkinter import ttk

class GameStartScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Jesture Game - Main Menu", font=("Helvetica", 24))
        label.pack(pady=20, padx=20)

        start_button = ttk.Button(self, text="Start Game",
                                  command=lambda: controller.show_frame("GamePlayScreen"))
        start_button.pack(pady=10)

        quit_button = ttk.Button(self, text="Quit",
                                 command=controller.destroy)
        quit_button.pack(pady=10)

        debug_button = ttk.Button(self, text="Debug Mode",
                                  command=lambda: controller.show_frame("GamePlayScreen", debug=True))
        debug_button.pack(pady=10)
