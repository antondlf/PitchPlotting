from flask import send_from_directory
from flask import Blueprint

bp = Blueprint('audio', __name__)

@bp.route('/Recordings/<path:filename>')
def download_file(filename):
    return send_from_directory('./Recordings', filename)