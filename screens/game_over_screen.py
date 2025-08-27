import tkinter as tk
from tkinter import ttk

class GameOverScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Game Over!", font=("Helvetica", 24))
        label.pack(pady=20, padx=20)

        self.score_label = ttk.Label(self, text="Final Score: 0", font=("Helvetica", 18))
        self.score_label.pack(pady=10)

        restart_button = ttk.Button(self, text="Play Again",
                                    command=lambda: controller.show_frame("GamePlayScreen"))
        restart_button.pack(pady=10)

        main_menu_button = ttk.Button(self, text="Main Menu",
                                      command=lambda: controller.show_frame("GameStartScreen"))
        main_menu_button.pack(pady=10)

    def set_score(self, score):
        self.score_label.config(text=f"Final Score: {score}")
