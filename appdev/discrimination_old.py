import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

class GestureRecognizer:
    """
    手のジェスチャーを認識するためのクラス。
    モデルの読み込み、MediaPipeの初期化、フレームごとの認識処理をカプセル化する。
    """
    def __init__(self, model_path='model.h5'):
        """
        クラスの初期化。モデルとMediaPipeをセットアップする。
        Args:
            model_path (str): 使用する学習済みモデルのパス。
        """
        # MediaPipe Handsのセットアップ
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # モデルの読み込み
        try:
            self.model = load_model(model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            print(f"Please ensure the model file exists at: {model_path}")
            self.model = None

    def _extract_landmark_data(self, hand_landmarks):
        """手のランドマークを1次元のリストに変換する"""
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        return landmarks

    def _predict_hand_shape(self, landmarks):
        """ランドマークデータから手の形を予測する"""
        if self.model is None:
            return "Model not loaded", 0.0

        # ランドマークデータを正しい形に変換
        landmarks_array = np.array(landmarks).reshape(1, -1)

        # モデルで予測
        prediction = self.model.predict(landmarks_array)
        predicted_class = np.argmax(prediction)
        confidence = prediction[0][predicted_class]

        # ラベルを返す (仮のラベル、必要に応じて変更)
        if predicted_class == 0:
            label = "piece"
        elif predicted_class == 1:
            label = "thumbs up"
        else:
            label = "unknown"

        return label, confidence

    def recognize(self, frame):
        """
        与えられたフレームに対してジェスチャー認識を行う。

        Args:
            frame: 入力となるOpenCVのフレーム。

        Returns:
            tuple: (処理後のフレーム, 予測ラベル, 信頼度)
        """
        # デフォルトの戻り値
        label = "unknown"
        confidence = 0.0

        # 画像を水平方向に反転し、RGBに変換
        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 手のランドマークの検出
        results = self.hands.process(image_rgb)

        # ランドマークが検出された場合、手の形を判別
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # ランドマークを描画
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                # 予測を実行
                landmarks_data = self._extract_landmark_data(hand_landmarks)
                label, confidence = self._predict_hand_shape(landmarks_data)

        return frame, label, confidence

    def release(self):
        """リソースを解放する"""
        self.hands.close()