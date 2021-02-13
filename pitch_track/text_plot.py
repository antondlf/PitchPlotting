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

    pitch = parselmouth.Sound(audio).to_pitch()
    # Extract selected pitch contour, and
    # replace unvoiced samples by NaN to not plot
    pitch_values = pitch.selected_array['frequency']
    np.trim_zeros(pitch_values)
    # Format textgrid
    tg = tgio.openTextgrid(textgrid)
    entryList = tg.tierDict["Sentence"].entryList  # Get all intervals
    time = pitch.xs()
    time = (np.around(time, decimals=2))
    invert_value = -1
    color_list = ['b', 'r', 'g', 'm', 'c', 'k', 'y']
    pitch_values[pitch_values == 0] = np.nan
    #pitch_values[pitch_values >= 300] = np.nan
    while len(color_list) < len(entryList):
        color_list = color_list *2
    for interval, style in zip(entryList, color_list):
        #plt.axvline(interval[0], linestyle='dotted')
        # Get start and end time for each boundary
        start, end = (np.where(time == round(interval[0], 2))[0], np.where(time == round(interval[1], 2))[0])
        # Place text at the start of each interval
        plt.text(
            round(interval[0], 2) + jitter,
            max(pitch_values[start[0]:end[0]]) + text_jitter,
            interval[2],
            fontsize=10,
            c = style
        )
        # Get the indices, round so that they match arrays
        time[start[0]:end[0]] += jitter
        plt.plot(time[start[0]:end[0]], pitch_values[start[0]:end[0]], 'o', markersize=5, color='w')
        plt.plot(time[start[0]:end[0]], pitch_values[start[0]:end[0]], 'o', markersize=2, color=style)
        jitter += jitter
        print(jitter)
    plt.xlim(min(time), max(time))
    plt.grid(False)
    plt.ylim(0, pitch.ceiling)
    plt.ylabel("fundamental frequency [Hz]")
    plt.tick_params(axis='x', which='both')
    plt.show()
    plt.savefig(plot_path)
    # Optionally pre-emphasize the sound before calculating the spectrogram snd.pre_emphasize()

# snd = parselmouth.Sound('/Users/anton/desktop/Mama_recording.wav')
# pitch = snd.to_pitch()
# textgrid =  tgio.openTextgrid(
#         "/Users/anton/desktop/mama_recording.TextGrid")

# spectrogram = snd.to_spectrogram(maximum_frequency=8000.0)
# plt.figure()
# #draw_spectrogram(spectrogram)
# #plt.twinx()
#draw_text_plot(pitch(pitch, textgrid)#, jitter=0.5)
# plt.xlim([snd.xmin, snd.xmax])
#
# tg = tgio.openTextgrid("/Users/anton/PycharmProjects/FlaskTutorial/Recordings/Chapter_1/Sentence1_dec.TextGrid")
# entryList = tg.tierDict["Sentence"].entryList # Get all intervals
#

