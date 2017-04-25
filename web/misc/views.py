from flask import render_template

from ..misc import misc_bp as bp


@bp.route('/')
def index():
    return render_template('index.html')
