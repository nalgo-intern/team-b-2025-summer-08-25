import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import time

# discrimination.pyからジェスチャー認識クラスをインポート
from discrimination import GestureRecognizer

class GameApplication:
    """
    Tkinterをベースにしたゲームアプリケーションのメインクラス。
    """
    def __init__(self, root):
        """アプリケーションの初期化"""
        self.root = root
        self.root.title("Janken Game")
        self.root.configure(bg='#f0f0f0') # 背景色
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- タイマー変数の初期化 ---
        self.start_time = time.time()
        self.numerical_timer_value = 60 # 60秒からスタート
        self.gauge_timer_percent = 100 # 100%からスタート

        # --- ジェスチャー認識クラスの初期化 ---
        self.recognizer = GestureRecognizer(model_path='model.h5')

        # --- カメラの初期化 ---
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            self.root.destroy()
            return

        # --- UIウィジェットの作成と配置 ---
        self._create_widgets()

        # --- メインループの開始 ---
        self.update_game()

    def _create_widgets(self):
        """UIウィジェットを作成し、画面に配置する"""
        # --- 上部フレーム (数値タイマー) ---
        top_frame = ttk.Frame(self.root, padding=(10, 10))
        top_frame.pack(fill=tk.X)
        self.numerical_timer_label = ttk.Label(top_frame, text=f"Time: {self.numerical_timer_value}", font=("Helvetica", 18, "bold"))
        self.numerical_timer_label.pack()

        # --- 中央のメインフレーム (左右のスペースをここで作る) ---
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 左フレーム (ゲージタイマー) ---
        left_frame = ttk.Frame(main_frame, padding=(10, 0))
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.gauge_timer = ttk.Progressbar(left_frame, orient='vertical', length=480, mode='determinate')
        self.gauge_timer['value'] = self.gauge_timer_percent
        self.gauge_timer.pack(fill=tk.Y, expand=True)

        # --- 中央フレーム (映像) ---
        center_frame = ttk.Frame(main_frame, padding=(20, 0))
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.video_label = ttk.Label(center_frame)
        self.video_label.pack(anchor=tk.CENTER, expand=True)

        # --- 認識結果ラベルを映像の下に配置 ---
        self.result_label = ttk.Label(center_frame, text="Detected: unknown (0.0%)", font=("Helvetica", 14))
        self.result_label.pack(pady=10)

    def update_numerical_timer(self):
        """数値タイマーを更新する機能"""
        elapsed_time = int(time.time() - self.start_time)
        self.numerical_timer_value = 60 - elapsed_time
        if self.numerical_timer_value < 0:
            self.numerical_timer_value = 0
        self.numerical_timer_label.config(text=f"Time: {self.numerical_timer_value}")

    def update_gauge_timer(self):
        """ゲージタイマーを更新する機能"""
        # 例として、5秒で1サイクルするゲージを実装
        self.gauge_timer_percent = 100 - ((time.time() - self.start_time) % 5) * 20
        self.gauge_timer['value'] = self.gauge_timer_percent

    def update_game(self):
        """ゲームの状態を更新し、UIに反映する (メインループ)"""
        # カメラからフレームを読み込み
        ret, frame = self.cap.read()
        if ret:
            # ジェスチャー認識を実行
            processed_frame, label, confidence = self.recognizer.recognize(frame)

            # 映像をTkinter用に変換して表示
            self.photo = self._cv2_to_imagetk(processed_frame)
            self.video_label.config(image=self.photo)

            # 認識結果をラベルに表示
            result_text = f"Detected: {label} ({confidence * 100:.1f}%)"
            self.result_label.config(text=result_text)
        else:
            print("Failed to capture frame.")

        # --- タイマー機能の呼び出し ---
        self.update_numerical_timer()
        self.update_gauge_timer()

        # 15ms後にもう一度この関数を呼び出す
        self.root.after(15, self.update_game)

    def _cv2_to_imagetk(self, frame):
        """OpenCVの画像をTkinterのPhotoImageに変換する"""
        cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_image)
        return ImageTk.PhotoImage(image=pil_image)

    def on_closing(self):
        """アプリケーション終了時の処理"""
        print("Releasing resources...")
        if self.cap.isOpened():
            self.cap.release()
        if self.recognizer:
            self.recognizer.release()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = GameApplication(root)
    root.mainloop()