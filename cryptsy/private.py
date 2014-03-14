# Copyright (c) 2014 Henry S. Harrison

import requests
import hmac
import logging
import re
from hashlib import sha512
from decimal import Decimal
from datetime import datetime

try:
    from urllib import urlencode
except ImportError:  # Python3 compatibility
    from urllib.parse import urlencode

from cryptsy.common import COMMON_HEADERS, CryptsyError, DATETIME_FORMAT
from cryptsy.trade import parse_trade_list
from cryptsy.order import parse_order_list, Order


URL = 'https://www.cryptsy.com/api'


class AuthenticatedSession(object):
    def __init__(self, key_file, request_kwargs=None):
        with open(key_file, 'rt') as f:
            key = f.readline().strip()
            self.secret = f.readline().strip()

        self.nonce = 0
        self.session = requests.Session()
        self.session.headers.update(COMMON_HEADERS)
        self.session.headers.update({'Key': key})

        if request_kwargs:
            self.kwargs = request_kwargs
        else:
            self.kwargs = {}

        self.pair_to_id, self.id_to_pair = self.get_market_ids()

    def get_sign(self, params):
        hasher = hmac.new(self.secret.encode(), digestmod=sha512)
        hasher.update(urlencode(params).encode())
        return hasher.hexdigest()

    def request(self, method, params=None):
        if not params:
            params = {}

        self.nonce += 1
        params.update({'method': method, 'nonce': self.nonce})
        sign = self.get_sign(params)

        response = self.session.post(URL, params, headers={'Sign': sign}, **self.kwargs)
        response.raise_for_status()

        parsed_response = response.json()
        if parsed_response['success'] == '0':
            raise CryptsyError(parsed_response['error'])

        try:
            return parsed_response['return']
        except KeyError:  # A few methods don't use the 'return' attribute.
            return parsed_response

    def getinfo(self):
        response = self.request('getinfo')
        response['balances_available'] = {
            currency: Decimal(balance) for currency, balance in response['balances_available'].items()}
        if response['openordercount'] > 0:
            response['balances_hold'] = {
                currency: Decimal(balance) for currency, balance in response['balances_hold'].items()}
        response['servertime'] = datetime.fromtimestamp(response['servertimestamp'])
        return response

    def getmarkets(self):
        response = self.request('getmarkets')
        for market in response:
            market['created'] = datetime.strptime(market['created'], DATETIME_FORMAT)
            market['current_volume'] = Decimal(market['current_volume'])
            market['high_trade'] = Decimal(market['high_trade'])
            market['last_trade'] = Decimal(market['last_trade'])
            market['low_trade'] = Decimal(market['low_trade'])
            market['marketid'] = int(market['marketid'])
        return response

    def mytransactions(self):
        response = self.request('mytransactions')
        for transaction in response:
            transaction['amount'] = Decimal(transaction['amount'])
            transaction['fee'] = Decimal(transaction['fee'])
            transaction['time'] = datetime.fromtimestamp(transaction['timestamp'])
        return response

    def markettrades(self, market_id):
        response = self.request('markettrades', params={'marketid': market_id})
        return parse_trade_list(response, market_id=market_id)

    def marketorders(self, market_id):
        response = self.request('marketorders', params={'marketid': market_id})
        response['buyorders'] = parse_order_list(response['buyorders'], type_='buy', market_id=market_id)
        response['sellorders'] = parse_order_list(response['sellorders'], type_='sell', market_id=market_id)
        return response

    def mytrades(self, market_id, limit=None):
        params = {'marketid': market_id}
        if limit:
            params.update(limit=limit)
        response = self.request('mytrades', params=params)
        return parse_trade_list(response, market_id=market_id)

    def allmytrades(self):
        response = self.request('allmytrades')
        return parse_trade_list(response)

    def myorders(self, market_id):
        response = self.request('myorders', params={'marketid': market_id})
        return parse_order_list(response, market_id=market_id)

    def depth(self, market_id):
        response = self.request('depth', params={'marketid': market_id})
        response['sell'] = [[Decimal(order[0]), Decimal(order[1])] for order in response['sell']]
        response['buy'] = [[Decimal(order[0]), Decimal(order[1])] for order in response['buy']]
        return response

    def allmyorders(self):
        response = self.request('allmyorders')
        return parse_order_list(response)

    def createorder(self, market_id, order_type, quantity, price):
        quantity = Decimal(quantity)
        price = Decimal(price)
        response = self.request('createorder', params={
            'marketid': market_id, 'ordertype': order_type, 'quantity': quantity, 'price': price})
        message_without_breaks = re.sub('<br>', ' ', response['moreinfo'])
        message = re.sub('<[^<]+?>', '', message_without_breaks)
        logging.info(message)
        return Order(marketid=market_id,
                     ordertype=order_type,
                     quantity=quantity,
                     price=price,
                     orderid=int(response['orderid']),
                     created=datetime.now(),
                     orig_quantity=quantity,
                     total=quantity*price)

    def cancelorder(self, order_id):
        response = self.request('cancelorder', params={'orderid': order_id})
        logging.info(response)

    def cancelmarketorders(self, market_id):
        response = self.request('cancelmarketorders', params={'marketid': market_id})
        for message in response:
            logging.info(message)

    def cancelallorders(self):
        response = self.request('cancelallorders')
        for message in response:
            logging.info(message)

    def calculatefees(self, order_type, quantity, price):
        response = self.request('calculatefees', params={'ordertype': order_type, 'quantity': quantity, 'price': price})
        response['fee'] = Decimal(response['fee'])
        response['net'] = Decimal(response['net'])
        return response

    def generatenewaddress(self, currency_id=None, currency_code=None):
        if not currency_id and not currency_code:
            raise ValueError("Neither 'currency_id' nor 'currency_code' supplied to 'generatenewaddress'")
        params = {}
        if currency_id:
            params.update(currencyid=currency_id)
        if currency_code:
            params.update(currencycode=currency_code)
        response = self.request('generatenewaddress', params=params)
        return response['address']

    def get_market_ids(self):
        markets = self.getmarkets()
        id_to_pair = {market['marketid']: market['label'] for market in markets}
        pair_to_id = {market['label']: market['marketid'] for market in markets}
        return id_to_pair, pair_to_id
