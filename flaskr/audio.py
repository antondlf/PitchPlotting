from flask import send_from_directory
from flask import Blueprint

bp = Blueprint('/audio', __name__)

@bp.route('/Recordings/<path:filename>')
def download_file(filename):
    return send_from_directory('../Recordings', filename, as_attachment=True)

@bp.route('/Recordings/test')
def test_audio():
    return download_file('Sentence1_dec.wav')


@bp.route('/test')
def test():
    return 'Hello, World!'