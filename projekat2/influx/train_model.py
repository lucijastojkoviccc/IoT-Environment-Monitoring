import numpy as np
import tensorflow as tf

# Ulazi: brightness, contrast
# Klase:
# 0 = dark    -> kamera je pokrivena / veoma malo svetla
# 1 = normal  -> uredaj stoji normalno na stolu
# 2 = bright  -> jako svetlo direktno u kameru
# 3 = anomaly -> neuobicajena ili nagla promena scene

X = np.array([
    # DARK - prst preko kamere
    [2, 11],
    [3, 13],
    [4, 14],
    [6, 10],
    [10, 13],
    [9, 11],
    [10, 14],
    [15, 13],
    [6, 27],
    [8, 24],
    [7, 18],

    # NORMAL - uredaj stoji na stolu
    [92, 163],
    [94, 162],
    [93, 158],
    [94, 163],
    [94, 158],
    [93, 160],
    [94, 160],
    [94, 164],
    [93, 153],
    [94, 156],
    [94, 160],

    # BRIGHT - svetlo telefona direktno ka kameri
    [250, 4],
    [252, 2],
    [253, 9],
    [247, 4],
    [255, 2],
    [241, 1],
    [255, 0],
    [251, 4],
    [250, 1],
    [247, 6],

    # ANOMALY - neuobicajene kombinacije koje nisu tipicne za tvoja 3 stabilna stanja
    # npr. srednji brightness sa veoma malim kontrastom,
    # veoma visok brightness sa velikim kontrastom,
    # ili vrlo nizak brightness sa velikim kontrastom
    [40, 160],
    [50, 180],
    [70, 220],
    [120, 10],
    [130, 20],
    [150, 30],
    [180, 200],
    [210, 180],
    [230, 160],
    [250, 160],
    [20, 150],
    [10, 120],
], dtype=np.float32)

y = np.array([
    # DARK
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,

    # NORMAL
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,

    # BRIGHT
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2,

    # ANOMALY
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3
], dtype=np.int32)

# Normalizacija na opseg 0-1
X[:, 0] = X[:, 0] / 255.0
X[:, 1] = X[:, 1] / 255.0

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(2,)),
    tf.keras.layers.Dense(16, activation="relu"),
    tf.keras.layers.Dense(16, activation="relu"),
    tf.keras.layers.Dense(4, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.fit(X, y, epochs=700, verbose=0)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open("light_model.tflite", "wb") as f:
    f.write(tflite_model)

print("TFLite model saved as light_model.tflite")
