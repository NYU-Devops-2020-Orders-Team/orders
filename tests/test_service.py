"""
Order API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
from unittest import TestCase
import os
import logging
from flask_api import status  # HTTP Status Codes
# from unittest.mock import MagicMock, patch
from service.models import Order, DataValidationError, db
from service import app
from service.service import init_db

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

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Orders REST API Service")
        self.assertEqual(data["version"], "1.0")


    def test_create_orders(self):
        ''''Create an order'''
        # test_order={"customer_id": "c1", 
        #             "order_items": [
        #                     {"product": "p1",
        #                     "quantity": 5,
        #                     "price": 500,
        #                     "status": "PLACED"
        #                     }]
        #             }

        # resp = self.app.post('/orders',
        #     json =test_order,
        #     content_type='application/json')

        # self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # # Check the data is correct
        # new_order = resp.get_json()
        # self.assertEqual(new_order["customer_id"], test_order.customer_id, "Names do not match")
        # self.assertEqual(
        #     new_order["order_items"], test_order.order_items, "order_items do not match"
        # )

        # create an order missing customer_id
        resp = self.app.post('/orders',
            json = {"customer_id":None, 
                    "order_items": [
                            {
                            "quantity": 5,
                            "price": 500,
                            "status": "PLACED"
                            }]
                    },
            content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,'Could not identify bad request')    


        # create an order missing product of order_items
        resp = self.app.post('/orders',
            json = {"customer_id":123, 
                    "order_items": [
                            {
                            "quantity": 5,
                            "price": 500,
                            "status": "PLACED"
                            }]
                    },
            content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,'Could not identify bad request')    

         # create an order missing quantity of order_items
        resp = self.app.post('/orders',
            json = {"customer_id":123, 
                    "order_items": [
                            {"product": "p1",
                            "price": 500,
                            "status": "PLACED"
                            }]
                    },
            content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,'Could not identify bad request')    

           # create an order missing price of order_items
        resp = self.app.post('/orders',
            json = {"customer_id":123, 
                    "order_items": [
                            {"product": "p1",
                            "quantity": 5,
                            "status": "PLACED"
                            }]
                    },
            content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,'Could not identify bad request')    

           # create an order missing status of order_items
        resp = self.app.post('/orders',
            json = {"customer_id":123, 
                    "order_items": [
                            {"product": "p1",
                            "quantity": 5,
                            "price": 500
                            }]
                    },
            content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,'Could not identify bad request')    

     


