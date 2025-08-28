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
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.debug = False # デバッグモード用のフラグ
        self.prompt_index = 0 # デバッグモード用のお題インデックス

        # --- アスペクト比維持のための変数 ---
        self.video_container_width = 1
        self.video_container_height = 1

        # --- スタイルの設定 (ゲージの太さと背景色) ---
        style = ttk.Style(self)
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

    def start_game_loop(self, debug=False):
        """ゲームループを開始し、カメラを初期化する"""
        self.debug = debug
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            self.controller.show_game_over_screen(self.score)
            return
        
        # タイマーとスコアをリセット
        self.start_time = time.time()
        self.score = 0
        self.score_label.config(text=f"Score: {self.score}")
        self.last_gauge_change_time = time.time()
        if self.debug_label:
            self.debug_label.config(text="")

        # デバッグモードに応じてタイマーの表示を切り替え
        if self.debug:
            self.numerical_timer_label.grid_remove()
            self.gauge_timer.grid_remove()
        else:
            self.numerical_timer_label.grid()
            self.gauge_timer.grid()
            self.numerical_timer_label.config(text="01:00")

        # お題をリセット
        if self.debug:
            self.prompt_index = 0
            self.current_prompt_text = self.pose_list[self.prompt_index]
        else:
            self.current_prompt_text = random.choice(self.pose_list)
        self.prompt_display_label.config(text=f"Make a {self.current_prompt_text} sign")

        self.running = True
        self.update_game()

    def stop_game_loop(self):
        """ゲームループを停止し、リソースを解放する"""
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def _create_widgets(self):
        """UIウィジェットを作成し、画面に配置する (gridシステムを使用)"""
        main_container = ttk.Frame(self, style='TFrame')
        main_container.pack(fill=tk.BOTH, expand=True)

        main_container.columnconfigure(0, weight=0)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=0)
        main_container.rowconfigure(1, weight=0)
        main_container.rowconfigure(2, weight=0)
        main_container.rowconfigure(3, weight=1)

        self.score_label = ttk.Label(main_container, text=f"Score: {self.score}", font=("Helvetica", 18, "bold"), style='TLabel')
        self.score_label.grid(row=0, column=1, pady=5, sticky="nw", padx=(20, 0))

        self.debug_label = ttk.Label(main_container, text="", font=("Helvetica", 14), style='TLabel', foreground="red")
        self.debug_label.grid(row=0, column=1, pady=(40,5), sticky="nw", padx=(20, 0))

        main_menu_button = ttk.Button(main_container, text="Main Menu", command=lambda: self.controller.show_frame("GameStartScreen"))
        main_menu_button.grid(row=0, column=1, pady=10, padx=10, sticky="ne")

        self.numerical_timer_label = tk.Label(main_container, text="01:00", font=("Courier", 24, "bold"), bg="#f0f0f0", fg="black", borderwidth=2, relief="sunken", padx=10)
        self.numerical_timer_label.grid(row=1, column=1, pady=5, sticky="n")

        self.prompt_display_label = ttk.Label(main_container, text=f"Make a {self.current_prompt_text} sign", font=("Helvetica", 28, "bold"), foreground="white", style='TLabel')
        self.prompt_display_label.grid(row=2, column=1, pady=10, sticky="n")

        left_frame = ttk.Frame(main_container, width=50, style='TFrame')
        left_frame.grid(row=3, column=0, sticky="ns", padx=10, pady=10)
        left_frame.grid_propagate(False)
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)

        self.gauge_timer = ttk.Progressbar(left_frame, orient='vertical', mode='determinate')
        self.gauge_timer.grid(row=0, column=0, sticky="nswe")
        self.gauge_timer['value'] = 100

        self.center_frame = ttk.Frame(main_container, style='TFrame')
        self.center_frame.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)
        self.video_label = ttk.Label(self.center_frame)
        self.video_label.pack(side=tk.BOTTOM)

        self.center_frame.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.video_container_width = event.width
        self.video_container_height = event.height

    def update_numerical_timer(self):
        elapsed_time = int(time.time() - self.start_time)
        remaining_seconds = 60 - elapsed_time
        if remaining_seconds < 0:
            remaining_seconds = 0
        
        if remaining_seconds == 0:
            self.on_closing()
            return

        minutes, seconds = divmod(remaining_seconds, 60)
        time_string = f"{minutes:02d}:{seconds:02d}"
        self.numerical_timer_label.config(text=time_string)

    def update_gauge_timer(self):
        current_time = time.time()
        self.gauge_timer_percent = 100 - ((current_time - self.last_gauge_change_time) % self.gauge_cycle_duration) * (100 / self.gauge_cycle_duration)
        self.gauge_timer['value'] = self.gauge_timer_percent

        if (current_time - self.last_gauge_change_time) >= self.gauge_cycle_duration:
            self._change_prompt()
            self.last_gauge_change_time = current_time

    def _change_prompt(self):
        """お題を変更する"""
        if self.debug:
            self.prompt_index = (self.prompt_index + 1) % len(self.pose_list)
            new_prompt = self.pose_list[self.prompt_index]
        else:
            available_prompts = [p for p in self.pose_list if p != self.current_prompt_text]
            if not available_prompts:
                return
            new_prompt = random.choice(available_prompts)

        self.current_prompt_text = new_prompt
        self.prompt_display_label.config(text=f"Make a {self.current_prompt_text} sign")

    def update_game(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            container_w = self.video_container_width * 0.8
            container_h = self.video_container_height * 0.8

            target_w = int(container_w)
            target_h = int(container_w / 16 * 9)

            if target_h > container_h:
                target_h = int(container_h)
                target_w = int(container_h / 9 * 16)
            
            if target_w > 0 and target_h > 0:
                frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)

            processed_frame, label, confidence = self.recognizer.recognize(frame, debug=self.debug)

            if self.debug:
                self.debug_label.config(text=f"Debug: {label} ({confidence:.2f})")

            self.photo = self._cv2_to_imagetk(processed_frame)
            self.video_label.config(image=self.photo)

            current_time = time.time()
            if label == self.current_prompt_text and \
               confidence > self.match_threshold and \
               (current_time - self.last_matched_prompt_time) > self.match_cooldown:
                
                self.score += 1
                self.score_label.config(text=f"Score: {self.score}")

                self._change_prompt()
                self.last_matched_prompt_time = current_time
                self.last_gauge_change_time = current_time

        if not self.debug:
            self.update_numerical_timer()
            self.update_gauge_timer()

        self.after(15, self.update_game)

    def _cv2_to_imagetk(self, frame):
        cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_image)
        return ImageTk.PhotoImage(image=pil_image)

    def on_closing(self):
        self.stop_game_loop()
        self.controller.show_game_over_screen(self.score)