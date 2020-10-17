from flask import Flask
from flask_api import status  # HTTP Status Codes

# Import Flask application
from . import __init__

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from .models import Order
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Orders REST API Service",
            version="1.0"
        ),
        status.HTTP_200_OK,
    )


if __name__ == '__main__':
    app.run()


def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Order.init_db(app)



@app.route('/orders', methods=['POST'])
def create_orders():
    app.logger.info('Create Order requested')
    order = Order()
    order.deserialize(request.get_json())
    order.create()
    app.logger.info('Created Order with id: {}'.format(order.id))
    return make_response(jsonify(order.serialize()),
                         status.HTTP_201_CREATED)
