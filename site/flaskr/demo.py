from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)

from pitch_track.pitch_plot import draw_pitch

import parselmouth as praat

import tempfile

import os


bp = Blueprint('/demo', __name__)

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/demo/menu')
def demo_index():
    return render_template('/demo/demo_index.html')


@app.route('/demo/upload')
def upload_file():
    return render_template('demo/own_recording.html')


@app.route('/demo/upload_demo', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']

        if f:

            return render_template(
                'demo/script_host.html', recording=f)
        else:
            flash('Error: file not uploaded correctly')


@app.route('/demo/upload_demo/plot', methods=['GET', 'POST'])
def plot_pitches(file):

    with tempfile.NamedTemporaryFile() as temp:

        new_pitch = praat.Sound(request.data).to_pitch()
        old_pitch = praat.Sound(file).to_pitch()

        draw_pitch(new_pitch, old_pitch, temp)

        return render_template(
            'demo/script_host.html', recording=f, plot=temp
        )



