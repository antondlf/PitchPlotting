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

    # Do the same for the trailing zeroes
    trimmed_pitch = np.trim_zeros(trimmed_pitch, 'b')
    trailing_trim = trimmed_pitch.shape[0]
    trimmed_time = trimmed_time[:trailing_trim]


    return trimmed_pitch, trimmed_time


def get_summary(pitch):

    average = np.mean(pitch)
    deviation = np.std(pitch)

    return average, deviation


def adjust_time_samples(new_time, old_time):
    """Get a resample of the new_pitch array to match the old pitch array."""


    new_time_normalized = new_time/(new_time.max()/old_time.max())

    return new_time_normalized


def preprocess_audio(new_pitch, old_pitch):

    pitch_new, time_new = trim_recording(new_pitch)
    pitch_old, time_old = trim_recording(old_pitch)
    new_time_normalized = adjust_time_samples(time_new, time_old)

    return pitch_new, pitch_old, new_time_normalized, time_old


def pitch_difference(pitch_values_old, pitch_values_new):
    """Generate a number to add to pitch_values_old so that
    graphs don't clash."""

    average_new, deviation_new = get_summary(pitch_values_new)
    average_old, deviation_old = get_summary(pitch_values_old)
    pitch_aver_new = np.mean(pitch_values_new[pitch_values_new <= average_new+(deviation_new*2.5)])
    pitch_aver_old = np.mean(pitch_values_old[pitch_values_old <= average_old+(deviation_old*2.5)])

    scaling_factor = pitch_aver_old - pitch_aver_new
    print(scaling_factor)

    pitch_values_new = pitch_values_new + scaling_factor

    return pitch_values_new, scaling_factor



def draw_pitch(new_pitch, old_pitch, path):
    """This function plots pitch from a praat sound object
    inputs
    _________________
    The new_pitch will be recorded when the script is run
    The old_pitch is the target audio that the student is given
    """

    # Clear figure to avoid cached plots
    #plt.clf()

    # Process audio
    pitch_values_new, pitch_values_old, time_new, time_old = preprocess_audio(
        new_pitch, old_pitch
    )


    # Make sure graphs don't clash
    pitch_values_new, scaling_factor = pitch_difference(pitch_values_old, pitch_values_new)


    # # replace unvoiced samples by NaN to not plot
    pitch_values_old[pitch_values_old == 0] = np.nan
    # Because we added the scaling factor the empty samples no longer equal 0
    pitch_values_new[pitch_values_new == scaling_factor] = np.nan
    plt.clf()

    # First Plot the old pitch

    # Make sure units are not included
    plt.xticks(time_old, '')
    plt.yticks(pitch_values_old, '')

    # Add some starting room from text_plot for both plots
    start_room = 0.5
    time_old += start_room
    time_new += start_room

    # create a plot object for old_pitch with label "Target"
    plt.plot(time_old, pitch_values_old, 'o', markersize=5, color='w')
    old_pitch_plot = plt.plot(time_old, pitch_values_old, 'o', label='Target', markersize=2, color='b')


    # Plot the new pitch over the old
    # Make sure units are not included
    plt.xticks(time_new, '')
    plt.yticks(pitch_values_new, '')
    # create a plot object for new_pitch with label "You"
    plt.plot(time_new, pitch_values_new, 'o', markersize=5, color='w')
    new_pitch_plot = plt.plot(time_new, pitch_values_new, 'o', label='You', markersize=2, color='y')

    # Create legends
    first_legend = plt.legend(handles=new_pitch_plot)

    plt.gca().add_artist(first_legend)

    # Second legend on the lower right corner
    #plt.legend(handles=old_pitch_plot, loc='lower right')
    plt.grid(False)
    # Set the plot's bounds
    plt.ylim(0,  max(pitch_values_old) + 200)
    plt.ylabel('Pitch')
    plt.xlabel('Time')
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
