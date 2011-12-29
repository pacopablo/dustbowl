# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 John Hampton <pacopablo@pacopablo.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: John Hampton <pacopablo@pacopablo.com>

# Standard Library Imports
import logging
import logging.handlers
import sys

# Third Party Imports

# Local Imports


__all__ = [
    'get_logger',
    'BufferHandler',
    'NullLogger',
    'NullHandler',
]

class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def NullLogger():
    logger = logging.getLogger('dustbowl')
    logger.setLevel(logging.CRITICAL)
    logger.addHandler(NullHandler())
    return logger


class BufferHandler(logging.Handler):
    """ Simple Log handler that buffers messages into a list """
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.buffer = []

    def emit(self, record):
        """ Add the message to the buffer """
        try:
            self.buffer.extend(self.format(record).split('\n'))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def get_length(self):
        return len(self.buffer)

    def get_lines(self, start=0, end=-1):
        if end < 0:
            return self.buffer[start:]
        else:
            return self.buffer[start:end]

    def clear_log(self):
        self.buffer = []


def get_logger(logname='dustbowl', level=logging.DEBUG, format=''):
    logger = logging.getLogger(logname)
    logger.setLevel(level)
    hndlr = BufferHandler()
    if format:
        fmt = logging.Formatter(format)
        hndlr.setFormatter(fmt)
    logger.addHandler(hndlr)
    logger._buffer_hndlr = hndlr
    return logger
