from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

from flaskr.db import get_db

import tempfile

import parselmouth as praat

from pitch_track.pitch_plot import draw_pitch

import os


bp = Blueprint('/record', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, created, chapter_title, audio_path' #TODO: match this function to audio
        ' FROM chapters p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/record/<string:filename>', methods=['GET'])
@login_required
def record(filename):
    """Yields the template without a plot."""
    return render_template('/record/index.html', recording=filename)

@bp.route('/record/plotted/<string:filename>/<string:path>', methods=['POST']) # TODO: undo hardcoding
@login_required
def record_redirect(filename, path):
    """Yields the template with latest plot and posts recording info into db."""
    chapter_id = request.form['title'] # TODO: find a way to encode into database
    author_id = request.form['body']
    recording_path = 'id' # TODO:link to id creation
    plot_path =
    error = None
    if not title:
        error = 'Title is required.'
    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO recordings (chapter_id, author_id, recording_path, plot_path)'
            ' VALUES (?, ?, ?, ?)',
            (recording_id, body, g.user['id']) #TODO: do right variables
        )
        db.commit()
    return render_template('/record/index.html', recording=filename, plot=path)


# @bp.route('/recorded/<string:filename>')
# def recorded(filename):
#     return render_template()


#bp = Blueprint('pitch_track', __name__, url_prefix='/pitch_track')


@bp.route('/record/send/<string:filename>/<string:path>', methods=['POST'])
def show_plot(filename, path='plot.png'):
    """Uses temporary file to write wav file and process in praat into
    pitch plot."""

    # Save the file that was sent, and read it into a parselmouth.Sound
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(request.data)
        with open('tmp/audio.wav', 'wb') as out_file:
            out_file.write(request.data)
        sound = praat.Sound(tmp.name)

    # Calculate the pitch track with Parselmouth
    new_pitch = sound.to_pitch()
    old_pitch = praat.Sound('Recordings/Sentence1_dec.wav').to_pitch()

    path = draw_pitch(new_pitch, old_pitch, path)

    return redirect(url_for('/record.record_redirect', filename=filename, path=path))


@bp.route('/record/tmp/<string:filename>')
def return_temp_file(plotname):
    """Get the plot file from tmp directory."""

    return send_from_directory('../tmp', plotname, as_attachment=True)


@bp.route('/record/tmp')
def test_png():
    return return_temp_file('plot.png')