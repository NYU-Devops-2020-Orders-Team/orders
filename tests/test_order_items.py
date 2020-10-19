import unittest
from datetime import datetime
import os
from service.models import OrderItem, DataValidationError, db
from service import app

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb")


######################################################################
#  T E S T   C A S E S
######################################################################
class TestOrderItems(unittest.TestCase):
    """ Test Cases for Order Items """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        """ These run once after Test suite """
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_repr(self):
        """ Create an order item and test it's repr """
        order_item = OrderItem(item_id=1, product="product", quantity=1, price=5, status="PLACED", order_id=1)
        self.assertEqual(order_item.__repr__(), "<OrderItem 1>")

    def test_repr_with_no_item_id(self):
        """ Create an order item and test it's repr with no item id """
        order_item = OrderItem(product="product", quantity=1, price=5, status="PLACED", order_id=1)
        self.assertEqual(order_item.__repr__(), "<OrderItem None>")

    def test_init_order(self):
        """ Create an order item and assert that it exists """
        order_item = OrderItem(product="product", quantity=1, price=5, status="PLACED", order_id=1)
        self.assertTrue(order_item is not None)
        self.assertEqual(order_item.item_id, None)
        self.assertEqual(order_item.product, 'product')
        self.assertEqual(order_item.price, 5)
        self.assertEqual(order_item.status, "PLACED")
        self.assertEqual(order_item.order_id, 1)

    def test_serialize_an_order_item(self):
        """ Test serialization of an Order Item """
        order_item = OrderItem(product="product", quantity=1, price=5, status="PLACED")
        data = order_item.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("item_id", data)
        self.assertEqual(data["item_id"], None)
        self.assertIn("product", data)
        self.assertEqual(data["product"], "product")
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], 1)
        self.assertIn("price", data)
        self.assertEqual(data["price"], 5)
        self.assertIn("status", data)
        self.assertEqual(data["status"], "PLACED")

    def test_deserialize_an_order(self):
        """ Test deserialization of an Order Item"""
        data = {"product": "product", "quantity": 1, "price": 5.0, "status": "PLACED"}
        order_item = OrderItem()
        order_item.deserialize(data)
        self.assertNotEqual(order_item, None)
        self.assertEqual(order_item.item_id, None)
        self.assertEqual(order_item.product, "product")
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(order_item.price, 5)
        self.assertEqual(order_item.status, "PLACED")

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad order item data """
        data = "this is not a dictionary"
        order = OrderItem()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_bad_data_with_keys_missing(self):
        """ Test deserialization of bad order item data with few keys missing """
        data = {"product": "product", "status": "PLACED"}
        order = OrderItem()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_bad_data_with_wrong_product(self):
        """ Test deserialization of bad order item data with product None """
        data = {"product": None, "quantity": 1, "price": 5.0, "status": "PLACED"}
        order = OrderItem()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_bad_data_with_wrong_quantity(self):
        """ Test deserialization of bad order item data with quantity not as int """
        data = {"product": "product", "quantity": "1", "price": 5.0, "status": "PLACED"}
        order = OrderItem()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_bad_data_with_wrong_price(self):
        """ Test deserialization of bad order item data with price not as float/int """
        data = {"product": "product", "quantity": 1, "price": "5.0", "status": "PLACED"}
        order = OrderItem()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_bad_data_with_wrong_status(self):
        """ Test deserialization of bad order item data with status as None """
        data = {"product": "product", "quantity": 1, "price": 5.0, "status": None}
        order = OrderItem()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_bad_data_with_wrong_status_not_in_list(self):
        """ Test deserialization of bad order item data with status as None """
        data = {"product": "product", "quantity": 1, "price": 5.0, "status": "None"}
        order = OrderItem()
        self.assertRaises(DataValidationError, order.deserialize, data)