# Copyright (c) 2014 Henry S. Harrison

import sys
import platform

uname = platform.uname()

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
COMMON_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/4.0 (compatible; ' + '; '.join([
        'Cryptsy API Python client',
        ' '.join([uname[0], uname[2], uname[4]]),
        'Python/' + sys.version.split()[0]]) + ')',
}


class CryptsyError(Exception):
    pass
