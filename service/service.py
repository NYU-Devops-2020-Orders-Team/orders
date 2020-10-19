from flask import jsonify, request, url_for, make_response, abort
from flask_api import status
from werkzeug.exceptions import NotFound

from .models import Order, DataValidationError
from . import app


######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=message
        ),
        status.HTTP_400_BAD_REQUEST,
    )


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    app.logger.warning(str(error))
    return (
        jsonify(
            status=status.HTTP_404_NOT_FOUND, error="Not Found", message=str(error)
        ),
        status.HTTP_404_NOT_FOUND,
    )


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=message,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=message,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


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
# ADD A NEW ORDER
######################################################################
@app.route('/orders', methods=['POST'])
def create_orders():
    """
    Creates an order
    This endpoint will create an order based the data in the body that is posted
    """
    app.logger.info("Request to create an order")
    check_content_type("application/json")
    order = Order()
    order.deserialize(request.get_json())
    order.create()
    message = order.serialize()
    location_url = url_for('get_orders', order_id=order.id, _external=True)
    app.logger.info('Created Order with id: {}'.format(order.id))
    return make_response(jsonify(message), status.HTTP_201_CREATED, {"Location": location_url})


######################################################################
# LIST ALL ORDERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """ Returns all of the Orders """
    app.logger.info("Request for order list")

    customer_id = request.args.get("customer_id")
    if customer_id:
        orders = Order.find_by_customer_id(customer_id)
    else:
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


######################################################################
# CANCEL AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/cancel", methods=["PUT"])
def cancel_orders(order_id):
    """ Cancel all the items of the Order that have not being shipped yet """
    app.logger.info("Request to cancel order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))

    shipped_or_delivered_orders = 0
    for i in range(len(order.order_items)):
        if order.order_items[i].status in ["DELIVERED", "SHIPPED"]:
            shipped_or_delivered_orders += 1
        elif order.order_items[i].status != "CANCELLED":
            order.order_items[i].status = "CANCELLED"
    if shipped_or_delivered_orders == len(order.order_items):
        raise DataValidationError("All the items have been shipped. Nothing to cancel")
    order.update()
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# CANCEL AN ITEM IN AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>/cancel", methods=["PUT"])
def cancel_item(order_id, item_id):
    """ Cancel a single item in the Order that have not being shipped yet """
    app.logger.info("Request to cancel item with id: %s in order with id: %s", item_id, order_id)
    order = Order.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))

    order_item_found = False
    for i in range(len(order.order_items)):
        if order.order_items[i].item_id == item_id:
            order_item_found = True
            if order.order_items[i].status in ["DELIVERED", "SHIPPED"]:
                raise DataValidationError("Item has already been shipped/delivered. Nothing to cancel")
            elif order.order_items[i].status != "CANCELLED":
                order.order_items[i].status = "CANCELLED"
            break

    if not order_item_found:
        raise NotFound("Item with id '{}' was not found inside order.".format(item_id))
    order.update()
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


if __name__ == '__main__':
    app.run()


def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Order.init_db(app)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))
