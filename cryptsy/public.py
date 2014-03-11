# Copyright (c) 2014 Henry S. Harrison

import requests
from datetime import datetime
from decimal import Decimal

from cryptsy.common import COMMON_HEADERS, CryptsyError, DATETIME_FORMAT
from cryptsy.order import parse_order_list
from cryptsy.trade import parse_trade_list


URL = 'http://pubapi.cryptsy.com/api.php'


def _parse_pair_info(market_id, info):
    if 'recenttrades' in info:
        info['recenttrades'] = parse_trade_list(info['recenttrades'], market_id=market_id)

    if 'lasttradetime' in info:
        info['lasttradetime'] = datetime.strptime(info['lasttradetime'], DATETIME_FORMAT)

    if 'sellorders' in info:
        info['sellorders'] = parse_order_list(info['sellorders'], type_='sell', market_id=market_id)

    if 'lasttradeprice' in info:
        info['lasttradeprice'] = Decimal(info['lasttradeprice'])

    if 'volume' in info:
        info['volume'] = Decimal(info['volume'])

    if 'buyorders' in info:
        info['buyorders'] = parse_order_list(info['buyorders'], type_='buy', market_id=market_id)

    if 'marketid' in info:
        info['marketid'] = int(info['marketid'])
        
    return info


def _public_request(method, params=None, **kwargs):
    if not params:
        params = {}
    params.update(method=method)

    response = requests.get(URL, params=params, headers=COMMON_HEADERS, **kwargs)
    response.raise_for_status()

    parsed_response = response.json()
    if parsed_response['success'] == 0:
        raise CryptsyError(parsed_response['error'])

    return parsed_response['return']


def marketdatav2(**kwargs):
    response = _public_request('marketdatav2', **kwargs)
    #  Response format: {'markets': {pair: info}
    #    info = {'recenttrades': list of trades: keys=(id, price, quantity, time, total),
    #            'lasttradetime': %Y-%m-%d %H:%M:%S,
    #            'secondarycode': second currency code,
    #            'primarycode': fist currency code,
    #            'lastttradeprice': decimal string,
    #            'sellorders': list of orders: keys=(price, quantity, total)
    #            'secondaryname': full name of second currency,
    #            'label': primarycode/secondary code (same as pair key),
    #            'volume': decimal string,
    #            'buyorders': list of orders,
    #            'primaryname': full name of first currency,
    #            'marketid': integer string}
    return {pair: _parse_pair_info(pair, info) for pair, info in response['markets'].items()}


def singlemarketdata(market_id, **kwargs):
    response = _public_request('singlemarketdata', params={'marketid': market_id}, **kwargs)
    data = response['markets'][list(response['markets'].keys())[0]]
    return _parse_pair_info(data['marketid'], data)


def orderdata(**kwargs):
    response = _public_request('orderdata', **kwargs)
    # Response format: {currency: info}
    #      info.keys() = ['secondarycode',
    #                     'primarycode',
    #                     'sellorders',
    #                     'secondaryname',
    #                     'label',
    #                     'buyorders',
    #                     'primaryname',
    #                     'marketid']
    return {info['label']: _parse_pair_info(info['label'], info) for info in response.values()}


def singleorderdata(market_id, **kwargs):
    response = _public_request('orderdata', params={'marketid': market_id}, **kwargs)
    data = response[list(response.keys())[0]]
    return _parse_pair_info(data['marketid'], data)


def get_market_ids(**kwargs):
    response = marketdatav2(**kwargs)
    pair_to_id = {pair: info['marketid'] for pair, info in response.items()}
    id_to_pair = {v: k for k, v in pair_to_id.items()}
    return id_to_pair, pair_to_id
