import matplotlib.pyplot as plt
import seaborn as sns
from praatio import tgio
import parselmouth
import numpy as np
import os
import pickle
from pitch_plot import preprocess_pipeline

sns.set() # Use seaborn's default style to make attractive graphs


def midpoint(x, y):
    point = x + ((y-x)/2)
    return point


def precompute_trace(sound, precompute_path, change_octave_cost=False):

    trace = preprocess_pipeline(sound)#, change_octave_cost=change_octave_cost)
    with open(precompute_path, 'wb') as in_file:
        pickled_trace = pickle.dumps(trace)
        in_file.write(pickled_trace)

    return trace


def draw_text_plot(audio, textgrid, plot_path, precompute_path, change_octave_cost=False):#,  jitter = 0.001, text_jitter = 10):

    plt.clf()

    sound = parselmouth.Sound(audio)


    # Extract selected pitch contour, and trim the beginning zeroes
    pitch_values, time = precompute_trace(sound, precompute_path, change_octave_cost=change_octave_cost)

    pitch_values[pitch_values == 0] = np.nan

    # Format textgrid
    tg = tgio.openTextgrid(textgrid)
    # Make sure there is only one tier
    if len(list(tg.tierDict.keys())) > 1:
        print('Error: more than one tier in textgrid')
        tier_key = list(tg.tierDict.keys())[0]
        print('Got tier:', tier_key)
        print()
    else:
        # Get tier name
        tier_key = list(tg.tierDict.keys())[0]

    entryList = tg.tierDict[tier_key].entryList  # Get all intervals

    # Get time values rounded to correspond to correspond to textgrid values
    time = (np.around(time, decimals=20))

    # Color list for plotting
    # color_list = ['b', 'r', 'g', 'm', 'c', 'k', 'y']

    # Summary statistics to remove outliers and noise
    deviation = np.std(pitch_values)
    average = np.mean(pitch_values)
    maximum = max(pitch_values)

    pitch_min = min(pitch_values[pitch_values > 0])

    # Remove 0 values and values further than two standard deviations from the mean
    pitch_values[pitch_values == 0] = np.nan

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

    plt.plot(time, pitch_values, markersize=5, color='w')
    plt.plot(time, pitch_values, markersize=2, color='b')

    plt.xticks(time, '')
    plt.yticks(pitch_values, '')

    plt.grid(False)
    plt.ylim(0, maximum+200)
    plt.ylabel('Pitch')
    plt.xlabel('Time')
    plt.tick_params(axis='x', which='both')
    plt.savefig(plot_path, bbox_inches='tight')
    #plt.show()


def preprocess_chapters(chapters_path, problem_list):
    """From path to Recordings_new add a pitch plot to every dir that starts with "Chapter_"."""

    for dir in os.listdir(chapters_path):

        if dir in problem_list:
            change_octave_cost = True
        else:
            change_octave_cost = False

        chap_directory = os.path.join(chapters_path, dir)
        print(chap_directory)
        if chap_directory != 'Recordings/.DS_Store':
            pass

            for file in os.listdir(chap_directory):

                if file.endswith('.TextGrid'):
                    grid = os.path.join(chap_directory, file)

                if file.endswith('.wav'):
                    audio = os.path.join(chap_directory, file)
                    pathname = os.path.join(chap_directory, file.rsplit('.')[0] + '.png')
                    trace_data_path = os.path.join(chap_directory, file.rsplit('.')[0] + '.pickle')
                    print(pathname)

            draw_text_plot(audio, grid, pathname, trace_data_path, change_octave_cost=change_octave_cost)


if __name__ == '__main__':

    #### This is the list of problem sentences due to octave halving at the start of the
    #### sentence. These file paths trigger a condition in preprocessing
    ### That changes the octave cost value of pitch extraction to 0.06. This is the
    ### Lowest value that fixes the issue for all of them
    problem_list = [
    'La_legna(S)',
    'La_via(S)',
    'Il_melone(S)']

    # ['Loredana_vende(S)',
    #     'Elena_guarda(Q)',
    #     'Luigi_odia(S)',
    # 'Il_leone(S)'
    # ,'La_balena(S)',
    #     'La_ragione(S)',
    #     'Debora_gira(S)']
    # (Livia_dorme(Q), 0.12)
    #
    # (Bernardo_viene(Q), 0.23)
    #
    # (Giovanni_ruba(Q), 0.27)
    #
    # (Il_nome(Q), 0.1)
    #
    # (La_balena(Q), 0.11)
    preprocess_chapters('Recordings', problem_list)

    #draw_text_plot('Recordings/La_via(S)/3-S-La_via.wav',
     #              'Recordings/La_via(S)/3-S-La_via.TextGrid',
      #             '',
       #            'Recordings/La_via(S)/3-S-La_via.pickle')