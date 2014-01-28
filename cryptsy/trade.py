# Copyright (c) 2014 Henry S. Harrison

from decimal import Decimal
from datetime import datetime

from cryptsy.common import DATETIME_FORMAT


def parse_trade_list(trades, market_id=None):
    if market_id:
        trade_list = []
        for trade in trades:
            trade.update(marketid=market_id)
            trade_list.append(Trade(**trade))
        return trade_list
    else:
        return [Trade(**trade) for trade in trades]


class Trade(object):
    def __init__(self, **kwargs):
        self.market_id = kwargs['marketid']

        # These attributes are the same for all methods returning trade info.
        self.quantity = Decimal(kwargs.get('quantity'))
        self.total = Decimal(kwargs.get('total'))

        # These attributes have different keys for different methods.
        tradeid = kwargs.get('tradeid')
        if not tradeid:
            tradeid = kwargs.get('id')
        self.id = int(tradeid)

        time = kwargs.get('datetime')
        if not time:
            time = kwargs.get('time')
        self.time = datetime.strptime(time, DATETIME_FORMAT)

        tradeprice = kwargs.get('tradeprice')
        if not tradeprice:
            tradeprice = kwargs.get('price')
        self.price = Decimal(tradeprice)

        # These attributes are missing from some methods.
        self.initiate_ordertype = kwargs.get('initiate_ordertype')
        self.trade_type = kwargs.get('tradetype')

        fee = kwargs.get('fee')
        if fee:
            self.fee = Decimal(fee)
        else:
            self.fee = None

        order_id = kwargs.get('order_id')
        if order_id:
            self.order_id = int(order_id)
        else:
            self.order_id = None
