"""
Test Factory to make fake order objects for testing
"""
import factory
from factory.fuzzy import FuzzyDateTime
from factory.fuzzy import FuzzyInteger
from service.models import Order, OrderItem
from .order_item_factory import OrderItemFactory
from datetime import datetime, timezone


class OrderFactory(factory.Factory):
    """ Creates fake orders """

    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n)
    customer_id = FuzzyInteger(0, 10)
    created_date = FuzzyDateTime(datetime(2020, 9, 1, tzinfo=timezone.utc))
    order_items = [OrderItemFactory()]


if __name__ == "__main__":
    for _ in range(10):
        order = OrderFactory()
        print(order.serialize())