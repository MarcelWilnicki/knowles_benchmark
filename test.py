import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import csv
import time
import os

from IPython.display import Audio
from scipy.signal import resample
from scipy.io import wavfile

# model documentation: https://tfhub.dev/google/yamnet/1

# Load the model.
model = hub.load('https://tfhub.dev/google/yamnet/1')


def class_names_from_csv(class_map_csv_text):
    """Returns list of class names corresponding to score vector."""
    class_names = []
    with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_names.append(row['display_name'])

    return class_names


def ensure_sample_rate(original_sample_rate, waveform,
                       desired_sample_rate=16000):
    """Resample waveform if required."""
    if original_sample_rate != desired_sample_rate:
        desired_length = int(round(float(len(waveform)) /
                                   original_sample_rate * desired_sample_rate))
        waveform = resample(waveform, desired_length)
    return desired_sample_rate, waveform


class_map_path = model.class_map_path().numpy()
class_names = class_names_from_csv(class_map_path)

for file in os.listdir('/onspecta/dev/knowles_benchmark/sounds/'):
    if file.endswith('.wav'):
        print(file)
        continue

# wav_file_name = 'speech_whistling2.wav'
wav_file_name = 'sounds/marimba.wav'
sample_rate, wav_data = wavfile.read(wav_file_name, 'rb')
sample_rate, wav_data = ensure_sample_rate(sample_rate, wav_data)

# Show some basic information about the audio.
duration = len(wav_data) / sample_rate
print(f'Sample rate: {sample_rate} Hz')
print(f'Total duration: {duration:.2f}s')
print(f'Size of the input: {len(wav_data)}')

# Listening to the wav file.
Audio(wav_data, rate=sample_rate)

# The wav_data needs to be normalized to values in [-1.0, 1.0]
waveform = wav_data / tf.int16.max

# Run the model, check the output.
start = time.time()
scores, embeddings, spectrogram = model(waveform)
finish = time.time()

inference_time = finish - start

scores_np = scores.numpy()
spectrogram_np = spectrogram.numpy()
infered_class = class_names[scores_np.mean(axis=0).argmax()]
print(f'The main sound is: {infered_class}')

print(f'Inference time was: {inference_time} seconds')
