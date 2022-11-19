from flask import Flask
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

from advencal import basic  # noqa: F401,E402
from advencal import admin  # noqa: F401,E402
