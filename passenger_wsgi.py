import sys, os
sys.path.append(os.getcwd())
os.environ['FLASK_APP']="advencal"
os.environ['SECRET_KEY']="this_is_ridiculous"
from startup import app as application