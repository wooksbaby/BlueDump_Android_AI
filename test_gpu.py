import tensorflow as tf

# TensorFlow 버전 및 GPU 디바이스 확인
print("TensorFlow Version:", tf.__version__)

# GPU 사용 가능 여부 확인
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"GPUs are available: {len(gpus)}")
    for gpu in gpus:
        print(f"GPU Name: {gpu.name}")
else:
    print("No GPUs found")
