from flask import Blueprint

bp = Blueprint('basic', __name__)

from advencal.basic import basic  # noqa: F401,E402
