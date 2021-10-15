import matplotlib.pyplot as plt
import seaborn as sns
from praatio import tgio
import parselmouth
import numpy as np
import os
from pitch_plot import preprocess_pipeline




sns.set() # Use seaborn's default style to make attractive graphs


def midpoint(x, y):
    point = x + ((y-x)/2)
    return point


def draw_text_plot(audio, textgrid, plot_path):#,  jitter = 0.001, text_jitter = 10):

    plt.clf()

    sound = parselmouth.Sound(audio)


    # Extract selected pitch contour, and trim the beginning zeroes
    pitch_values, time = preprocess_pipeline(sound)

    pitch_values[pitch_values == 0] = np.nan

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
    time = (np.around(time, decimals=2))

    # Color list for plotting
    # color_list = ['b', 'r', 'g', 'm', 'c', 'k', 'y']

    # Summary statistics to remove outliers and noise
    deviation = np.std(pitch_values)
    average = np.mean(pitch_values)
    maximum = max(pitch_values)

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
    #trace_max = max(pitch_values[pitch_values <= average+(deviation*2.5)])

    trim = entryList[0][0]

    start_room = 0.5

    for interval in entryList:

        # Place text at the start of each interval
        plt.text(
            round(interval[0]-trim, 2) + start_room, #+ jitter,
            pitch_min - 20,
            interval[2],
            fontsize=8,
            c='k'
        )
    #     # Get the indices, round so that they match arrays
    #     time[start[0]:end[0]] += jitter
    #     plt.plot(time[start[0]:end[0]], pitch_values[start[0]:end[0]], 'o', markersize=5, color='w')
    #     plt.plot(time[start[0]:end[0]], pitch_values[start[0]:end[0]], 'o', markersize=2, color=style)
    #     jitter += jitter

    # plt.xlim(min(time), max(time))

    time += start_room

    plt.plot(time, pitch_values, 'o', markersize=5, color='w')
    plt.plot(time, pitch_values, 'o', markersize=2, color='b')

    plt.xticks(time, '')
    plt.yticks(pitch_values, '')

    plt.grid(False)
    plt.ylim(0, maximum+200)
    plt.ylabel('Pitch')
    plt.xlabel('Time')
    plt.tick_params(axis='x', which='both')
    plt.savefig(plot_path)
    # Optionally pre-emphasize the sound before calculating the spectrogram snd.pre_emphasize()


def preprocess_chapters(chapters_path):
    """From path to Recordings add a pitch plot to every dir that starts with "Chapter_"."""

    for dir in os.listdir(chapters_path):

        chap_directory = os.path.join(chapters_path, dir)
        print(chap_directory)
        if chap_directory != '../../Recordings/.DS_Store':
            pass

            for file in os.listdir(chap_directory):

                if file.endswith('.TextGrid'):
                    grid = os.path.join(chap_directory, file)

                if file.endswith('.wav'):
                    audio = os.path.join(chap_directory, file)
                    pathname = os.path.join(chap_directory, file.rsplit('.')[0] + '.png')
                    print(pathname)

            draw_text_plot(audio, grid, pathname)

if __name__ == '__main__':
    preprocess_chapters('../Recordings')