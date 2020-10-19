"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyText, FuzzyFloat
from service.models import OrderItem


class OrderItemFactory(factory.Factory):
    """ Creates fake orders """

    class Meta:
        model = OrderItem

    item_id = factory.Sequence(lambda n: n)
    product = FuzzyText(length = 5, prefix = "p")
    quantity = FuzzyInteger(0, 10)
    price = FuzzyFloat(0.5, 50, 2)
    status = FuzzyChoice(choices=["Pending","Processing","Shipped","Delivered","Canceled"])
    order_id = FuzzyInteger(0, 10)


if __name__ == "__main__":
    for _ in range(10):
        order_item = OrderItemFactory()
        print(order_item.serialize())