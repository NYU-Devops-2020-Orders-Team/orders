""" Module to define the Rest APIs """
from flask import jsonify, request, url_for, make_response, abort
from flask_api import status
from werkzeug.exceptions import NotFound

from .models import Order, OrderItem, DataValidationError
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
# UPDATE AN EXISTING ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update an Order's customer_id
    Since customer_id is the only field in the Order table that can be updated
    This endpoint will update an Order based the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")
    new_customer_id = get_customer_id_from_request(request.get_json())
    order = Order.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))
    order.customer_id = new_customer_id
    order.update()

    app.logger.info("Order with ID [%s] updated.", order_id)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING ORDER ITEM
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_order_items(order_id, item_id):
    """
    Update an Order Item
    This endpoint will update an Order item based the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")
    order = Order.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))
    order_item_found = False

    new_order_item = OrderItem()
    new_order_item.deserialize(request.get_json())
    for i in range(len(order.order_items)):
        if order.order_items[i].item_id == item_id:
            order_item_found = True
            order.order_items[i].product_id = new_order_item.product_id
            order.order_items[i].quantity = new_order_item.quantity
            order.order_items[i].price = new_order_item.price
            order.order_items[i].status = new_order_item.status
            break

    if not order_item_found:
        raise NotFound("Item with id '{}' was not found inside order.".format(item_id))
    order.update()
    app.logger.info("Order with ID [%s] updated.", order_id)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


def get_customer_id_from_request(json):
    """ Helper function to get customer_id from the request """
    try:
        new_customer_id = json["customer_id"]
        if new_customer_id is None or not isinstance(new_customer_id, int):
            raise DataValidationError("Invalid Customer Id provided for update")
        return new_customer_id
    except KeyError as error:
        raise DataValidationError("Invalid order: missing " + error.args[0])


######################################################################
# DELETE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    """
    Delete an Order
    This endpoint will delete an Order based the id specified in the path
    """
    app.logger.info("Request to delete order with id: %s", order_id)
    order = Order.find(order_id)
    if order:
        order.delete()

    app.logger.info("Order with ID [%s] delete complete.", order_id)
    return make_response("", status.HTTP_204_NO_CONTENT)


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
    for order_item in order.order_items:
        if order_item.status in ["DELIVERED", "SHIPPED"]:
            shipped_or_delivered_orders += 1
        elif order_item.status != "CANCELLED":
            order_item.status = "CANCELLED"
    if shipped_or_delivered_orders == len(order.order_items):
        raise DataValidationError("All the items have been shipped/delivered. Nothing to cancel")
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

    order_item = find_order_item(order.order_items, item_id)
    if not order_item:
        raise NotFound("Item with id '{}' was not found inside order.".format(item_id))
    if order_item.status in ["DELIVERED", "SHIPPED"]:
        raise DataValidationError("Item has already been shipped/delivered")
    if order_item.status != "CANCELLED":
        order_item.status = "CANCELLED"
        order.update()

    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# SHIP AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/ship", methods=["PUT"])
def ship_orders(order_id):
    """ Ship all the items of the Order that have not being shipped yet """
    app.logger.info("Request to ship order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))

    shipped_delivered_canceled_orders = 0
    for i in range(len(order.order_items)):
        if order.order_items[i].status in ["DELIVERED", "CANCELLED"]:
            shipped_delivered_canceled_orders += 1
        elif order.order_items[i].status != "SHIPPED":
            order.order_items[i].status = "SHIPPED"
    if shipped_delivered_canceled_orders == len(order.order_items):
        raise DataValidationError("All the items in this order are DELIVERED/SHIPPED/CANCELED, no items can be shipped.")
    order.update()
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# SHIP AN ITEM IN AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>/ship", methods=["PUT"])
def ship_item(order_id, item_id):
    """ Ship a single item in the Order that have not being cancelled or delivered yet """
    app.logger.info("Request to ship item with id: %s in order with id: %s", item_id, order_id)
    order = Order.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))

    order_item = find_order_item(order.order_items, item_id)
    if not order_item:
        raise NotFound("Item with id '{}' was not found inside order.".format(item_id))
    if order_item.status in ["CANCELLED", "DELIVERED"]:
        raise DataValidationError("Item has already been cancelled/delivered")
    if order_item.status != "SHIPPED":
        order_item.status = "SHIPPED"
        order.update()

    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# DELIVER AN ITEM IN AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>/deliver", methods=["PUT"])
def deliver_item(order_id, item_id):
    """ 
    Change status of a single item in the Order to "DELIVERED".
    The item has not been cancelled and has been shipped 
    """
    app.logger.info("Request to deliver item with id: %s in order with id: %s", item_id, order_id)
    order = Order.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))

    order_item = find_order_item(order.order_items, item_id)
    if not order_item:
        raise NotFound("Item with id '{}' was not found inside order.".format(item_id))
    if order_item.status == "PLACED":
        raise DataValidationError("Item has not been shipped yet.")
    if order_item.status == "CANCELLED":
        raise DataValidationError("Item has already been cancelled.")
    if order_item.status == "DELIVERED":
        raise DataValidationError("Item has already been delivered.")
    if order_item.status == "SHIPPED":
        order_item.status = "DELIVERED"
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


def find_order_item(order_items, item_id):
    """ Find order item with the item_id """
    for order_item in order_items:
        if order_item.item_id == item_id:
            return order_item
    return None
