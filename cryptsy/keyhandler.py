# Copyright (c) 2014 Henry S. Harrison


class KeyHandler(object):
    def __init__(self, filename=None):
        self.filename = filename
        self.keys = {}

        if filename:
            with open(filename, 'rt') as f:
                while True:
                    key = f.readline().strip()
                    if not key:
                        break
                    secret = f.readline().strip()
                    self.keys.update({key: secret})
