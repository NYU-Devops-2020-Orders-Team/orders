""" Module to define the Rest APIs """
from functools import wraps
from flask import jsonify, request, url_for, make_response, abort
from flask_api import status
from flask_restx import Api, Resource, fields, reqparse, inputs
from werkzeug.exceptions import NotFound

from .models import Order, OrderItem, DataValidationError
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return app.send_static_file('index.html')


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Orders REST API Service',
          description='This is the back end for an eCommerce web site as a RESTful microservice for the resource order.',
          default='orders',
          default_label='Orders operations',
          doc='/apidocs'
          )

# Define the model so that the docs reflect what can be sent
create_item_model = api.model('Item', {
    'product_id': fields.Integer(required=True,
                                 description='Product id of the item'),
    'quantity': fields.Integer(required=True,
                               description='Quantity of the item'),
    'price': fields.Float(required=True,
                          description='Price of the item'),
    'status': fields.String(required=True,
                            description='Status of the item')
})

item_model = api.model('Item', {
    'item_id': fields.Integer(readOnly=True,
                              description='The unique item id assigned internally by service'),
    'product_id': fields.Integer(required=True,
                                 description='Product id of the item'),
    'quantity': fields.Integer(required=True,
                               description='Quantity of the item'),
    'price': fields.Float(required=True,
                          description='Price of the item'),
    'status': fields.String(required=True,
                            description='Status of the item')
})

create_model = api.model('Order', {
    'customer_id': fields.Integer(required=True,
                                  description='The customer id of the Order'),
    'order_items': fields.List(fields.Nested(create_item_model, required=True), required=True,
                               description='The items in the Order')
})

order_model = api.model('Order', {
    'id': fields.Integer(required=True, description='The id for each order'),
    'created_date': fields.DateTime(required=False, description='The date at which order was created'),
    'customer_id': fields.Integer(required=True,
                                  description='The customer id of the Order'),
    'order_items': fields.List(fields.Nested(item_model, required=True), required=True,
                               description='The items in the Order')
})

# query string arguments
order_args = reqparse.RequestParser()
order_args.add_argument('customer_id', type=int, required=True, help='List Orders by Customer id')


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
    location_url = api.url_for(OrderResource, order_id=order.id, _external=True)
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
#  PATH: /orders/{id}
######################################################################
@api.route('/orders/<int:order_id>', strict_slashes=False)
@api.param('order_id', 'The Order identifier')
class OrderResource(Resource):
    """
    OrderResource class
    Allows the manipulation of a single Order
    GET /order{id} - Returns an Order with the id
    PUT /order{id} - Update an Order with the id
    DELETE /order{id} -  Deletes an Order with the id
    """

    #------------------------------------------------------------------
    # RETRIEVE AN ORDER
    #------------------------------------------------------------------
    @api.doc('get_orders')
    @api.response(404, 'Order not found')
    @api.marshal_with(order_model)
    def get(self, order_id):
        """
        Retrieve a single Order

        This endpoint will return a Order based on it's id
        """
        app.logger.info("Request for order with id: %s", order_id)
        order = Order.find(order_id)
        if not order:
            raise NotFound("Order with id '{}' was not found.".format(order_id))
        return order.serialize(), status.HTTP_200_OK


    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ORDER
    # ------------------------------------------------------------------
    @api.doc('update_orders')
    @api.response(404, 'Order not found')
    @api.response(400, 'The posted Order data was not valid')
    @api.expect(order_model)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """
        Update an Order
        This endpoint will update an Order based the body that is posted
        """
        app.logger.info("Request to update order with id: %s", order_id)
        check_content_type("application/json")
        order = Order.find(order_id)
        if not order:
            api.abort(status.HTTP_404_NOT_FOUND, "Order with id '{}' was not found.".format(order_id))
        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        order.deserialize(data)
        order.id = order_id
        order.update()
        return order.serialize(), status.HTTP_200_OK

######################################################################
#  PATH: /orders/{order_id}/items/{item_id}
######################################################################
@api.route('/orders/<int:order_id>/items/<int:item_id>', strict_slashes=False)
@api.param('order_id', 'The Order identifier')
@api.param('item_id', 'The Order Item identifier')
class OrderItemResource(Resource):
    """
    OrderItemResource class
    Allows the manipulation of a single Order Item
    PUT /orders/{order_id}/items/{item_id} - Update an Order Item with the id
    """

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ORDER ITEM
    # ------------------------------------------------------------------
    @api.doc('update_order_items')
    @api.response(404, 'Order not found')
    @api.response(400, 'The posted Order data was not valid')
    @api.expect(item_model)
    @api.marshal_with(order_model)
    def put(self, order_id, item_id):
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
        return order.serialize(), status.HTTP_200_OK


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
        raise DataValidationError(
            "All the items in this order are DELIVERED/SHIPPED/CANCELED, no items can be shipped.")
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


######################################################################
# DELIVER AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/deliver", methods=["PUT"])
def deliver_orders(order_id):
    """ deliver all the items of the Order that have not being delivered yet """
    app.logger.info("Request to deliver order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))

    cancelled_orders = 0
    for i in range(len(order.order_items)):
        if order.order_items[i].status == "PLACED":
            raise DataValidationError("At least one item in this order is PLACED, order cannot be delivered.")
        elif order.order_items[i].status == "CANCELLED":
            cancelled_orders += 1
        elif order.order_items[i].status != "DELIVERED":
            order.order_items[i].status = "DELIVERED"
    if cancelled_orders == len(order.order_items):
        raise DataValidationError("All the items in this order are CANCELLED, no items can be delivered.")
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