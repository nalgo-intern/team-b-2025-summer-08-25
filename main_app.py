import os
# TensorFlowの警告ログを抑制（INFOとWARNINGが表示されなくなる）
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tkinter as tk
from tkinter import ttk

from screens.game_start_screen import GameStartScreen
from screens.game_play_screen import GamePlayScreen
from screens.game_over_screen import GameOverScreen

class GameManager(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Janken Game App")
        # self.geometry("1000x700") # 初期ウィンドウサイズはフルスクリーンで不要
        self.attributes('-fullscreen', True) # フルスクリーンを有効にする
        self.bind('<Escape>', self.exit_fullscreen) # Escapeキーでフルスクリーン解除

        # コンテナフレームを作成し、ウィンドウ全体を埋めるように配置
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # 各画面クラスをインスタンス化し、辞書に格納
        for F in (GameStartScreen, GamePlayScreen, GameOverScreen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # 全ての画面を同じグリッドセルに配置し、表示したい画面だけを最前面に持ってくる
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("GameStartScreen")

    def exit_fullscreen(self, event=None):
        """Escapeキーでフルスクリーンを解除する"""
        self.attributes('-fullscreen', False)

    def show_frame(self, page_name):
        """指定された画面を最前面に表示する"""
        # 現在表示されているフレームがGamePlayScreenであれば停止する
        current_frame_name = None
        for name, frame_instance in self.frames.items():
            if frame_instance.winfo_ismapped(): # 現在表示されているフレームを特定
                current_frame_name = name
                break

        if current_frame_name == "GamePlayScreen":
            self.frames["GamePlayScreen"].stop_game_loop()

        # 新しいフレームを表示
        frame = self.frames[page_name]
        frame.tkraise()

        # 新しいフレームがGamePlayScreenであれば開始する
        if page_name == "GamePlayScreen":
            self.frames["GamePlayScreen"].start_game_loop()

    def show_game_over_screen(self, final_score):
        """ゲームオーバー画面を表示し、スコアを渡す"""
        game_over_frame = self.frames["GameOverScreen"]
        game_over_frame.set_score(final_score)
        self.show_frame("GameOverScreen")


if __name__ == "__main__":
    app = GameManager()
    app.mainloop()
