from flask import Blueprint

bp = Blueprint('admin', __name__)

from advencal.admin import admin  # noqa: F401,E402
