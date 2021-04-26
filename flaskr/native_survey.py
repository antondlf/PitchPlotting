from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, request, url_for, send_from_directory
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


bp = Blueprint('/judgments', __name__)

@bp.route('/judgments/<string:question_num>')
@login_required
def get_questions(question_num):

    user_id = g.user['id']

    db = get_db()
    sentence = db.execute(
        'SELECT speaker, chapter, is_baseline, native, text'
        ' FROM judgment_questions WHERE question_num=?'  # p JOIN user u ON p.author_id = u.id'
        ' ORDER BY question_num DESC',
        (question_num,)
    ).fetchall()

    speaker, chapter, is_baseline, native, text = sentence[]

    return sentence


# TODO: Create function to select given question
    speaker, chapter, is_baseline, native, text = sentence[]