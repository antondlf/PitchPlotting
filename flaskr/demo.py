from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)

from pitch_track.pitch_plot import draw_pitch

from flaskr.audio_processing import save_audio, save_plot

import parselmouth as praat

import random

import tempfile

import os

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

@bp.route('/demo/italian_example', methods=['GET', 'POST'])
def italian_demo():
    if request.method == 'GET':
        return get_demo_sent()
    elif request.method == 'POST':
        # The audio data is contained in the request object
        audio_data = request.data

        demo_id = str(random.randint(0,50))

        # Use utility from audio_processing.py to process the audio
        trial_path = os.path.join(current_app.root_path, '../demo_recordings', 'demo_rec' + demo_id)

        recording_path = save_audio(trial_path, audio_data)
        print(recording_path)

        # If recording_path = None then wav file is empty.
        if recording_path == None:
            flash("No audio was recorded.", 'error')
            return get_demo_sent()

        nativeaudio = 'Damiano_morde(Q)'
        plot, useraudio = save_plot(nativeaudio, trial_path)

        # Redirect to the post_trial (comparison plot template)
        return redirect(url_for('/demo.get_demo_post_trial', demo_id=demo_id))


def get_demo_sent():

    return render_template(
        '/demo/italian_example.html', recording='Damiano_morde(Q)', sentence='Damiano morde la mela?',
        sent_type='QUESTION: ', textplot='2-Q-Damiano_morde.png', audio='2-Q-Damiano_morde.wav'
    )

@bp.route('/demo/italian_example/post_trial/<string:demo_id>')
def get_demo_post_trial(demo_id):


    nativefilename = '2-Q-Damiano_morde.wav'
    trial_path = 'demo_rec' + demo_id

    plot = trial_path + '.png'
    useraudio = trial_path + '.wav'

    # Redirect to the post_trial (comparison plot template)
    return render_template(
        '/demo/script_host.html', plot=plot, nativeaudio='Damiano_morde(Q)', useraudio=useraudio, demo_id=demo_id
    )


@bp.route('/demo/italian_example/get_demo_file/<string:filename>')
def return_demo_plot(filename):
    """Get the comparison plot"""
    dir = os.path.join(current_app.root_path, '../demo_recordings')
    return send_from_directory(dir, filename, as_attachment=True)


#Hardcode textplot for demo to avoid login requirement and protect data
@bp.route('/demo/italian_example/textplot')
def demo_textplot():
    """Get the orthographic plot"""

    path = os.path.join(current_app.root_path, '../Recordings', 'Damiano_morde(Q)')

    return send_from_directory(path, '2-Q-Damiano_morde.png', as_attachment=True)


@bp.route('/demo/reset_demo/<string:demo_id>')
def reset_demo(demo_id):
    """Delete current demo file"""

    trial_path = 'demo_rec' + demo_id

    dir = os.path.join(current_app.root_path, '../demo_recordings', trial_path)

    plot = dir + '.png'
    useraudio = dir + '.wav'

    if os.path.isfile(plot):
        os.remove(plot)
    if os.path.isfile(useraudio):
        os.remove(useraudio)

    return render_template('demo/demo_index.html')


