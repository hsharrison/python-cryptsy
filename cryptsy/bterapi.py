# Copyright (C) 2014 Henry S. Harrison

import time
from decimal import Decimal

from cryptsy.private import AuthenticatedSession


class TradeAPI(AuthenticatedSession):
    def __init__(self, *args, **kwargs):
        super(TradeAPI, self).__init__(*args, **kwargs)
        _, self.market_ids = self.get_market_ids()
        self.all_pairs = list(self.market_ids.keys())

    def getFunds(self):
        info = self.getinfo()
        funds = {'balance_' + currency: balance for currency, balance in info['balances_available'].items()}
        return funds

    def placeOrder(self, pair, order_type, price, quantity, update_delay=None):
        result = self.createorder(self.market_ids[pair], order_type, quantity, price)
        result.remains = result.quantity

        if update_delay:
            time.sleep(update_delay)
            orders = self.myorders(self.market_ids[pair])
            updated_order = next((order for order in orders if order.id == result.id), None)

            if updated_order:
                result = updated_order
                result.remains = result.quantity
            else:  # Order completed
                result.remains = Decimal(0)
                result.quantity = Decimal(0)

        return result

    def getDepth(self, pair):
        depth = self.depth(self.market_ids[pair])
        return depth['sell'], depth['buy']

    def orderList(self):
        orders = self.allmyorders()
        for order in orders:
            order.remains = order.quantity

TradeAPI.cancelOrder = TradeAPI.cancelorder
