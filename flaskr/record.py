from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

from flaskr.db import get_db

from flaskr.audio import download_file

from werkzeug.exceptions import abort

import tempfile

import parselmouth as praat

from pitch_track.pitch_plot import draw_pitch

from flaskr.data_management import get_unique_id

import os


bp = Blueprint('/record', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    posts = db.execute(
        'SELECT created, chapter_title, audio_path' 
        ' FROM chapters'# p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/record/<string:chaptername>', methods=['POST', 'GET'])
@login_required
def record(chaptername):
    """Yields the template without a plot."""

    db = get_db()
    sentence = db.execute(
        'SELECT audio_path, text'
        ' FROM chapters WHERE chapter_title=?'  # p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC',
        (chaptername,)
    ).fetchall()
    if not len(sentence) == 1:
        abort(404, "Audio '{0}' doesn't exist or database entry is corrupt.".format(chaptername))
    audio_path, text = sentence[0]
    user_id = g.user['id']
    if request.method == 'GET':
        user_audio = db.execute(
            'SELECT recording_path, plot_path'
            ' FROM recordings WHERE chapter_id=? AND user_id=?'
            ' ORDER BY created DESC',
            (chaptername, user_id)
        ).fetchall()
        if len (user_audio) < 1:
            plot_path = None
        else:
            new_audio_path, plot_path = user_audio[0]
        #return render_template('/record/index.html', recording=chaptername, sentence=text, plot=plot_path)

    if request.method == 'POST':
        process_recording(audio_path, chaptername)
        return redirect(url_for('/record.record', chaptername=chaptername), code=302)

    return render_template('/record/index.html', recording=chaptername, sentence=text, plot=plot_path)



def process_recording(original_recording, chaptername):
    """Yields the template with latest plot and posts recording info into db."""
    # First get a unique id for this recording
    recording_id = get_unique_id()
    plot_id = '{}.png'.format(recording_id)

    # Chaptername passed to the function
    chapter_id = chaptername
    # Get author_id
    user_id = g.user['id']
    # Format a path for the recording
    recording_path = './participant_recordings/{}/{}.wav'.format(user_id, recording_id) # TODO:link to id creation
    # Format a path for the plot
    plot_path = save_plot(original_recording, './participant_recordings/{}'.format(plot_id))
    error = None
    if not chapter_id:
        error += 'Chapter_id is missing.'
    if not user_id:
        error += 'Author_id missing.'
    if not recording_path:
        error += 'Recording_path missing.'
    if not plot_path:
        error += 'Plot_path missing.'
    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO recordings (chapter_id, user_id, recording_path, plot_path)'
            ' VALUES (?, ?, ?, ?)',
            (chapter_id, user_id, recording_path, plot_id)
        )
        db.commit()
    return plot_id


# @bp.route('/recorded/<string:filename>')
# def recorded(filename):
#     return render_template()


#bp = Blueprint('pitch_track', __name__, url_prefix='/pitch_track')


#@bp.route('/record/send/<string:filename>/<string:path>', methods=['POST'])
def save_plot(filename, path):
    """Uses temporary file to write wav file and process in praat into
    pitch plot saved on a given path."""

    # Save the file that was sent, and read it into a parselmouth.Sound
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(request.data)
        with open('tmp/audio.wav', 'wb') as out_file:
            out_file.write(request.data)
        sound = praat.Sound(tmp.name)



    # Calculate the pitch track with Parselmouth
    new_pitch = sound.to_pitch()
    old_pitch = praat.Sound(filename).to_pitch()
    draw_pitch(new_pitch, old_pitch, path)

    return path


@bp.route('/record/participant_recordings/<string:filename>')
@login_required
def return_temp_file(filename):
    """Get the plot file from tmp directory."""
    return send_from_directory('./participant_recordings', filename, as_attachment=True)