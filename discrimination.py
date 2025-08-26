import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

# Mediapipe Handsのセットアップ
mp_hands = mp.solutions.hands
hands = mp_hands.Hands( static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# モデルの読み込み
model = load_model( 'model/janken_model.h5')

# 手のランドマークを抽出する関数
def extract_landmark_data( hand_landmarks):
    landmarks = []
    for lm in hand_landmarks.landmark:
        landmarks.extend( [ lm.x, lm.y, lm.z])
    return landmarks

# 手の形を判別する関数
def predict_hand_shape( landmarks):
    # ランドマークデータを正しい形に変換
    landmarks = np.array( landmarks).reshape( 1, -1)
    
    # モデルで予測
    prediction = model.predict( landmarks)
    predicted_class = np.argmax( prediction)
    confidence = prediction[ 0][ predicted_class]  # 確率を取得

    # ラベルを返す
    if predicted_class == 0:
        label = "piece"
    elif predicted_class == 1:
        label = "thumbs up"
    else:
        label = "unknown"

    return label, confidence

# カメラのセットアップ
cap = cv2.VideoCapture( 0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 画像を水平方向に反転
    frame = cv2.flip( frame, 1)

    # 画像をRGBに変換
    image = cv2.cvtColor( frame, cv2.COLOR_BGR2RGB)

    # 手のランドマークの検出
    results = hands.process( image)

    # 画像をBGRに戻す
    frame = cv2.cvtColor( image, cv2.COLOR_RGB2BGR)

    # ランドマークが検出された場合、手の形を判別
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = extract_landmark_data( hand_landmarks)
        
            # 判別結果と確率
            hand_shape, confidence = predict_hand_shape( landmarks)
        
            # 結果を表示（% 表示）
            text = f"Predicted: {hand_shape} ( {confidence*100:.1f}%)"
            cv2.putText(frame, text, ( 10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, ( 0, 255, 0), 2, cv2.LINE_AA)
        
        # ランドマークを描画
            mp_drawing.draw_landmarks( frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    # 画像を表示
    cv2.imshow( 'result', frame)

    # 'q'キーで終了
    if cv2.waitKey( 1) & 0xFF == ord( 'q'):
        break

# リソースの解放
cap.release()
cv2.destroyAllWindows()
