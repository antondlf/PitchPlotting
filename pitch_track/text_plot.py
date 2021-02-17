import parselmouth
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from praatio import tgio




sns.set() # Use seaborn's default style to make attractive graphs


def midpoint(x, y):
    point = x + ((y-x)/2)
    return point


def draw_text_plot(audio, textgrid, plot_path,  jitter = 0.001, text_jitter = 10):

    plt.clf()

    pitch = parselmouth.Sound(audio).to_pitch()

    # Extract selected pitch contour, and
    pitch_values = pitch.selected_array['frequency']
    np.trim_zeros(pitch_values)

    # Format textgrid
    tg = tgio.openTextgrid(textgrid)
    # Make sure there is only one tier
    if len(list(tg.tierDict.keys())) > 1:
        print('Error: more than one tier in textgrid')
        return
    else:
        # Get tier name
        tier_key = list(tg.tierDict.keys())[0]


    entryList = tg.tierDict[tier_key].entryList  # Get all intervals

    # Get time values rounded to correspond to correspond to textgrid values
    time = pitch.xs()
    time = (np.around(time, decimals=2))

    # Color list for plotting
    # color_list = ['b', 'r', 'g', 'm', 'c', 'k', 'y']

    # Summary statistics to remove outliers and noise
    deviation = np.std(pitch_values)
    average = np.mean(pitch_values)

    pitch_min = min(pitch_values[pitch_values > 0])

    # Remove 0 values and values further than two standard deviations from the mean
    pitch_values[pitch_values == 0] = np.nan
    pitch_values[pitch_values >= average+(deviation*2.5)] = np.nan
    pitch_values[pitch_values <= average-(deviation*2.5)] = np.nan

    # # Make sure there are enough colors for each word
    # while len(color_list) < len(entryList):
    #     color_list = color_list *2
    #
    # # Get jitter values for text
    # text_jitter = np.resize([20, 0], len(entryList))
    #
    # Place the text right above the maximum value that sits within 2.5 standard
    # Deviations of the mean.
    text_placement = max(pitch_values[pitch_values <= average+(deviation*2.5)]) + 10

    for interval in entryList:
    #     #plt.axvline(interval[0], linestyle='dotted')
    #     # Get start and end time for each boundary
    #     start, end = (np.where(time == round(interval[0], 2))[0], np.where(time == round(interval[1], 2))[0])
    #     # Place text at the start of each interval
        plt.text(
            round(interval[0], 2), #+ jitter,
            text_placement,
            interval[2],
            fontsize=8,
            c='k'
        )
    #     # Get the indices, round so that they match arrays
    #     time[start[0]:end[0]] += jitter
    #     plt.plot(time[start[0]:end[0]], pitch_values[start[0]:end[0]], 'o', markersize=5, color='w')
    #     plt.plot(time[start[0]:end[0]], pitch_values[start[0]:end[0]], 'o', markersize=2, color=style)
    #     jitter += jitter

    plt.plot(time, pitch_values, 'o', markersize=5, color='w')
    plt.plot(time, pitch_values, 'o', markersize=2, color='b')

    plt.xlim(min(time), max(time))
    plt.grid(False)
    plt.ylim(pitch_min - 30, text_placement + 30)
    plt.ylabel("fundamental frequency [Hz]")
    plt.tick_params(axis='x', which='both')
    plt.savefig(plot_path)
    # Optionally pre-emphasize the sound before calculating the spectrogram snd.pre_emphasize()