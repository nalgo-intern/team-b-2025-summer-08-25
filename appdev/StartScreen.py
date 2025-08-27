import tkinter as tk
from tkinter import ttk

# --- switch_frame : 画面を切り替えるための関数
# 選択した難易度、アシストの有無を保存

class AppState:
    mode = False
    selected_index = None

class StartScreen(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        master.geometry("1200x600")
        tk.Label(self.master, text="これはスタート画面(仮)です", font=("Arial", 16)).pack(pady=20)
        

        self.mode_var = tk.BooleanVar(value=False)  # 初期値: False
        self.mode_button = tk.Checkbutton(
            self,
            text="アシストモード",
            variable=self.mode_var,
            onvalue=True,
            offvalue=False,
            indicatoron=False,  # ← トグルボタン風
            width=20,
            height=2,
            command=self.check_assist
        )
        self.mode_button.place(relx=0.5, rely=0.8, x=-10)

        # スタートボタン
        self.start_button = tk.Button(
            self.master,
            text="スタート画面",
            width=40,
            height=5,
            command=self.show_choices
            )
        self.start_button.place(relx=0.5, rely=0.2, x=-140)

        # 選択肢を置くための空間
        self.choice_frame = tk.Frame(self)
        self.choice_frame.pack(pady=10)

        self.options = ["Easy", "Medium", "Hard"]
        self.selected_var = tk.IntVar(value=-1)

        self.debug_button = tk.Button(root, text="状態を確認(デバッグ用)", command=self.check_mode)
        self.introduction = tk.Button(root, text="遊び方説明", command=self.make_info)
        self.debug_button.pack(pady=20, side = "left")
        self.introduction.place(relx=0.5, rely=0.8, x=-20)

        # 決定ボタン
        self.confirm_button = tk.Button(self, text="決定", command=self.save_selection)
        # 最初は非表示
        self.confirm_button.pack_forget()

        # アプリ終了ボタン
        master.update_idletasks()
        self.quit_button = tk.Button(self.master, text="アプリを閉じる", command=self.master.destroy)
        self.quit_button.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)
    
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
    def check_mode(self):
        print("ModeSelect の状態:", app.get_mode())

    # 説明用のウィンドウを作成
    def make_info(self):
        self.show_info()

    # アシストの有無の状態をスタート画面に表示
    def check_assist(self):
        if self.mode_var.get():
            self.mode_button.config(text="アシスト：あり")
        else:
            self.mode_button.config(text="アシスト：なし")

    def show_choices(self):
        # スタートボタンを無効化
        self.start_button.config(state="disabled")

        # 選択肢のボタンを動的生成
        for i, option in enumerate(self.options):
            btn = tk.Button(
                self.master,
                text=option,
                width=20,
                height=2,
                command=lambda index=i: self.save_selection(index)
            )
            btn.place(relx=0.5, rely=0.4+0.08*i, x=-50)
    
    # 選択した難易度を保存
    def save_selection(self, index):
        AppState.selected_index = index
        AppState.mode = self.get_mode()
        print("DifficultIndex: ", AppState.selected_index)
        print("Assist: ", AppState.mode)



root = tk.Tk()
app = StartScreen(master=root)

app.pack()
app.mainloop()