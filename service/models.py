import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class OrderItem(db.Model):
    app = None

    ##################################################
    # Order Item Table Schema
    ##################################################
    item_id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(40), nullable=False)
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
            "product": self.product,
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
            self.product = data["product"]
            self.quantity = data["quantity"]
            self.price = data["price"]
            self.status = data["status"]
        except KeyError as error:
            raise DataValidationError("Invalid order: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid order: body of request contained bad or no data"
            )
        return self


class Order(db.Model):
    """
    Class that represents an Order
    """
    logger = logging.getLogger(__name__)
    app = None

    ##################################################
    # Order Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime(), default=datetime.now)
    order_items = db.relationship('OrderItem', backref='order')

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
        if not self.id:
            raise DataValidationError("Update called with empty id field")
        if self.customer_id is None:
            raise DataValidationError("Customer id can't be empty")
        if len(self.order_items) == 0:
            raise DataValidationError("Order Items can't be empty")
        if not isinstance(self.id, int):
            raise DataValidationError("Id should be an integer")
        if not isinstance(self.customer_id, int):
            raise DataValidationError("Customer id should be an integer")
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
            items = data["order_items"]
            for i in range(len(items)):
                item = OrderItem()
                item.deserialize(items[i])
                self.order_items.append(item)
        except KeyError as error:
            raise DataValidationError("Invalid order: missing " + error.args[0])
        except TypeError as error:
            print(error)
            raise DataValidationError(
                "Invalid order: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """Initializes the database session

        :param app: the Flask app
        :type data: Flask

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
