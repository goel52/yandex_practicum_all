#!/usr/bin/env python

import sys
import logging

if __name__ == '__main__':
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)

    log.info("Your code: 8b7f48b59a815a15f0658576")
