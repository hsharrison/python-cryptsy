# Copyright (c) 2014 Henry S. Harrison

from decimal import Decimal
from datetime import datetime

from cryptsy.common import DATETIME_FORMAT


def parse_order_list(orders, type_=None, market_id=None):
    if not type_ and not market_id:
        return [Order(**order) for order in orders]
    else:
        order_list = []
        for order in orders:
            if type_:
                order.update(ordertype=type_)
            if market_id:
                order.update(marketid=market_id)
            order_list.append(Order(**order))
        return order_list


class Order(object):
    def __init__(self, **kwargs):
        self.market_id = kwargs['marketid']
        self.type = kwargs['ordertype']

        # These attributes are present in all methods returning order info.
        self.quantity = Decimal(kwargs.get('quantity'))
        self.total = Decimal(kwargs.get('total'))

        # These attributes have different keys in different methods
        price = kwargs.get('price')
        if not price:
            price = kwargs.get(self.type + 'price')
        self.price = Decimal(price)

        # These attributes don't exist in all methods.
        order_id = kwargs.get('orderid')
        if order_id:
            self.id = int(order_id)
        else:
            self.id = None

        time_created = kwargs.get('created')
        if isinstance(time_created, datetime):
            self.time_created = time_created
        elif time_created:
            self.time_created = datetime.strptime(time_created, DATETIME_FORMAT)
        else:
            self.time_created = None

        original_quantity = kwargs.get('orig_quantity')
        if original_quantity:
            self.original_quantity = Decimal(original_quantity)
        else:
            self.original_quantity = None
