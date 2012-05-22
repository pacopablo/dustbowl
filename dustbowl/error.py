# -*- coding: utf-8 -*-
#
# Modifcations Copyright (C) 2009 John Hampton <pacopablo@pacopablo.com>
#
# Original code from Trac trunk r8199
# http://svn.edgewall.org/reops/trac/trunk
#
# Moved from core.py
#
# Original Copyright and License:
# Copyright (C) 2003-2009 Edgewall Software
# Copyright (C) 2003-2004 Jonas Borgström <jonas@edgewall.com>
# Copyright (C) 2004-2005 Christopher Lenz <cmlenz@gmx.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.org/wiki/TracLicense.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.
#
# Author: Jonas Borgström <jonas@edgewall.com>
#         Christopher Lenz <cmlenz@gmx.de>

__all__ = [
    'DustbowlError',
    'ConfigurationError',
    'ConsoleObjectError',
]

class DustbowlError(Exception):
    """Exception base class for errors in Gartersnake."""

    title = 'Gartersnake Error'

    def __init__(self, message, title=None, show_traceback=False):
        Exception.__init__(self, message)
        self.message = message
        if title:
            self.title = title
        self.show_traceback = show_traceback

    def __unicode__(self):
        return unicode(self.message)

class ConfigurationError(DustbowlError):
    """Exception raised when a value in the configuration file is not valid."""
    title = 'Configuration Error'


class ConsoleObjectError(Exception):
    """Raised when unable to assign a console object.

    This may be due to the console object already existing, or the namespace
    not being able to support the object.
    """

    def __init__(self, key, is_ns=False, cur_ns=None):
        if not is_ns or (is_ns and not cur_ns):
            self.msg = "The key >>%s<< already exists in the console." % key
        else:
            self.msg = "The namespace %s is not an object that can be " \
                       "assigned methods and other namespaces.  Can not " \
                       "add object: %s" % ('.'.join(cur_ns), key)
        self.key = key
        self.is_ns = is_ns
        self.cur_ns = cur_ns or []

    def __repr__(self):
        return "<ConsoleObjectError(key=%s, is_ns=%s, cur_ns=%s)>" \
               % (str(self.key), str(self.is_ns), str(self.cur_ns))

