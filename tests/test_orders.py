""" Module for Order tests """
import unittest
from datetime import datetime
import os
from service.models import Order, OrderItem, DataValidationError, db
from service import app

DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb")


######################################################################
#  T E S T   C A S E S
######################################################################
class TestOrders(unittest.TestCase):
    """ Test Cases for Orders """

    @classmethod
    def setUpClass(cls):
        """ These run once before Test suite """
        app.debug = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        Order.init_db(app)
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_init_order(self):
        """ Initialize an order and assert that it exists """
        order_items = [OrderItem(product="product", quantity=1, price=5, status="PLACED")]
        order = Order(customer_id=123, order_items=order_items)
        self.assertTrue(order is not None)
        self.assertEqual(order.id, None)
        self.assertEqual(order.customer_id, 123)
        self.assertEqual(len(order.order_items), 1)

    def test_repr(self):
        """ Create an order and test it's repr """
        order = Order(id=1, customer_id=123)
        self.assertEqual(order.__repr__(), "<Order 1>")

    def test_repr_with_no_item_id(self):
        """ Create an order and test it's repr with no item id """
        order = Order(customer_id=123)
        self.assertEqual(order.__repr__(), "<Order None>")

    def test_create_order(self):
        """ Create an order with a single item in the database """
        order_item = OrderItem(product="product", quantity=1, price=5, status="PLACED")
        order_items = [order_item]
        order = Order(customer_id=123, order_items=order_items)
        self.assertTrue(order is not None)
        self.assertEqual(order.id, None)
        self.assertEqual(len(order.order_items), 1)
        self.assertEqual(order.order_items[0].item_id, None)
        order.create()
        self.assertEqual(order.id, 1)
        self.assertEqual(order.customer_id, 123)
        self.assertEqual(len(order.order_items), 1)
        self.assertEqual(order.order_items[0].item_id, 1)
        self.assertEqual(order.order_items[0].order_id, 1)

    def test_create_order_with_no_customer_id(self):
        """ Create an order with no customer id """
        order_item = OrderItem(product="product", quantity=1, price=5, status="PLACED")
        order_items = [order_item]
        order = Order(order_items=order_items)
        self.assertRaises(DataValidationError, order.create)

    def test_create_order_with_multiple_items(self):
        """ Create an order with multiple order items """
        order_item1 = OrderItem(product="product1", quantity=1, price=5, status="PLACED")
        order_item2 = OrderItem(product="product2", quantity=1, price=5, status="PLACED")
        order_items = [order_item1, order_item2]
        order = Order(customer_id=123, order_items=order_items)
        order.create()
        self.assertTrue(order.id is not None)
        order_id = order.id
        self.assertEqual(order.customer_id, 123)
        self.assertEqual(len(order.order_items), 2)
        i = order.order_items[0].item_id
        for j in range(0, len(order.order_items)):
            self.assertEqual(order.order_items[j].item_id, i)
            self.assertEqual(order.order_items[j].order_id, order_id)
            i += 1

    def test_create_order_with_no_item(self):
        """ Create an order with no items in the database """
        order_items = []
        order = Order(customer_id=123, order_items=order_items)
        self.assertRaises(DataValidationError, order.create)

    def test_update_an_order(self):
        """ Update an existing Order """
        order_item1 = OrderItem(product="p1", quantity=1, price=5, status="PLACED")
        order_items = [order_item1]
        order = Order(customer_id=111, order_items=order_items)
        order.create()
        self.assertTrue(order.id is not None)

        order.customer_id = 234
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(new_order.id, order.id)
        self.assertEqual(new_order.customer_id, 234)

    def test_update_an_order_not_exists(self):
        """ Update a non-existing Order """
        order_item1 = OrderItem(product="p1", quantity=1, price=5, status="PLACED")
        order_items = [order_item1]
        order = Order(id=1234567, customer_id=111, order_items=order_items)
        order.update()
        self.assertRaises(DataValidationError)

    def test_update_order_with_no_id(self):
        """ Update an order with no id """
        order_item = OrderItem(product="product", quantity=1, price=5, status="PLACED")
        order_items = [order_item]
        order = Order(customer_id=123, order_items=order_items)
        self.assertRaises(DataValidationError, order.update)

    def test_update_order_with_no_customer_id(self):
        """ Update an order with no customer id """
        order_item = OrderItem(product="product", quantity=1, price=5, status="PLACED")
        order_items = [order_item]
        order = Order(id=1, order_items=order_items)
        self.assertRaises(DataValidationError, order.update)

    def test_update_order_with_no_order_items(self):
        """ Update an order with no order items"""
        order = Order(id=1, customer_id=123)
        self.assertRaises(DataValidationError, order.update)

    def test_serialize_an_order(self):
        """ Serialization of an Order """
        date = datetime.now
        order_item = OrderItem(product="product", quantity=1, price=5, status="PLACED")
        order_item2 = OrderItem(product="product2", quantity=1, price=5, status="PLACED")
        order_items = [order_item, order_item2]
        order = Order(customer_id=123, created_date=date, order_items=order_items)
        data = order.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], None)
        self.assertIn("customer_id", data)
        self.assertEqual(data["customer_id"], 123)
        self.assertIn("created_date", data)
        self.assertEqual(data["created_date"], date)
        self.assertIn("order_items", data)
        self.assertEqual(data["order_items"], [order_item.serialize(), order_item2.serialize()])

    def test_deserialize_an_order(self):
        """ Deserialization of an Order """
        data = {"customer_id": 123,
                "order_items": [
                    {"product": "product",
                     "quantity": 1,
                     "price": 5,
                     "status": "PLACED"}
                ]}
        order = Order()
        order.deserialize(data)
        self.assertNotEqual(order, None)
        self.assertEqual(order.id, None)
        self.assertEqual(order.customer_id, 123)
        self.assertEqual(order.created_date, None)
        self.assertEqual(len(order.order_items), 1)
        self.assertEqual(order.order_items[0].item_id, None)
        self.assertEqual(order.order_items[0].product, "product")

    def test_deserialize_bad_data(self):
        """ Deserialization of bad data """
        data = "this is not a dictionary"
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_bad_data_with_keys_missing(self):
        """ Deserialization of bad order data with few keys missing """
        data = {"order_items": [{
            "product": "product",
            "quantity": 1,
            "price": 5,
            "status": "PLACED"
        }]}
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_find_order(self):
        """ Find an Order by ID """
        order_items1 = [OrderItem(product="product1", quantity=1, price=5, status="PLACED")]
        order1 = Order(customer_id=111, order_items=order_items1)
        order1.create()
        order = Order.find(order1.id)
        self.assertIsNot(order, None)
        self.assertEqual(order.id, order1.id)
        self.assertEqual(order.customer_id, 111)
        self.assertEqual(len(order.order_items), 1)
        self.assertEqual(order.order_items[0].product, "product1")

    def test_find_invalid_order(self):
        """ Find an Order by an invalid ID """
        order = Order.find(0)
        self.assertEqual(order, None)

    def test_delete_an_order(self):
        """ Delete an Order """
        order_items1 = [OrderItem(product="product1", quantity=1, price=5.0, status="PLACED")]
        order = Order(customer_id=111, order_items=order_items1)
        order.create()
        self.assertEqual(len(Order.all()), 1)
        # delete the order and make sure it isn't in the database
        order.delete()
        self.assertEqual(len(Order.all()), 0)


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
