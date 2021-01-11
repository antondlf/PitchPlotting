from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

import tempfile

import parselmouth as praat

from pitch_track.pitch_plot import draw_pitch


bp = Blueprint('/record', __name__)


@bp.route('/record/<string:filename>')
@login_required
def record(filename):
    return render_template('/record/index.html', recording=filename)

@bp.route('/record/plotted/<string:filename>/<string:path>') # TODO: undo hardcoding
def record_redirect(filename, path):
    return render_template('/record/index.html', recording=filename, plot=path)


@bp.route('/recorded/<string:filename>')
def recorded(filename):
    return render_template()


#bp = Blueprint('pitch_track', __name__, url_prefix='/pitch_track')


@bp.route('/record/send/<string:filename>/<string:path>', methods=['POST'])
def show_plot(filename, path):

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

    return redirect(url_for('/record.record_redirect', filename='Sentence1_dec.wav', path=path))


@bp.route('/tmp/<string:filename>')
def return_temp_file(filename):
    return send_from_directory('./tmp', filename, as_attachment=True)


@bp.route('/tmp')
def test_png():
    return return_temp_file('plot.png')