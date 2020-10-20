"""
Module that initiliazes the flask application
"""
import logging
from flask import Flask

# Create Flask application
app = Flask(__name__)
app.config.from_object("config")

from service import service, models

# Set up logging for production
print("Setting up logging for {}...".format(__name__))
app.logger.propagate = False
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    app.logger.info("Logging established")

app.logger.info(70 * "*")
app.logger.info("  O R D E R   S E R V I C E  ".center(70, "*"))
app.logger.info(70 * "*")

# make our sqlalchemy tables
service.init_db()

app.logger.info("Service inititalized!")
