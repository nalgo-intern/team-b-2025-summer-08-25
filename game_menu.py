
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
        self.root.configure(bg='#f0f0f0')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- アスペクト比維持のための変数 ---
        self.video_container_width = 1
        self.video_container_height = 1

        # --- スタイルの設定 (ゲージの太さを定義) ---
        style = ttk.Style(self.root)
        style.configure('Thick.Vertical.TProgressbar', thickness=30)

        # --- タイマー変数の初期化 ---
        self.start_time = time.time()

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
        # --- 上部フレーム (タイマーと結果) ---
        top_frame = ttk.Frame(self.root, padding=(10, 5))
        top_frame.pack(fill=tk.X)
        self.numerical_timer_label = tk.Label(
            top_frame, text="01:00", font=("Courier", 24, "bold"),
            bg="white", fg="black", borderwidth=2, relief="sunken", padx=10
        )
        self.numerical_timer_label.pack(side=tk.LEFT, padx=10)
        self.result_label = ttk.Label(top_frame, text="Detected: unknown (0.0%)", font=("Helvetica", 16))
        self.result_label.pack(side=tk.LEFT, padx=20, expand=True)

        # --- 下部のメインフレーム ---
        main_frame = ttk.Frame(self.root, padding=(10, 5, 10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 左フレーム (ゲージタイマー) ---
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.gauge_timer = ttk.Progressbar(
            left_frame, orient='vertical', length=480, mode='determinate', style='Thick.Vertical.TProgressbar'
        )
        self.gauge_timer.pack(fill=tk.Y, expand=True)

        # --- 中央フレーム (映像) ---
        self.center_frame = ttk.Frame(main_frame, relief="sunken", borderwidth=2)
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.video_label = ttk.Label(self.center_frame)
        self.video_label.pack(anchor=tk.CENTER, expand=True)

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
        if remaining_seconds < 0: remaining_seconds = 0
        minutes, seconds = divmod(remaining_seconds, 60)
        time_string = f"{minutes:02d}:{seconds:02d}"
        self.numerical_timer_label.config(text=time_string)

    def update_gauge_timer(self):
        """ゲージタイマーを更新する機能"""
        self.gauge_timer_percent = 100 - ((time.time() - self.start_time) % 5) * 20
        self.gauge_timer['value'] = self.gauge_timer_percent

    def update_game(self):
        """ゲームの状態を更新し、UIに反映する (メインループ)"""
        ret, frame = self.cap.read()
        if ret:
            # ★★★★★ 16:9のアスペクト比を維持してリサイズ ★★★★★
            # コンテナの幅と高さから、16:9に収まる最大のサイズを計算
            container_w = self.video_container_width
            container_h = self.video_container_height
            target_w = container_w
            target_h = int(container_w / 16 * 9)

            if target_h > container_h:
                target_h = container_h
                target_w = int(container_h / 9 * 16)
            
            # target_w, target_hが0以下にならないように保護
            if target_w > 0 and target_h > 0:
                frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)

            # ジェスチャー認識を実行
            processed_frame, label, confidence = self.recognizer.recognize(frame)

            # 映像をTkinter用に変換して表示
            self.photo = self._cv2_to_imagetk(processed_frame)
            self.video_label.config(image=self.photo)

            # 認識結果をラベルに表示
            result_text = f"Detected: {label} ({confidence * 100:.1f}%)"
            self.result_label.config(text=result_text)

        # --- タイマー機能の呼び出し ---
        self.update_numerical_timer()
        self.update_gauge_timer()

        self.root.after(15, self.update_game)

    def _cv2_to_imagetk(self, frame):
        """OpenCVの画像をTkinterのPhotoImageに変換する"""
        cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_image)
        return ImageTk.PhotoImage(image=pil_image)

    def on_closing(self):
        """アプリケーション終了時の処理"""
        print("Releasing resources...")
        if self.cap.isOpened(): self.cap.release()
        if self.recognizer: self.recognizer.release()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = GameApplication(root)
    root.mainloop()
