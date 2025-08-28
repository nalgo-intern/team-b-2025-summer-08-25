import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import time
import random # randomモジュールをインポート

# discrimination.pyからジェスチャー認識クラスをインポート
from discrimination_app import GestureRecognizer

# ★★★★★ array.txtのファイルパスを定義 ★★★★★
POSE_LIST_FILE = "array.txt"

class GamePlayScreen(tk.Frame):
    """
    Tkinterをベースにしたゲームアプリケーションのメインクラス。
    """
    def __init__(self, parent, controller):
        """アプリケーションの初期化"""
        tk.Frame.__init__(self, parent) # tk.Frameを継承
        self.controller = controller
        # self.root = root # 削除
        # self.root.title("Janken Game") # 削除
        # self.root.configure(bg='#f0f0f0') # 削除
        # self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # 削除

        # --- アスペクト比維持のための変数 ---
        self.video_container_width = 1
        self.video_container_height = 1

        # --- スタイルの設定 (ゲージの太さと背景色) ---
        style = ttk.Style(self) # self.rootからselfに変更
        style.configure('Thick.Vertical.TProgressbar', thickness=30)
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')

        # --- タイマー変数の初期化 ---
        self.start_time = time.time()
        self.numerical_timer_value = 60 # 60秒からスタート
        self.gauge_timer_percent = 100 # 100%からスタート
        self.gauge_cycle_duration = 5 # ゲージ1サイクルの時間 (秒)
        self.last_gauge_change_time = time.time() # ゲージでお題が変更された最終時刻

        # --- スコアの初期化 ---
        self.score = 0

        # --- ポーズリストの読み込みと初期お題の設定 ---
        self.pose_list = []
        try:
            with open(POSE_LIST_FILE, "r") as f:
                self.pose_list = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Warning: {POSE_LIST_FILE} not found. Using default poses.")
            self.pose_list = ["thumbs up", "piece"]
        
        if not self.pose_list:
            print(f"Warning: {POSE_LIST_FILE} is empty. Using default poses.")
            self.pose_list = ["thumbs up", "piece"]

        self.current_prompt_text = random.choice(self.pose_list)
        self.match_threshold = 0.8 # 信頼度閾値
        self.last_matched_prompt_time = 0 # 最後にマッチした時刻
        self.match_cooldown = 2 # マッチ後のクールダウン秒数

        # --- ジェスチャー認識クラスの初期化 ---
        self.recognizer = GestureRecognizer(model_path='model.h5')

        # --- カメラの初期化はstart_game_loopで行う ---
        self.cap = None # 初期化は後で行う
        self.running = False # ゲームループの実行フラグ

        # --- UIウィジェットの作成と配置 ---
        self._create_widgets()

        # --- メインループの開始はstart_game_loopで行う ---

    def start_game_loop(self):
        """ゲームループを開始し、カメラを初期化する"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            # self.controller.destroy() # アプリケーション全体を終了させる
            # カメラが開けない場合はゲームオーバー画面に遷移させるなど、適切なエラーハンドリングが必要
            self.controller.show_game_over_screen(self.score) # 仮でゲームオーバー画面へ
            return
        
        # タイマーとスコアをリセット
        self.start_time = time.time()
        self.score = 0
        self.score_label.config(text=f"Score: {self.score}")
        self.numerical_timer_label.config(text="01:00")
        self.last_gauge_change_time = time.time()

        # お題をリセット
        self.current_prompt_text = random.choice(self.pose_list)
        self.prompt_display_label.config(text=f"Make a {self.current_prompt_text} sign")

        self.running = True
        self.update_game()

    def stop_game_loop(self):
        """ゲームループを停止し、リソースを解放する"""
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        # self.recognizer.release() # recognizerは再利用可能なのでリリースしない

    def _create_widgets(self):
        """UIウィジェットを作成し、画面に配置する (gridシステムを使用)"""
        # ★★★★★ 全体を覆う「土台」のフレームを作成 ★★★★★
        main_container = ttk.Frame(self, style='TFrame') # self.rootからselfに変更
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- 土台フレームのグリッド設定 ---
        # 0列目(ゲージ)は固定幅、1列目(お題/映像/結果)がウィンドウ幅に応じて伸縮する
        main_container.columnconfigure(0, weight=0)
        main_container.columnconfigure(1, weight=1)
        # 0行目(スコア)、1行目(タイマー)、2行目(お題)、3行目(映像)がウィンドウ高さに応じて伸縮する
        main_container.rowconfigure(0, weight=0) # スコア用
        main_container.rowconfigure(1, weight=0) # タイマー用
        main_container.rowconfigure(2, weight=0) # お題用
        main_container.rowconfigure(3, weight=1) # 映像用

        # --- スコア表示ラベル (左上) ---
        self.score_label = ttk.Label(
            main_container, text=f"Score: {self.score}", 
            font=("Helvetica", 18, "bold"), 
            style='TLabel'
        )
        self.score_label.grid(row=0, column=1, pady=5, sticky="nw", padx=(20, 0)) # row=0, column=1, sticky=nw

        # --- メインメニューに戻るボタン (右上) ---
        main_menu_button = ttk.Button(
            main_container, text="Main Menu",
            command=lambda: self.controller.show_frame("GameStartScreen")
        )
        main_menu_button.grid(row=0, column=1, pady=10, padx=10, sticky="ne")

        # --- 上部タイマー (映像フレームと同じ列に配置) ---
        self.numerical_timer_label = tk.Label(
            main_container, text="01:00", font=("Courier", 24, "bold"),
            bg="#f0f0f0", fg="black", borderwidth=2, relief="sunken", padx=10
        )
        self.numerical_timer_label.grid(row=1, column=1, pady=5, sticky="n") # row=1に変更

        # --- お題表示ラベル (上部中央) ---
        self.prompt_display_label = ttk.Label(
            main_container, 
            text=f"Make a {self.current_prompt_text} sign", 
            font=("Helvetica", 28, "bold"), 
            foreground="white", # お題の色
            style='TLabel'
        )
        self.prompt_display_label.grid(row=2, column=1, pady=10, sticky="n") # row=2に変更

        # --- 左フレーム (ゲージタイマー) ---
        left_frame = ttk.Frame(main_container, width=50, style='TFrame')
        left_frame.grid(row=3, column=0, sticky="ns", padx=10, pady=10) # row=3に変更
        left_frame.grid_propagate(False)
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)

        self.gauge_timer = ttk.Progressbar(
            left_frame, orient='vertical', mode='determinate'
        )
        self.gauge_timer.grid(row=0, column=0, sticky="nswe")
        self.gauge_timer['value'] = 100 # 初期値

        # --- 中央フレーム (映像) ---
        self.center_frame = ttk.Frame(main_container, style='TFrame')
        self.center_frame.grid(row=3, column=1, sticky="nsew", padx=10, pady=10) # row=3に変更
        self.video_label = ttk.Label(self.center_frame)
        self.video_label.pack(side=tk.BOTTOM)

        # ★★★★★ 映像フレームのサイズ変更イベントをバインド ★★★★★
        self.center_frame.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        """ウィンドウリサイズ時に呼び出され、映像コンテナのサイズを記録する"""
        self.video_container_width = event.width
        self.video_container_height = event.height

    def update_numerical_timer(self):
        """数値タイマーを更新する機能"""
        elapsed_time = int(time.time() - self.start_time)
        remaining_seconds = 60 - elapsed_time
        if remaining_seconds < 0:
            remaining_seconds = 0
        
        # タイマーが0になったらアプリケーションを終了
        if remaining_seconds == 0:
            self.on_closing()
            return # 終了処理が呼ばれたらそれ以上更新しない

        minutes, seconds = divmod(remaining_seconds, 60)
        time_string = f"{minutes:02d}:{seconds:02d}"
        self.numerical_timer_label.config(text=time_string)

    def update_gauge_timer(self):
        """ゲージタイマーを更新する機能"""
        # 例として、5秒で1サイクルするゲージを実装
        current_time = time.time()
        self.gauge_timer_percent = 100 - ((current_time - self.last_gauge_change_time) % self.gauge_cycle_duration) * (100 / self.gauge_cycle_duration)
        self.gauge_timer['value'] = self.gauge_timer_percent

        # ゲージが1サイクル完了したらお題を変更
        if (current_time - self.last_gauge_change_time) >= self.gauge_cycle_duration:
            self._change_prompt_randomly()
            self.last_gauge_change_time = current_time # ゲージのサイクル開始時刻をリセット

    def _change_prompt_randomly(self):
        """お題をランダムに選択し、表示を更新するヘルパー関数"""
        # 現在のお題を除外したリストを作成
        available_prompts = [p for p in self.pose_list if p != self.current_prompt_text]

        # もし異なるお題が選択肢にない場合、何もしない
        if not available_prompts:
            return

        new_prompt = random.choice(available_prompts)
        self.current_prompt_text = new_prompt
        self.prompt_display_label.config(text=f"Make a {self.current_prompt_text} sign")

    def update_game(self):
        """ゲームの状態を更新し、UIに反映する (メインループ)"""
        # ★★★★★ ゲームループが停止中の場合は何もしない ★★★★★
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            # ★★★★★ 16:9のアスペクト比を維持してリサイズ (7割のサイズで) ★★★★★
            # コンテナの幅と高さの80%をターゲットサイズとする
            container_w = self.video_container_width * 0.8
            container_h = self.video_container_height * 0.8

            # 70%のエリアに収まる最大の16:9サイズを計算
            target_w = int(container_w)
            target_h = int(container_w / 16 * 9)

            if target_h > container_h:
                target_h = int(container_h)
                target_w = int(container_h / 9 * 16)
            
            # target_w, target_hが0以下にならないように保護
            if target_w > 0 and target_h > 0:
                frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)

            # ジェスチャー認識を実行
            processed_frame, label, confidence = self.recognizer.recognize(frame)

            # 映像をTkinter用に変換して表示
            self.photo = self._cv2_to_imagetk(processed_frame)
            self.video_label.config(image=self.photo)

            # ★★★★★ お題マッチングロジック ★★★★★
            current_time = time.time()
            if label == self.current_prompt_text and \
               confidence > self.match_threshold and \
               (current_time - self.last_matched_prompt_time) > self.match_cooldown:
                
                self.score += 1 # スコア加算
                self.score_label.config(text=f"Score: {self.score}") # スコア表示更新

                self._change_prompt_randomly() # ヘルパー関数を呼び出す
                self.last_matched_prompt_time = current_time
                self.last_gauge_change_time = current_time # マッチ時もゲージのサイクルをリセット

        # --- タイマー機能の呼び出し ---
        self.update_numerical_timer()
        self.update_gauge_timer()

        self.after(15, self.update_game) # self.root.afterからself.afterに変更

    def _cv2_to_imagetk(self, frame):
        """OpenCVの画像をTkinterのPhotoImageに変換する"""
        cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_image)
        return ImageTk.PhotoImage(image=pil_image)

    def on_closing(self):
        """アプリケーション終了時の処理"""
        # print("Releasing resources...") # 削除
        self.stop_game_loop()
        self.controller.show_game_over_screen(self.score)

# if __name__ == '__main__': # 削除
#     root = tk.Tk()
#     app = GameApplication(root)
#     root.mainloop() # 削除
