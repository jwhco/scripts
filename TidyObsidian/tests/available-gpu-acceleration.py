import tensorflow as tf
import torch

def check_tensorflow_gpu():
    tf_available = tf.config.list_physical_devices('GPU')
    if tf_available:
        print(f"TensorFlow can use the GPU: {len(tf_available)} GPUs detected.")
    else:
        print("TensorFlow does not detect a GPU.")

def check_pytorch_gpu():
    if torch.cuda.is_available():
        print(f"PyTorch can use the GPU: {torch.cuda.device_count()} GPUs detected.")
    else:
        print("PyTorch does not detect a GPU.")

if __name__ == "__main__":
    check_tensorflow_gpu()
    check_pytorch_gpu()
