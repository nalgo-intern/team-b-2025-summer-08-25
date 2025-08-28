import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

# データを読み込む
df = pd.read_csv( "hand_landmarks_merged.csv")

# 特徴量（X）とラベル（y）に分ける
X = df.drop( 'label', axis=1).values
y = df['label'].values

# ラベルを数値にエンコード
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform( y)
print(y_encoded[400])

# OHE
y_categorical = to_categorical( y_encoded, num_classes=41)#ここを変える

# 訓練データとテストデータに分割
X_train, X_test, y_train, y_test = train_test_split( X, y_categorical, test_size=0.2, random_state=42)



# モデルの構築
model = Sequential()

# 入力層
model.add(Dense( 128, input_shape=(X_train.shape[1],), activation='relu'))

# 中間層
model.add(Dense( 64, activation='relu'))
model.add(Dropout( 0.3))  # 過学習防止のためのDropout層

model.add(Dense( 64, activation='relu'))
model.add(Dropout( 0.3))

# 出力層 
model.add(Dense( 41, activation='softmax'))#ここを変える

# モデルのコンパイル
model.compile( optimizer='adam', loss='categorical_crossentropy', metrics=[ 'accuracy'])

# モデルの概要を表示
model.summary()

# モデルの学習
history = model.fit( X_train, y_train, epochs=10, batch_size=32, validation_data=( X_test, y_test))

# モデルの評価
loss, accuracy = model.evaluate( X_test, y_test)
print( f"Test Accuracy: {accuracy * 100:.2f}%")

#モデルの保存
model.save( 'model.h5')
