python-cryptsy
=========

This library provides Python bindings to [the API offered by cryptsy.com](https://www.cryptsy.com/pages/api).

*Note: use at your own risk. This project is in alpha status and is not affiliated with cryptsy.com.*


Install
---

The only dependency is the very convenient Python library [`requests`](http://docs.python-requests.org/en/latest/). To install:

    pip install requests

    git clone https://github.com/hsharrison/python-cryptsy.git
    cd python-cryptsy
    python setup.py install


Usage
---

Three APIs are offered. For the first two (public and private), functions/methods have the same names and signatures as described in the [cryptsy API specs](https://www.cryptsy.com/pages/api).

---

To access the public API methods:

    import cryptsy.public

The public methods are implemented as module-level functions in `cryptsy.public`. Besides those in the API spec, there is one additional helper function:

    id_to_pair, pair_to_id = cryptsy.public.get_market_ids()

This returns a mapping from pair strings to ids and vice-versa, allowing for easy conversion back and forth.

*Note: As of the time of this writing, cryptsy's public API methods appear to be unreliable. The private methods can duplicate all their functions, so it is recommended to use those instead.*

---

To access the private APIs:

    from cryptsy.private import AuthenticatedSession

    api = AuthenticatedSession('keyfile.txt')

where `keyfile.txt` has two lines: the first line containing your API key and the second your API secret. There is also an implementation of `get_market_ids` as a method of `AuthenticatedSession`.

---

Finally, I have implemented an API that mirrors as closely as possible the API of [bter-api](https://github.com/hsharrison/bter-api) and by extension the original [btce-api](https://github.com/alanmcintyre/btce-api). It is *nearly* a drop-in replacement (but again, use at your own risk):

    import cryptsy.bterapi as bterapi

    api = bterapi.TradeAPI('keyfile.txt')

`bterapi` code is not prefectly compatible. Be aware of the following differences:
* Authenticate `TradeAPI` by passing the name of a key file instead of a `KeyHandler` instance.
* Currency pairs are split by `/` instead of `_`. That is, use `LTC/BTC` instead of `LTC_BTC`.
* `bterapi.all_pairs` is now `api.all_pairs`, where `api` is a `TradeAPI` instance.
* `bterapi.fees` could not be duplicated in the same way as the original, because cryptsy has different fees for buys and sells. Instead use `api.calculatefees(order_type, quantity, price)` to determine fees.
* Not all functions and methods have been duplicated. If one is missing, feel free to contribute!

*Note: I recommend using this module only as a temporary measure. It would be beneficial to port your code to `cryptsy.private` as a long-term solution.*

---

One final usage comment: any keyword arguments passed to any of the public methods, or used in the creation of an `AuthenticatedSession` will be passed onto the corresponding call to `requests`. Use a keyword argument to specify a [timeout duration](http://docs.python-requests.org/en/latest/user/quickstart/#timeouts), for example:

    api = bterapi.TradeAPI('keyfile.txt', timeout=1)


License
---

Copyright (c) 2014 Henry S. Harrison under the MIT license (see `LICENSE.txt`).


Obligatory cryptocurrency addresses
---

If this library earns you money, consider donating to the following addresses:

    BTC: 1MAPTQ1YU839kengQtdLdySrsDPAoT2SEY
    LTC: LcpK52Vt3KgB3EF1hoZDXtvv4KqsS7TPT5

However, contributions in the form of issue reports and pull requests are preferred.
