#!/usr/bin/env python

import sys
import logging

if __name__ == '__main__':
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)

    log.info("Your code: 1f2b4a15b237162c0fa954b3")
