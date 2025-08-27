import tkinter as tk

# --- switch_frame : 画面を切り替えるための関数

class AppState:
    mode = False
    selected_index = None

class StartScreen(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        tk.Label(self, text="これはスタート画面(仮)です", font=("Arial", 16)).pack(pady=20)

        self.mode_var = tk.BooleanVar(value=False)  # 初期値: False
        self.mode_button = tk.Checkbutton(
            self,
            text="Mode Select (ON/OFF)",
            variable=self.mode_var,
            onvalue=True,
            offvalue=False,
            indicatoron=False,  # ← トグルボタン風
            width=20,
            height=2
        )
        self.mode_button.pack(pady=10)

        # スタートボタン
        self.start_button = tk.Button(self, text="スタート画面", command=self.show_choices)
        self.start_button.pack(pady=20)

        # 選択肢を置くための空間
        self.choice_frame = tk.Frame(self)
        self.choice_frame.pack(pady=10)

        self.options = ["かんたん", "ふつう", "むずかしい"]
        self.selected_var = tk.IntVar(value=-1)

        tk.Button(root, text="状態を確認(デバッグ用)", command=self.check_mode).pack(pady=10)
        tk.Button(root, text="遊び方説明", command=self.make_info).pack(pady=10)

        # 決定ボタン
        self.confirm_button = tk.Button(self, text="決定", command=self.save_selection)
        # 最初は非表示
        self.confirm_button.pack_forget()
    
    def get_mode(self):
        return self.mode_var.get()

    def show_info(self):
        # 新しいウィンドウを作る
        info_win = tk.Toplevel(self)
        info_win.title("アプリの説明")
        info_win.geometry("300x200")
        tk.Label(info_win, text="アプリの説明", wraplength=250).pack(pady=20)
        tk.Button(info_win, text="閉じる", command=info_win.destroy).pack(pady=10)

    # メインから状態を確認するためのボタン
    def check_mode():
        print("ModeSelect の状態:", app.get_mode())

    # 説明用のウィンドウを作成
    def make_info():
        app.show_info()

    def show_choices(self):
        # スタートボタンを無効化
        self.start_button.config(state="disabled")

        # 選択肢のボタンを動的生成
        for i, option in enumerate(self.options):
            btn = tk.Button(
                self.choice_frame,
                text=option,
                width=20,
                height=2,
                command=lambda index=i: self.save_selection(index)
            )
            btn.pack(pady=5)
    
    # 選択した難易度を保存
    def save_selection(self, index):
        AppState.selected_index = index
        print("DifficultIndex: ", AppState.selected_index)



root = tk.Tk()
app = StartScreen(master=root)

app.pack()
app.mainloop()