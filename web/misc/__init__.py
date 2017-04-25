from flask import Blueprint

misc_bp = Blueprint('misc', __name__)

from ..misc import views  # noqa
