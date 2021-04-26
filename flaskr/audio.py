from flask import send_from_directory
from flask import Blueprint
from flaskr.db import get_db
from flask import current_app
from werkzeug.exceptions import abort
import os

bp = Blueprint('/audio', __name__)

@bp.route('/Recordings/<string:chaptername>', methods=['GET'])
def download_file(chaptername):
    audio = get_db().execute(
        'SELECT audio_path FROM chapters WHERE chapter_title=?',
        (chaptername,)
    ).fetchall() # maybe fetchone()

    if not len(audio) == 1:
        abort(404, "Audio '{0}' doesn't exist or database entry is corrupt.".format(audio))

    directory, file = audio[0][0].rsplit('/', 1)

    return send_from_directory(directory, file, as_attachment=True)

@bp.route('/bell_sound')
def get_bell():
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'bell_sound.wav', as_attachment=True)

@bp.route('/Recordings/test')
def test_audio():
    return download_file('Sentence1_dec.wav')


@bp.route('/test')
def test():
    return 'Hello, World!'