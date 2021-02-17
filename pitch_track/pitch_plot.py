import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import parselmouth as praat
import seaborn as sns

sns.set()

def trim_recording(pitch:np.array) -> tuple:
    """Trims the front zeros from the pitch array and the corresponding
    time values."""


    array = pitch.selected_array['frequency']
    trimmed_pitch = np.trim_zeros(array, 'f')

    trim = array.shape[0] - trimmed_pitch.shape[0]
    time = pitch.xs()
    trimmed_time = time[trim:]

    # Subtract time values
    norm = min(trimmed_time)
    trimmed_time = trimmed_time - norm


    return trimmed_pitch, trimmed_time

def pitch_difference(pitch_values_old, pitch_values_new):
    """Generate a number to add to pitch_values_old so that
    graphs don't clash."""


    pitch_floor_new = min(pitch_values_new)
    pitch_ceiling_old = max(pitch_values_old)

    if  pitch_floor_new - 100 < pitch_ceiling_old:
        scaling_factor = (pitch_ceiling_old - pitch_floor_new) + 100
        pitch_values_new += scaling_factor

    return pitch_values_old



def draw_pitch(new_pitch, old_pitch, path):
    """This function plots pitch from a praat sound object
    inputs
    _________________
    The new_pitch will be recorded when the script is run
    The old_pitch is the target audio that the student is given
    """

    # Clear figure to avoid cached plots
    plt.clf()

    # Extract selected pitch contour, and
    pitch_values_new, time_new = trim_recording(new_pitch)
    # replace unvoiced samples by NaN to not plot
    pitch_values_new[pitch_values_new == 0] = np.nan

    # Repeat the actions above for the other pitch sample
    pitch_values_old, time_old = trim_recording(old_pitch)
    pitch_values_old[pitch_values_old == 0] = np.nan

    # Make sure graphs don't clash
    pitch_values_old = pitch_difference(pitch_values_old, pitch_values_new)

    plt.clf()
    # create a plot object for new_pitch with label "You"
    plt.plot(time_new, pitch_values_new, 'o', markersize=5, color='w')
    new_pitch_plot = plt.plot(time_new, pitch_values_new, 'o', label='You', markersize=2, color='b')

    # create a plot object for old_pitch with label "Target"
    plt.plot(time_old, pitch_values_old, 'o', markersize=5, color='w')
    old_pitch_plot = plt.plot(time_old, pitch_values_old, 'o', label='Target', markersize=2, color='y')

    # Create legends
    first_legend = plt.legend(handles=new_pitch_plot)

    plt.gca().add_artist(first_legend)

    # Second legend on the lower right corner
    plt.legend(handles=old_pitch_plot, loc='lower right')
    plt.grid(False)
    # Set the plot's bounds
    plt.ylim(0, max(max(pitch_values_old), max(pitch_values_new)) + 10)
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
