"""
Order API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
from unittest import TestCase
from unittest.mock import MagicMock
import os
import logging
from flask_api import status  # HTTP Status Codes
# from unittest.mock import MagicMock, patch
from service.models import Order, DataValidationError, db
from .order_factory import OrderFactory
from service import app
from service.service import init_db
from .order_factory import OrderFactory, OrderItemFactory

logging.disable(logging.CRITICAL)

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb")


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
        pass

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
            item1 = OrderItemFactory()
            item2 = OrderItemFactory()
            item3 = OrderItemFactory()
            test_order = OrderFactory(items=[item1, item2, item3])
            resp = self.app.post(
                "/orders", json=test_order.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test order"
            )
            new_order = resp.get_json()
            test_order.id = new_order["id"]

            created_order = Order()
            created_order.deserialize(new_order)
            for i in range(len(created_order.order_items)):
                test_order.order_items[i].item_id = created_order.order_items[i].item_id
            orders.append(test_order)
        return orders

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Orders REST API Service")
        self.assertEqual(data["version"], "1.0")

    def test_create_orders(self):
        """ create an order """
        resp = self.app.post('/orders',
                             json={"customer_id": 123,
                                   "order_items": [
                                       {
                                           "product": "product1",
                                           "quantity": 5,
                                           "price": 500,
                                           "status": "PLACED"
                                       }]
                                   },
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, 'Could not create order')

    def test_create_orders_wrong_content_type(self):
        """ create an order """
        resp = self.app.post('/orders',
                             json={"customer_id": 123,
                                   "order_items": [
                                       {
                                           "quantity": 5,
                                           "price": 500,
                                           "status": "PLACED"
                                       }]
                                   },
                             content_type='application/xml')

        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Could not create order')

    def test_create_orders_customer_id_missing(self):
        """ create an order missing customer_id """
        resp = self.app.post('/orders',
                             json={"customer_id": None,
                                   "order_items": [
                                       {
                                           "quantity": 5,
                                           "price": 500,
                                           "status": "PLACED"
                                       }]
                                   },
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, 'Could not identify bad request')

    def test_create_orders_customer_id_wrong_type(self):
        """ create an order with invalid customer_id """
        resp = self.app.post('/orders',
                             json={"customer_id": "abc",
                                   "order_items": [
                                       {
                                           "quantity": 5,
                                           "price": 500,
                                           "status": "PLACED"
                                       }]
                                   },
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, 'Could not identify bad request')

    def test_create_orders_order_items_missing(self):
        """ create an order missing order_items """
        resp = self.app.post('/orders',
                             json={"customer_id": 123,
                                   "order_items": None
                                   },
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, 'Could not identify bad request')

    def test_create_orders_missing_product(self):
        """ create an order missing product in order_items """
        resp = self.app.post('/orders',
                             json={"customer_id": 123,
                                   "order_items": [
                                       {
                                           "quantity": 5,
                                           "price": 500,
                                           "status": "PLACED"
                                       }]
                                   },
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, 'Could not identify bad request')

    def test_create_orders_missing_quantity(self):
        """ create an order missing quantity in order_items """
        resp = self.app.post('/orders',
                             json={"customer_id": 123,
                                   "order_items": [
                                       {"product": "p1",
                                        "price": 500,
                                        "status": "PLACED"
                                        }]
                                   },
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, 'Could not identify bad request')

    def test_create_orders_missing_price(self):
        """ create an order missing price of order_items """
        resp = self.app.post('/orders',
                             json={"customer_id": 123,
                                   "order_items": [
                                       {"product": "p1",
                                        "quantity": 5,
                                        "status": "PLACED"
                                        }]
                                   },
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, 'Could not identify bad request')

    def test_create_orders_missing_status(self):
        """ create an order missing status of order_items """
        resp = self.app.post('/orders',
                             json={"customer_id": 123,
                                   "order_items": [
                                       {"product": "p1",
                                        "quantity": 5,
                                        "price": 500
                                        }]
                                   },
                             content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, 'Could not identify bad request')

    def test_get_order_list_empty_list(self):
        """ Get a list of Orders when no orders present in database """
        resp = self.app.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)
        
    # def test_get_order_list(self):
    #     """ Get a list of Orders """
    #     self._create_orders(5)
    #     resp = self.app.get("/orders")
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     data = resp.get_json()
    #     self.assertEqual(len(data), 5)

    def test_get_order_list(self):
        """ Get a list of Orders """
        self._create_orders(5)
        resp = self.app.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_wrong_method(self):
        """ Test if wrong method gives the correct error """
        resp = self.app.patch("/orders")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_order(self):
        """ Get a single Order """
        # get the id of an order
        test_order = self._create_orders(1)[0]
        resp = self.app.get(
            "/orders/{}".format(test_order.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_order.name)
