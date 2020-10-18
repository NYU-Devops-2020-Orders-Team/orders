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
        resp = self.app.post('/orders',
            json = {"customer_id": "c1", 
                    "order_items": [
                            {"product": "p1",
                            "quantity": 5,
                            "price": 500,
                            "status": "PLACED"
                            }]
                    },
            content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED,'Could not create test order')

        # create an order with empty customer_id
        resp = self.app.post('/orders',
            json = {"customer_id": "", 
                    "order_items": [
                            {"product": "p1",
                            "quantity": 5,
                            "price": 500,
                            "status": "PLACED"
                            }]
                    },
            content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST,'Could not identify bad request')        

