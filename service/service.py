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

######################################################################
# LIST ALL ORDERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """ Returns all of the Orders """
    app.logger.info("Request for order list")
    orders = []
    orders = Order.all()
    results = [order.serialize() for order in orders]
    app.logger.info("Returning %d orders", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_orders(order_id):
    """
    Retrieve a single Order

    This endpoint will return a Order based on it's id
    """
    app.logger.info("Request for order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)

if __name__ == '__main__':
    app.run()


def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Order.init_db(app)
