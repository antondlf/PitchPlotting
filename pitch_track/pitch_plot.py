from flask import  jsonify
from flask import(
    Blueprint, flash, jsonify, request, url_for
)
import tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import parselmouth as praat
from urllib.parse import quote

# def pitch_track():
#
#     # Save the file that was sent, and read it into a parselmouth.Sound
#     with tempfile.NamedTemporaryFile() as tmp:
#         tmp.write(request.files['audio'].read())
#         sound = praat.Sound(tmp.name)
#
#     # Calculate the pitch track with Parselmouth
#     pitch_track = sound.to_pitch().selected_array['frequency']
#
#     # Convert the NumPy array into a list, then encode as JSON to send back
#     return jsonify(list(pitch_track))


def load_json_as_np(path):

    with open(path) as in_file:
        data = json.load(in_file)
    return np.asarray(data)


def draw_pitch(new_pitch, old_pitch, path):
    """This function plots pitch from a praat sound object
    inputs
    _________________
    The new_pitch will be recorded when the script is run
    The old_pitch is the target audio that the student is given
    """
    # Extract selected pitch contour, and
    pitch_values_new = new_pitch.selected_array['frequency']
    # replace unvoiced samples by NaN to not plot
    pitch_values_new[pitch_values_new == 0] = np.nan

    # Repeat the actions above for the other pitch sample
    pitch_values_old = old_pitch.selected_array['frequency']
    pitch_values_old[pitch_values_old == 0] = np.nan

    plt.clf()
    # create a plot object for new_pitch with label "You"
    new_pitch_plot = plt.plot(new_pitch.xs() - 2, pitch_values_new, 'o', label='You', markersize=5, color='blue')
    #plt.plot(new_pitch.xs(), pitch_values_new, 'o', label = 'You', markersize=2)

    # create a plot object for old_pitch with label "Target"
    old_pitch_plot = plt.plot(old_pitch.xs(), pitch_values_old, 'o', label='Target', markersize=5, color='orange')
    #plt.plot(old_pitch.xs(), pitch_values_old, 'o', label = 'Target', markersize=2)

    # Create legends
    first_legend = plt.legend(handles=new_pitch_plot)

    plt.gca().add_artist(first_legend)

    # Second legend on the lower right corner
    plt.legend(handles=old_pitch_plot, loc='lower right')
    plt.grid(False)
    # Set the plot's bounds
    plt.ylim(0, max(new_pitch.ceiling, old_pitch.ceiling))
    plt.ylabel("fundamental frequency [Hz]")
    plt.savefig(path)
    return path


def plot_pitch(new_audio_path, old_audio_path):
    """This function takes in two audio samples and turns them into
    a pitch plot"""
    old_pitch = praat.Sound(old_audio_path).to_pitch()
    # spectrogram = old_audio.to_spectrogram()
    draw_pitch(new_audio_path, old_pitch)
    # draw_spectrogram(spectrogram, pitch, dynamic_range = 70)


def main(original_audio, new_audio):
    """Our main function here runs record() inside plot_pitch to provide
    the new_audio, and then as a hardcoded input uses the original audio."""
    target_audio = praat.Sound(original_audio)
    recorded_audio = praat.Sound(new_audio)
    #duration = target_audio.get_total_duration() + 1
    plot_pitch(recorded_audio, target_audio)
