import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import parselmouth
from parselmouth.praat import call
import seaborn as sns
import sys

sns.set()


def get_summary(pitch):

    average = np.mean(pitch)
    deviation = np.std(pitch)

    return average, deviation


def remove_outliers(pitch):
    """Removes outlier noise."""

    data = pitch.selected_array['frequency']
    avg, std = (get_summary(data))

    # make samples outside 2.5 deviations of
    # mean equal 0
    data[data >= avg+(std*2.5)] = 0

    return data


def low_pass(sound_object, low_freq, high_freq, smoothing):
    """Filters sound object using praat's command
    Filter (pass Hann band)"""

    filtered = call(sound_object, "Filter (pass Hann band)", low_freq, high_freq, smoothing)
    print('filtered:', type(filtered), filtered)

    return filtered


def validated_smooth(sound_object):
    """Smooths f0 while filtering out doubled samples."""

    # Turn into a pitch object
    pitch_object = sound_object.to_pitch()

    # Remove octave jumps
    kill_octaves = pitch_object.kill_octave_jumps()

    # Smooth
    smoothed = kill_octaves.smooth()

    return smoothed


def trim_silences(sound: parselmouth.Sound) -> parselmouth.Sound:
    """Uses praat command Trim silences to remove noise and long
    silent sections."""

    trimmed_sound = call(sound, 'Trim silences', 0.05, 0, 100, 0, -25, 0.1, 0.1, 0, "silence")
    # Parselmouth call is not well documented, and trimmed_sound sometimes
    # returns a list of length 1, this causes problems for the rest of the script
    if type(trimmed_sound) == list:
        trimmed_sound = trimmed_sound[0]

    return trimmed_sound


def trim_recording(pitch: parselmouth.Pitch) -> tuple:
    """Trims the front and back zeros from the pitch
    array and the corresponding time values."""

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


def adjust_time_samples(new_time, old_time):
    """Get a resample of the new time array to match the old time array."""

    new_time_normalized = new_time/(new_time.max()/old_time.max())

    return new_time_normalized


def preprocess_pipeline(sound, low=0, high=500, smoothing=50):
    """Preprocesses praat sound objects for plotting.
    Filters, trims silences, smooths samples."""

    # Filter out high frequencies to reduce chances of interfering noise
    filtered = low_pass(sound, low, high, smoothing)

    # Trim short transient noise samples and long silences
    trimmed = trim_silences(filtered)

    # Create pitch objects and smooth
    smooth = validated_smooth(trimmed)
        #trimmed.to_pitch().smooth()

    # Remove trailing and leading silences
    pitch, time = trim_recording(smooth)

    return pitch, time


def preprocess_audio(new_sound, old_sound, low=0, high=500, smoothing=50):
    """Processes sound objects for plotting"""

    # Individual audio preprocessing
    pitch_old, time_old = preprocess_pipeline(old_sound, low=low, high=high, smoothing=smoothing)
    pitch_new, time_new = preprocess_pipeline(new_sound, low=low, high=high, smoothing=smoothing)

    # Simple time warping
    new_time_normalized = adjust_time_samples(time_new, time_old)

    return pitch_new, pitch_old, new_time_normalized, time_old


def pitch_difference(pitch_values_old, pitch_values_new):
    """Generate a number to add to pitch_values_old so that
    graphs don't clash."""

    # average_new, deviation_new = get_summary(pitch_values_new)
    # average_old, deviation_old = get_summary(pitch_values_old)
    pitch_aver_new = np.mean(pitch_values_new)
    pitch_aver_old = np.mean(pitch_values_old)

    scaling_factor = pitch_aver_old - pitch_aver_new
    print(scaling_factor)

    pitch_values_new = pitch_values_new + scaling_factor

    return pitch_values_new, scaling_factor



def draw_pitch(new_pitch, old_pitch, path, show=False):
    """This function plots pitch from a praat sound object
    inputs
    _________________
    The new_pitch will be recorded when the script is run
    The old_pitch is the target audio that the student is given
    """

    # Clear figure to avoid cached plots
    # plt.clf()

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
    plt.plot(time_old, pitch_values_old, 'o', markersize=7, color='w')
    old_pitch_plot = plt.plot(time_old, pitch_values_old, 'o', label='Native', markersize=3, color='b')

    # Plot the new pitch over the old
    # Make sure units are not included
    plt.xticks(time_new, '')
    plt.yticks(pitch_values_new, '')
    # create a plot object for new_pitch with label "You"
    plt.plot(time_new, pitch_values_new, 'o', markersize=5, color='w')
    new_pitch_plot = plt.plot(time_new, pitch_values_new, 'o', label='You', markersize=2, color='y')

    # Create legends
    first_legend = plt.legend(handles=new_pitch_plot, markerscale=3.0)
    second_legend = plt.legend(handles=old_pitch_plot, loc='lower right', markerscale=2.0)

    plt.gca().add_artist(first_legend)
    plt.gca().add_artist(second_legend)

    # Second legend on the lower right corner
    #plt.legend(handles=old_pitch_plot, loc='lower right')
    plt.grid(False)
    # Set the plot's bounds
    plt.ylim(0,  np.nanmax(pitch_values_old) + 200)
    plt.ylabel('Pitch')
    plt.xlabel('Time')
    plt.savefig(path)
    if show:
        plt.show()

    return path


def main():
    # testing code
    native = input('Path to native:')
    learner = input('Path to learner:')
    path = input('Path to plot:')
    old = parselmouth.Sound(native)
    new = parselmouth.Sound(learner)
    draw_pitch(new, old, path, show=True)

if __name__=='__main__':
    main()