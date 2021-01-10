from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flaskr.auth import login_required

import tempfile

bp = Blueprint('/record', __name__)


@bp.route('/record')
@login_required
def record():
    return render_template('/record/index.html')


bp = Blueprint('pitch_track', __name__, url_prefix='/pitch_track')


@bp.route('/pitch_track', methods=['POST'])
def pitch_track():
    import parselmouth as praat

    # Save the file that was sent, and read it into a parselmouth.Sound
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(request.files['audio'].read())
        sound = praat.Sound(tmp.name)

    # Calculate the pitch track with Parselmouth
    pitch_track = sound.to_pitch().selected_array['frequency']

    # Convert the NumPy array into a list, then encode as JSON to send back
    return jsonify(list(pitch_track))

