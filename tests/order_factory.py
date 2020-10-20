"""
Test Factory to make fake objects for testing
"""
import random
import factory
from factory.fuzzy import FuzzyChoice
from flask_sqlalchemy import SQLAlchemy
from service.models import Order, OrderItem

db = SQLAlchemy()


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """ Base Factory for SQLAlchemy """
    class Meta:
        """ Meta Class """
        abstract = True
        sqlalchemy_session = db.session


class OrderFactory(BaseFactory):
    """ Creates fake orders """

    class Meta:
        """ Meta class for Order Factory """
        model = Order

    id = factory.Sequence(lambda n: n)
    customer_id = random.randint(0, 100000)
    order_items = []

    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        """ Method to add items to Order Foctory """
        if not create:
            return

        if extracted:
            self.order_items = extracted


class OrderItemFactory(BaseFactory):
    """ Creates fake order items """

    class Meta:
        """ Meta class for Order Item Factory """
        model = OrderItem

    item_id = factory.Sequence(lambda n: n)
    product = factory.Faker('sentence', nb_words=1, variable_nb_words=True)
    quantity = random.randint(0, 100000)
    price = random.uniform(0, 100000)
    status = FuzzyChoice(choices=["PLACED"])
    order_id = factory.SubFactory(OrderFactory)


if __name__ == "__main__":
    for _ in range(5):
        item1 = OrderItemFactory()
        item2 = OrderItemFactory()
        item3 = OrderItemFactory()
        order = OrderFactory(items=[item1, item2, item3])
        print(order.serialize())
