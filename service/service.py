from flask import Flask
from flask_api import status  # HTTP Status Codes

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return "Hello from Flask"

if __name__ == '__main__':
    app.run()
