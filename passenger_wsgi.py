import sys
import os

sys.path.append(os.getcwd())
os.environ['FLASK_APP'] = "advencal"
os.environ['SECRET_KEY'] = os.environ['ADVENCAL_SECRET_KEY']

from startup import app as application  # noqa: F401,E402
