"""
Module to define the models for the orders resource.
"""
import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class OrderItem(db.Model):
    """ Class that represents an Order Item """
    app = None

    ##################################################
    # Order Item Table Schema
    ##################################################
    item_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

    def __repr__(self):
        return "<OrderItem %r>" % self.item_id

    def serialize(self):
        """ Serializes a OrderItem into a dictionary """
        return {
            "item_id": self.item_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
            "status": self.status,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a OrderItem from a dictionary

        :param data: a dictionary of attributes
        :type data: dict

        :return: a reference to self
        :rtype: OrderItem
        """
        try:
            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.price = data["price"]
            self.status = data["status"]

            if self.product_id is None or not isinstance(self.product_id, int):
                raise DataValidationError("Invalid order: invalid product ID")
            if self.quantity is None or not isinstance(self.quantity, int):
                raise DataValidationError("Invalid order: invalid quantity")
            if self.price is None or \
                    (not isinstance(self.price, float) and not isinstance(self.price, int)):
                raise DataValidationError("Invalid order: invalid price")
            if self.status is None or not isinstance(self.status, str):
                raise DataValidationError("Invalid order: invalid status")
            if self.status not in ['PLACED', 'SHIPPED', 'DELIVERED', 'CANCELLED']:
                raise DataValidationError("Invalid order: status not in list")
        except KeyError as error:
            raise DataValidationError("Invalid order: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid order: body of request contained bad or no data"
            )
        return self


class Order(db.Model):
    """ Class that represents an Order """
    logger = logging.getLogger(__name__)
    app = None

    ##################################################
    # Order Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime(), default=datetime.now)
    order_items = db.relationship('OrderItem', backref='order', cascade="all, delete", lazy=True)

    def __repr__(self):
        return "<Order %r>" % self.id

    def create(self):
        """
        Creates an order in the database
        """
        if self.customer_id is None:
            raise DataValidationError("Customer Id can't be empty")

        if len(self.order_items) == 0:
            raise DataValidationError("Order Items can't be empty")

        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an Order to the database
        """
        if not self.id or not isinstance(self.id, int):
            raise DataValidationError("Update called with invalid id field")
        if self.customer_id is None or not isinstance(self.customer_id, int):
            raise DataValidationError("Customer id is not valid")
        if len(self.order_items) == 0:
            raise DataValidationError("Order Items can't be empty")
        db.session.commit()

    def delete(self):
        """
        Removes an Order from the data store
        """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes an order into a dictionary """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "created_date": self.created_date,
            "order_items": [order_item.serialize() for order_item in self.order_items]
        }

    def deserialize(self, data: dict):
        """
        Deserializes an Order from a dictionary
        :param data: a dictionary of attributes
        :type data: dict
        :return: a reference to self
        :rtype: Order
        """
        try:
            self.customer_id = data["customer_id"]
            # check if customer_id is integer
            if self.customer_id is None or not isinstance(self.customer_id, int):
                raise DataValidationError("Customer Id must be integer")

            items = data["order_items"]
            if items is None or len(items) == 0:
                raise DataValidationError("Order items can't be empty")
            for data_item in items:
                item = OrderItem()
                item.deserialize(data_item)
                self.order_items.append(item)
        except KeyError as error:
            raise DataValidationError("Invalid order: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid order: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """Initializes the database session

        :param app: the Flask app

        """
        cls.logger.info("Initializing database")
        cls.app = app
        db.init_app(app)
        app.app_context().push()
        db.create_all()

    @classmethod
    def all(cls):
        """ Returns all of the Orders in the database """
        cls.logger.info("Listing all Orders")
        return cls.query.all()

    @classmethod
    def find(cls, order_id):
        """ Finds a Order by it's ID """
        cls.logger.info("Processing lookup for id %s ...", order_id)
        return cls.query.get(order_id)

    @classmethod
    def find_by_customer_id(cls, customer_id: int):
        """Returns all of the orders with customer_id: customer_id """
        cls.logger.info("Processing customer_id query for %s ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id)
