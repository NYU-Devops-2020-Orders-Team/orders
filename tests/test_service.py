"""
Order API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
from unittest import TestCase
from unittest.mock import patch
import os
import logging
from flask_api import status
from flask import abort
from service.models import DataValidationError, db
from service import app
from service.service import init_db
from .order_factory import OrderFactory, OrderItemFactory

logging.disable(logging.CRITICAL)

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb")


def _get_order_factory_with_items(count):
    items = []
    for _ in range(count):
        items.append(OrderItemFactory())
    return OrderFactory(items=items)


######################################################################
#  T E S T   C A S E S
######################################################################

class TestOrderService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.debug = False
        app.testing = True
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        """ Run once after all tests """

    def setUp(self):
        """ Runs before each test """
        init_db()
        db.drop_all()
        db.create_all()
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_orders(self, count):
        """ Factory method to create orders in bulk """
        orders = []
        for _ in range(count):
            test_order = _get_order_factory_with_items(count=1)
            resp = self.app.post(
                "/orders", json=test_order.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test order"
            )
            new_order = resp.get_json()
            test_order.id = new_order["id"]
            order_items = new_order["order_items"]
            for i, item in enumerate(order_items):
                test_order.order_items[i].item_id = item["item_id"]
            orders.append(test_order)
        return orders

    def test_index(self):
        """ Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Orders REST API Service")
        self.assertEqual(data["version"], "1.0")

    def test_create_orders(self):
        """ Create an order """
        order_factory = _get_order_factory_with_items(1)
        resp = self.app.post('/orders',
                             json=order_factory.serialize(),
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_orders_wrong_content_type(self):
        """ Create an order with wrong content type """
        resp = self.app.post('/orders',
                             json=_get_order_factory_with_items(1).serialize(),
                             content_type='application/xml')

        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_orders_customer_id_missing(self):
        """ Create an order missing customer_id """
        order_factory = _get_order_factory_with_items(1)
        order_factory.customer_id = None
        resp = self.app.post('/orders',
                             json=order_factory.serialize(),
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_orders_customer_id_wrong_type(self):
        """ Create an order with invalid customer_id """
        order_factory = _get_order_factory_with_items(1)
        order_factory.customer_id = "string"
        resp = self.app.post('/orders',
                             json=order_factory.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_orders_order_items_missing(self):
        """ Create an order missing order_items """
        resp = self.app.post('/orders',
                             json=_get_order_factory_with_items(0).serialize(),
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_orders_missing_product(self):
        """ Create an order missing product in order_items """
        order_factory = _get_order_factory_with_items(1)
        order_factory.order_items[0].product = None
        resp = self.app.post('/orders',
                             json=order_factory.serialize(),
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_orders_missing_quantity(self):
        """ Create an order missing quantity in order_items """
        order_factory = _get_order_factory_with_items(1)
        order_factory.order_items[0].quantity = None
        resp = self.app.post('/orders',
                             json=order_factory.serialize(),
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_orders_missing_price(self):
        """ Create an order missing price of order_items """
        order_factory = _get_order_factory_with_items(1)
        order_factory.order_items[0].price = None
        resp = self.app.post('/orders',
                             json=order_factory.serialize(),
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_orders_missing_status(self):
        """ Create an order missing status of order_items """
        order_factory = _get_order_factory_with_items(1)
        order_factory.order_items[0].status = None
        resp = self.app.post('/orders',
                             json=order_factory.serialize(),
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_order(self):
        """ Delete an Order """
        test_order = self._create_orders(1)[0]
        resp = self.app.delete(
            "/orders/{}".format(test_order.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure order is deleted
        resp = self.app.get(
            "/orders/{}".format(test_order.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_already_deleted(self):
        """ Attempt to Delete an Order which does not exist in DB """
        resp = self.app.delete(
            "/orders/{}".format(999), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure order is deleted
        resp = self.app.get(
            "/orders/{}".format(999), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order_list_empty_list(self):
        """ Get a list of Orders when no orders present in database """
        resp = self.app.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_get_order_list(self):
        """ Get a list of Orders """
        self._create_orders(5)
        resp = self.app.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_query_order_list_by_customer_id(self):
        """ Query Orders by Customer Id """
        orders = self._create_orders(10)
        test_customer_id = orders[0].customer_id
        customer_id_pets = [order for order in orders if order.customer_id == test_customer_id]
        resp = self.app.get("/orders", query_string="customer_id={}".format(test_customer_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(customer_id_pets))
        # check the data just to be sure
        for pet in data:
            self.assertEqual(pet["customer_id"], test_customer_id)

    def test_query_order_list_by_customer_id_empty(self):
        """ Query Orders by Customer Id where no orders exist """
        test_customer_id = 123
        resp = self.app.get("/orders", query_string="customer_id={}".format(test_customer_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_query_order_list_by_customer_id_not_exists(self):
        """ Query Orders by Customer Id when no order for customer id exists """
        orders = self._create_orders(1)
        test_customer_id = orders[0].customer_id + 1
        resp = self.app.get("/orders", query_string="customer_id={}".format(test_customer_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_wrong_method(self):
        """ Method not allowed """
        resp = self.app.patch("/orders")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_order(self):
        """ Get a single Order """
        test_order = self._create_orders(5)[0]
        resp = self.app.get(
            "/orders/{}".format(test_order.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], test_order.id)
        self.assertEqual(data["customer_id"], test_order.customer_id)
        self.assertEqual(len(data["order_items"]), len(test_order.order_items))

    def test_get_order_invalid_id(self):
        """ Get an single Order with an invalid id """
        resp = self.app.get(
            "/orders/{}".format(0), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND, "Not Found")

    @patch('service.service.create_orders')
    def test_bad_request(self, bad_request_mock):
        """ Bad Request error from Create Order """
        bad_request_mock.side_effect = DataValidationError()
        resp = self.app.post('/orders', json="",
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_internal_server_error(self):
        """ Internal Server error from Create Order """

        @app.route('/orders/500Error')
        def internal_server_error():
            abort(500)

        resp = self.app.get('/orders/500Error')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_update_order(self):
        """ Update an existing Order """
        # create an order to update
        test_order = self._create_orders(5)[0]

        resp = self.app.put('/orders/{}'.format(test_order.id), json={'customer_id': 123},
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["customer_id"], 123)

    def test_update_order_not_exists(self):
        """ Update an existing Order when the order does not exist """
        resp = self.app.put('/orders/{}'.format(0), json={'customer_id': 123},
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_order_not_exists(self):
        """ Update an existing Order when the order does not exist """
        resp = self.app.put('/orders/{}'.format(0), json={'customer_id': 123},
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_customer_id_missing(self):
        """ Update an existing Order when customer_id is missing in request """
        resp = self.app.put('/orders/{}'.format(0), json={},
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_customer_id_none(self):
        """ Update an existing Order when customer_id is missing in request """
        resp = self.app.put('/orders/{}'.format(0), json={'customer_id': None},
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_item(self):
        """ Update an existing Order Item """
        # create an order to update
        test_order = self._create_orders(1)[0]
        item_id = test_order.order_items[0].item_id
        order_item = OrderItemFactory()
        resp = self.app.put('/orders/{}/items/{}'.format(test_order.id, item_id),
                            json=order_item.serialize(),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()["order_items"][0]
        self.assertEqual(new_item["product"], order_item.product)
        self.assertEqual(new_item["quantity"], order_item.quantity)
        self.assertAlmostEqual(new_item["price"], order_item.price)
        self.assertEqual(new_item["status"], order_item.status)

    def test_update_order_item_order_not_exists(self):
        """ Update an existing Order Item when order is not present"""
        resp = self.app.put('/orders/{}/items/{}'.format(0, 0), json="",
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_item_not_exists(self):
        """ Update an existing Order Item when order item is not present """
        # create an order to update
        test_order = self._create_orders(1)[0]
        item_id = test_order.order_items[0].item_id + 1
        order_item = OrderItemFactory()
        resp = self.app.put('/orders/{}/items/{}'.format(test_order.id, item_id),
                            json=order_item.serialize(),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def _create_new_order(self, order_factory):
        resp = self.app.post('/orders',
                             json=order_factory.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        return resp.get_json()

    def test_cancel_order(self):
        """ Cancel an order """
        order = self._create_orders(1)[0]
        resp = self.app.put("/orders/{}/cancel".format(order.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK, 'Could not cancel the order')

    def test_cancel_order_not_found(self):
        """ Cancel an order when order does not exist"""
        resp = self.app.put("/orders/{}/cancel".format(0))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_order_with_all_shipped(self):
        """ Cancel an order with all shipped/delivered items """
        order_factory = _get_order_factory_with_items(2)
        order_factory.order_items[0].status = "SHIPPED"
        order_factory.order_items[1].status = "DELIVERED"

        new_order_id = self._create_new_order(order_factory)["id"]

        resp = self.app.put("/orders/{}/cancel".format(new_order_id))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_order_with_some_shipped(self):
        """ Cancel an order with all shipped/delivered items """
        order_factory = _get_order_factory_with_items(2)
        order_factory.order_items[0].status = "SHIPPED"

        new_order_id = self._create_new_order(order_factory)["id"]

        resp = self.app.put("/orders/{}/cancel".format(new_order_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_cancel_order_item(self):
        """ Cancel an order item """
        order = self._create_orders(1)[0]
        item_id = order.order_items[0].item_id
        resp = self.app.put("/orders/{}/items/{}/cancel".format(order.id, item_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK, 'Could not cancel the order')

    def test_cancel_order_item_order_not_found(self):
        """ Cancel an order item when order does not exist"""
        resp = self.app.put("/orders/{}/items/{}/cancel".format(0, 0))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_order_item_not_found(self):
        """ Cancel an order item when order item does not exist"""
        order = self._create_orders(1)[0]
        resp = self.app.put("/orders/{}/items/{}/cancel".format(order.id, 0))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_order_item_with_shipped(self):
        """ Cancel an order item with shipped/delivered status """
        order_factory = _get_order_factory_with_items(2)
        order_factory.order_items[0].status = "SHIPPED"

        new_order_json = self._create_new_order(order_factory)
        new_order_id = new_order_json["id"]
        new_item_id = new_order_json["order_items"][0]["item_id"]
        resp = self.app.put("/orders/{}/items/{}/cancel".format(new_order_id, new_item_id))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ship_order_item(self):
        """ Ship an order item """
        order = self._create_orders(1)[0]
        item_id = order.order_items[0].item_id
        resp = self.app.put("/orders/{}/items/{}/ship".format(order.id, item_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_ship_order_item_order_not_found(self):
        """ Ship an order item when order does not exist"""
        resp = self.app.put("/orders/{}/items/{}/ship".format(0, 0))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_ship_order_item_not_found(self):
        """ Ship an order item when order item does not exist"""
        order = self._create_orders(1)[0]
        resp = self.app.put("/orders/{}/items/{}/ship".format(order.id, 0))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_ship_order_item_with_cancelled(self):
        """ Ship an order item with cancelled status """
        order_factory = _get_order_factory_with_items(2)
        order_factory.order_items[0].status = "CANCELLED"

        new_order_json = self._create_new_order(order_factory)
        new_order_id = new_order_json["id"]
        new_item_id = new_order_json["order_items"][0]["item_id"]
        resp = self.app.put("/orders/{}/items/{}/ship".format(new_order_id, new_item_id))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ship_order_item_with_delivered(self):
        """ Ship an order item with delivered status """
        order_factory = _get_order_factory_with_items(2)
        order_factory.order_items[0].status = "DELIVERED"

        new_order_json = self._create_new_order(order_factory)
        new_order_id = new_order_json["id"]
        new_item_id = new_order_json["order_items"][0]["item_id"]
        resp = self.app.put("/orders/{}/items/{}/ship".format(new_order_id, new_item_id))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deliver_order_item(self):
        """ Deliver an order item """
        order_factory = _get_order_factory_with_items(2)
        order_factory.order_items[0].status = "SHIPPED"

        new_order_json = self._create_new_order(order_factory)
        new_order_id = new_order_json["id"]
        new_item_id = new_order_json["order_items"][0]["item_id"]
        resp = self.app.put("/orders/{}/items/{}/deliver".format(new_order_id, new_item_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)        

    def test_deliver_order_item_order_not_found(self):
        """ Deliver an order item when order does not exist"""
        resp = self.app.put("/orders/{}/items/{}/deliver".format(0, 0))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_deliver_order_item_item_not_found(self):
        """ Deliver an order item when order item does not exist"""
        order = self._create_orders(1)[0]
        resp = self.app.put("/orders/{}/items/{}/deliver".format(order.id, 0))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_deliver_order_item_with_placed_status(self):
        """ Deliver an order item with placed status """
        order_factory = _get_order_factory_with_items(2)
        order_factory.order_items[0].status = "PLACED"

        new_order_json = self._create_new_order(order_factory)
        new_order_id = new_order_json["id"]
        new_item_id = new_order_json["order_items"][0]["item_id"]
        resp = self.app.put("/orders/{}/items/{}/deliver".format(new_order_id, new_item_id))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deliver_order_item_with_cancelled_status(self):
        """ Deliver an order item with cancelled status """
        order_factory = _get_order_factory_with_items(2)
        order_factory.order_items[0].status = "CANCELLED"

        new_order_json = self._create_new_order(order_factory)
        new_order_id = new_order_json["id"]
        new_item_id = new_order_json["order_items"][0]["item_id"]
        resp = self.app.put("/orders/{}/items/{}/deliver".format(new_order_id, new_item_id))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deliver_order_item_with_delivered_status(self):
        """ Deliver an order item with delivered status """
        order_factory = _get_order_factory_with_items(2)
        order_factory.order_items[0].status = "DELIVERED"

        new_order_json = self._create_new_order(order_factory)
        new_order_id = new_order_json["id"]
        new_item_id = new_order_json["order_items"][0]["item_id"]
        resp = self.app.put("/orders/{}/items/{}/deliver".format(new_order_id, new_item_id))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
