import tensorflow as tf
import numpy as np
import io
import csv
import os

from scipy.io import wavfile
from scipy.signal import resample
# Download the model to yamnet.tflite
# path on graviton inside docker
interpreter = tf.lite.Interpreter('/onspecta/dev/knowles_benchmark/lite-model_yamnet_tflite_1.tflite')


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

input_details = interpreter.get_input_details()
waveform_input_index = input_details[0]['index']
output_details = interpreter.get_output_details()
scores_output_index = output_details[0]['index']
embeddings_output_index = output_details[1]['index']
spectrogram_output_index = output_details[2]['index']

# Input: 3 seconds of silence as mono 16 kHz waveform samples.
waveform = np.zeros(3 * 16000, dtype=np.float32)

# wav_file_name = 'sounds/cough.wav'
# print(wav_file_name)
# sample_rate, wav_data = wavfile.read(wav_file_name, 'rb')
# sample_rate, wav_data = ensure_sample_rate(sample_rate, wav_data)
#
# waveform = wav_data / tf.int16.max
#
# print(type(waveform))

interpreter.resize_tensor_input(waveform_input_index, [len(waveform)], strict=True)
interpreter.allocate_tensors()
interpreter.set_tensor(waveform_input_index, waveform)
interpreter.invoke()
scores, embeddings, spectrogram = (
    interpreter.get_tensor(scores_output_index),
    interpreter.get_tensor(embeddings_output_index),
    interpreter.get_tensor(spectrogram_output_index))

print(scores.shape, embeddings.shape, spectrogram.shape)  # (N, 521) (N, 1024) (M, 64)

# Download the YAMNet class map (see main YAMNet model docs) to yamnet_class_map.csv
# See YAMNet TF2 usage sample for class_names_from_csv() definition.
# class_names = class_names_from_csv(open('/onspecta/dev/knowles_benchmark/yamnet_class_map.csv').read())
# print(class_names[scores.mean(axis=0).argmax()])  # Should print 'Silence'.


