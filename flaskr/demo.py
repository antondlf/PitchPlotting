from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)

from pitch_track.pitch_plot import draw_pitch

import parselmouth as praat

import tempfile

import os


# This is an unfinished demo app, please ignore

bp = Blueprint('/demo', __name__)


@bp.route('/demo')
def demo_index():
    return render_template('/demo/demo_index.html')


@bp.route('/demo/upload')
def demo_upload():
    return render_template('demo/own_recording.html')

#
# @bp.route('/demo/upload_demo', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         f = request.files['file']
#
#         if f:
#
#             return render_template(
#                 'demo/script_host.html', recording=f)
#         else:
#             flash('Error: file not uploaded correctly')


@bp.route('/demo/upload_demo/plot', methods=['GET', 'POST'])
def plot_pitches(file):

    with tempfile.NamedTemporaryFile() as temp:

        new_pitch = praat.Sound(request.data).to_pitch()
        old_pitch = praat.Sound(file).to_pitch()

        draw_pitch(new_pitch, old_pitch, temp)

@bp.route('/demo/italian_example')
def get_demo_sent():

    return render_template(
            '/record/index.html', recording='Damiano_morde(Q)', sentence='Damiano morde la mela?',
        sent_type='QUESTION: ', textplot='2-Q-Damiano_morde.png', audio='2-Q-Damiano_morde.wav'
        )



