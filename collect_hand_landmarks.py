import cv2
import mediapipe as mp
import pandas as pd
import os

csv_file = "hand_landmarks.csv"

# MediaPipe Handsのセットアップ
mp_hands = mp.solutions.hands
hands = mp_hands.Hands( static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# カメラのセットアップ
cap = cv2.VideoCapture(0)

# 手の座標データを収集
landmarks_data = []

def collect_landmarks( label):
    global landmarks_data
    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print( "Failed to capture image")
            break

        # 画像を水平方向に反転
        frame = cv2.flip( frame, 1)

        # 画像をRGBに変換
        image = cv2.cvtColor( frame, cv2.COLOR_BGR2RGB)

        # 手のランドマークの検出
        results = hands.process( image)

        # 画像をBGRに戻す
        frame = cv2.cvtColor( image, cv2.COLOR_RGB2BGR)

        # ランドマークが検出された場合、データを収集
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.extend( [ lm.x, lm.y, lm.z])
                landmarks.append( label)
                landmarks_data.append( landmarks)
                mp_drawing.draw_landmarks( frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                count += 1
                print( f"Collected {count} images for {label}")

        # 画像を表示
        cv2.imshow( 'Hand Landmarks', frame)

        # 'q'キーが押されたら終了
        if cv2.waitKey( 1) & 0xFF == ord( 'q'):
            break

    print( f'Collected { len( landmarks_data)} data points for {label}')

# データ収集のための指示    
word = ["a","i","u","e","o","ka","ki","ku","ke","ko","sa","si","su","se","so","ta","ti","tu","te","to","na","ni","nu","ne","no","ha","hi","hu","he","ho","ma","mi","mu","me","mo","ya","yu","yo","ra","ri","ru","re","ro","wa","wo","n"]
for i in word:
    input(f"Press Enter to collect data for {i}...")
    collect_landmarks(i)

# データをCSVファイルに保存
try:
    columns = [f'x{i}' for i in range( 21)] + [f'y{i}' for i in range( 21)] + [f'z{i}' for i in range( 21)] + ['label']
    df = pd.DataFrame( landmarks_data, columns=columns)
    df.to_csv( csv_file, index=False)
    print( f'Data saved successfully to { csv_file}')
except Exception as e:
    print( f'Error saving data: {e}')

# リソースの解放
cap.release()
cv2.destroyAllWindows()


