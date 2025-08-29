import tkinter as tk
from tkinter import ttk

from screens.game_start_screen import GameStartScreen
from screens.game_play_screen import GamePlayScreen
from screens.game_over_screen import GameOverScreen

class GameManager(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Jesture Game App")
        self.attributes('-fullscreen', True)
        self.bind('<Escape>', self.exit_fullscreen)

        # コンテナフレームをインスタンス変数として保持
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # GamePlayScreen以外を先にインスタンス化
        for F in (GameStartScreen, GameOverScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("GameStartScreen")

    def exit_fullscreen(self, event=None):
        """Escapeキーでフルスクリーンを解除する"""
        self.attributes('-fullscreen', False)

    def show_frame(self, page_name, debug=False):
        """指定された画面を最前面に表示する"""
        # GamePlayScreenに遷移する場合、またはGamePlayScreenから遷移する場合の処理
        # まず、既存のGamePlayScreenがあれば破棄する
        if "GamePlayScreen" in self.frames:
            self.frames["GamePlayScreen"].stop_game_loop()
            self.frames["GamePlayScreen"].destroy()
            del self.frames["GamePlayScreen"]

        # 遷移先に応じてフレームを準備
        if page_name == "GamePlayScreen":
            # GamePlayScreenを新規作成
            frame = GamePlayScreen(parent=self.container, controller=self)
            self.frames["GamePlayScreen"] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        else:
            # 既存のフレームを取得
            frame = self.frames[page_name]

        # フレームを最前面に表示
        frame.tkraise()

        # 遷移先がGamePlayScreenであればゲームループを開始
        if page_name == "GamePlayScreen":
            self.frames["GamePlayScreen"].start_game_loop(debug=debug)

    def show_game_over_screen(self, final_score):
        """ゲームオーバー画面を表示し、スコアを渡す"""
        game_over_frame = self.frames["GameOverScreen"]
        game_over_frame.set_score(final_score)
        self.show_frame("GameOverScreen")


if __name__ == "__main__":
    app = GameManager()
    app.mainloop()